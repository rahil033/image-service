"""
DynamoDB metadata repository.
"""
import boto3
from boto3.dynamodb.conditions import Attr
from ..models.image_model import ImageMetadata
from ..common.logger import get_logger
from ..common.errors import DatabaseError, NotFoundError
from ..common.config import Config, get_aws_endpoint

logger = get_logger(__name__)


class MetadataRepository:
    """Repository for DynamoDB operations."""
    
    def __init__(self, dynamodb_resource=None):
        """Initialize with DynamoDB connection."""
        if dynamodb_resource:
            self.dynamodb = dynamodb_resource
        else:
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=get_aws_endpoint('dynamodb'),
                region_name=Config.get_region(),
                aws_access_key_id='test' if get_aws_endpoint('dynamodb') else None,
                aws_secret_access_key='test' if get_aws_endpoint('dynamodb') else None
            )
        self.table_name = Config.get_table_name()
        self.table = self.dynamodb.Table(self.table_name)
    
    def save_metadata(self, metadata):
        """Save image metadata to DynamoDB."""
        try:
            self.table.put_item(Item=metadata.to_dynamodb_item())
            logger.info("Metadata saved", image_id=metadata.image_id)
        except Exception as e:
            logger.error("Failed to save metadata", image_id=metadata.image_id, error=str(e))
            raise DatabaseError(f"Failed to save metadata: {str(e)}", operation='save')
    
    def get_metadata(self, image_id):
        """Get image metadata from DynamoDB."""
        try:
            response = self.table.get_item(Key={'image_id': image_id})
            
            if 'Item' not in response:
                raise NotFoundError('Image', image_id)
            
            logger.info("Retrieved metadata", image_id=image_id)
            return ImageMetadata.from_dynamodb_item(response['Item'])
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("Failed to get metadata", image_id=image_id, error=str(e))
            raise DatabaseError(f"Failed to retrieve metadata: {str(e)}", operation='get')
    
    def delete_metadata(self, image_id):
        """Delete image metadata from DynamoDB."""
        try:
            self.table.delete_item(Key={'image_id': image_id})
            logger.info("Metadata deleted", image_id=image_id)
        except Exception as e:
            logger.error("Failed to delete metadata", image_id=image_id, error=str(e))
            raise DatabaseError(f"Failed to delete metadata: {str(e)}", operation='delete')
    
    def list_metadata(self, user_id=None, tags=None, limit=50, last_evaluated_key=None):
        """List image metadata with optional filters."""
        try:
            scan_kwargs = {'Limit': limit}
            
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            
            # Build filter expressions
            filter_expressions = []
            
            if user_id:
                filter_expressions.append(Attr('user_id').eq(user_id))
            
            if tags:
                tag_filters = [Attr('tags').contains(tag) for tag in tags]
                if len(tag_filters) == 1:
                    filter_expressions.append(tag_filters[0])
                else:
                    # Combine with OR logic
                    combined_tag_filter = tag_filters[0]
                    for tag_filter in tag_filters[1:]:
                        combined_tag_filter = combined_tag_filter | tag_filter
                    filter_expressions.append(combined_tag_filter)
            
            # Combine all filters with AND logic
            if filter_expressions:
                combined_filter = filter_expressions[0]
                for filter_expr in filter_expressions[1:]:
                    combined_filter = combined_filter & filter_expr
                scan_kwargs['FilterExpression'] = combined_filter
            
            # Execute scan
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            next_key = response.get('LastEvaluatedKey')
            
            # Convert to ImageMetadata objects
            metadata_list = [ImageMetadata.from_dynamodb_item(item) for item in items]
            
            logger.info(
                "Listed metadata",
                count=len(metadata_list),
                user_id=user_id,
                has_more=next_key is not None
            )
            
            return metadata_list, next_key
            
        except Exception as e:
            logger.error("Failed to list metadata", error=str(e))
            raise DatabaseError(f"Failed to list metadata: {str(e)}", operation='list')
