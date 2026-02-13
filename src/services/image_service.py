"""
Image service - business logic layer.
"""
import json
from ..models.image_model import ImageMetadata
from ..repositories.storage_repository import StorageRepository
from ..repositories.metadata_repository import MetadataRepository
from ..common.logger import get_logger
from ..common.utils import (
    generate_image_id,
    get_current_timestamp,
    get_s3_key,
    parse_base64_image,
    get_content_type_from_filename,
    validate_image_size,
    validate_required_fields
)
from ..common.config import Config
from ..common.errors import StorageError, DatabaseError, NotFoundError

logger = get_logger(__name__)


class ImageService:
    """Service layer for image operations."""
    
    def __init__(self, storage_repo=None, metadata_repo=None):
        """Initialize image service with repositories."""
        self.storage_repo = storage_repo or StorageRepository()
        self.metadata_repo = metadata_repo or MetadataRepository()
    
    def upload_image(self, user_id, filename, image_data, tags=None, description=None, width=None, height=None):
        """Upload an image with metadata."""
        logger.info("Starting image upload", user_id=user_id, filename=filename)
        
        # Validate required fields
        validate_required_fields(
            {'user_id': user_id, 'filename': filename, 'image_data': image_data},
            ['user_id', 'filename', 'image_data']
        )
        
        # Prepare image data
        image_id = generate_image_id()
        image_bytes = parse_base64_image(image_data)
        validate_image_size(image_bytes, Config.get_max_image_size())
        content_type = get_content_type_from_filename(filename)
        s3_key = get_s3_key(user_id, image_id, filename)
        
        # Upload to S3
        self.storage_repo.upload_image(
            s3_key, image_bytes, content_type,
            {'user_id': user_id, 'image_id': image_id, 'original_filename': filename}
        )
        
        # Create metadata
        metadata = ImageMetadata(
            image_id=image_id,
            user_id=user_id,
            filename=filename,
            s3_key=s3_key,
            content_type=content_type,
            size=len(image_bytes),
            upload_date=get_current_timestamp(),
            tags=tags if tags else None,
            description=description if description else None,
            width=width,
            height=height
        )
        
        # Save metadata (with automatic rollback on failure)
        try:
            self.metadata_repo.save_metadata(metadata)
        except DatabaseError:
            logger.error("Metadata save failed, rolling back", image_id=image_id)
            try:
                self.storage_repo.delete_image(s3_key)
            except StorageError:
                logger.error("Rollback failed", image_id=image_id)
            raise
        
        # Generate presigned URL
        image_url = self.storage_repo.generate_presigned_url(
            s3_key, Config.get_presigned_url_expiration()
        )
        
        logger.info("Image upload completed", image_id=image_id)
        
        return {
            'message': 'Image uploaded successfully',
            'image_id': image_id,
            'image_url': image_url,
            'metadata': metadata.to_dict()
        }
    
    def list_images(self, user_id=None, tags=None, limit=50, last_key=None):
        """List images with optional filters."""
        logger.info("Listing images", user_id=user_id, tags=tags, limit=limit)
        
        # Parse tags
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Parse pagination key
        last_evaluated_key = json.loads(last_key) if last_key else None
        
        # Get metadata from DynamoDB
        metadata_list, next_key = self.metadata_repo.list_metadata(
            user_id, tags_list, limit, last_evaluated_key
        )
        
        # Add presigned URLs to each image
        images = []
        for metadata in metadata_list:
            image_dict = metadata.to_dict()
            image_dict['image_url'] = self.storage_repo.generate_presigned_url(
                metadata.s3_key, Config.get_presigned_url_expiration()
            )
            images.append(image_dict)
        
        result = {'images': images, 'count': len(images)}
        if next_key:
            result['last_evaluated_key'] = json.dumps(next_key)
        
        logger.info("Images listed", count=len(images))
        return result
    
    def get_image(self, image_id, download=False, expires_in=None):
        """Get image metadata and download URL."""
        logger.info("Getting image", image_id=image_id)
        
        # Get metadata from DynamoDB
        metadata = self.metadata_repo.get_metadata(image_id)
        
        # Verify image exists in S3
        if not self.storage_repo.check_image_exists(metadata.s3_key):
            logger.error("Image file not found in S3", image_id=image_id)
            raise NotFoundError('Image file in storage', image_id)
        
        # Generate presigned URL
        expiration = expires_in or Config.get_presigned_url_expiration()
        download_url = self.storage_repo.generate_presigned_url(
            metadata.s3_key, expiration, download,
            metadata.filename if download else None
        )
        
        logger.info("Image retrieved", image_id=image_id)
        
        return {
            'image_id': image_id,
            'metadata': metadata.to_dict(),
            'download_url': download_url,
            'expires_in': expiration
        }
    
    def delete_image(self, image_id):
        """Delete an image and its metadata."""
        logger.info("Deleting image", image_id=image_id)
        
        # Get metadata (to get S3 key)
        metadata = self.metadata_repo.get_metadata(image_id)
        
        # Delete from S3 and DynamoDB
        self.storage_repo.delete_image(metadata.s3_key)
        self.metadata_repo.delete_metadata(image_id)
        
        logger.info("Image deleted", image_id=image_id)
        
        return {'message': 'Image deleted successfully', 'image_id': image_id}
