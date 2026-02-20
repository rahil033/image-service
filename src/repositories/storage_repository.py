"""
S3 storage repository.
"""
import boto3
from botocore.exceptions import ClientError
from ..common.logger import get_logger
from ..common.errors import StorageError
from ..common.config import Config, get_aws_endpoint

logger = get_logger(__name__)


class StorageRepository:
    """Repository for S3 operations."""
    
    def __init__(self, s3_client=None):
        """Initialize with S3 connection."""
        if s3_client:
            self.s3_client = s3_client
        else:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=get_aws_endpoint('s3'),
                region_name=Config.get_region(),
                aws_access_key_id='test' if get_aws_endpoint('s3') else None,
                aws_secret_access_key='test' if get_aws_endpoint('s3') else None
            )
        self.bucket_name = Config.get_bucket_name()
    
    def upload_image(self, s3_key, image_bytes, content_type, metadata):
        """Upload image to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_bytes,
                ContentType=content_type,
                Metadata=metadata
            )
            logger.info("Image uploaded to S3", s3_key=s3_key, size=len(image_bytes))
        except Exception as e:
            logger.error("Failed to upload image", s3_key=s3_key, error=str(e))
            raise StorageError(f"Failed to upload image: {str(e)}", operation='upload')
    
    def delete_image(self, s3_key):
        """Delete image from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info("Image deleted from S3", s3_key=s3_key)
        except Exception as e:
            logger.error("Failed to delete image", s3_key=s3_key, error=str(e))
            raise StorageError(f"Failed to delete image: {str(e)}", operation='delete')
    
    def check_image_exists(self, s3_key):
        """Check if image exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            if error_code in ('404', 'NoSuchKey', 'NotFound'):
                return False
            logger.error("Error checking image existence", s3_key=s3_key, error=str(e))
            raise StorageError(f"Failed to check image existence: {str(e)}", operation='check')
        except Exception as e:
            logger.error("Error checking image existence", s3_key=s3_key, error=str(e))
            raise StorageError(f"Failed to check image existence: {str(e)}", operation='check')
    
    def generate_presigned_url(self, s3_key, expires_in=3600, download=False, filename=None):
        """Generate presigned URL for image access."""
        try:
            params = {'Bucket': self.bucket_name, 'Key': s3_key}
            
            if download and filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )
            logger.info("Generated presigned URL", s3_key=s3_key, expires_in=expires_in)
            return url
        except Exception as e:
            logger.error("Failed to generate presigned URL", s3_key=s3_key, error=str(e))
            raise StorageError(f"Failed to generate presigned URL: {str(e)}", operation='presign')
