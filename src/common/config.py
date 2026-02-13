"""
Configuration management.
"""
import os


class Config:
    """Configuration class for environment variables."""
    
    # Default values
    BUCKET_NAME = 'image-service-bucket'
    TABLE_NAME = 'image-metadata'
    REGION = 'us-east-1'
    PRESIGNED_URL_EXPIRATION = 3600  # seconds
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    @staticmethod
    def get_bucket_name():
        """Get S3 bucket name."""
        return os.environ.get('BUCKET_NAME', Config.BUCKET_NAME)
    
    @staticmethod
    def get_table_name():
        """Get DynamoDB table name."""
        return os.environ.get('TABLE_NAME', Config.TABLE_NAME)
    
    @staticmethod
    def get_region():
        """Get AWS region."""
        return os.environ.get('AWS_DEFAULT_REGION', Config.REGION)
    
    @staticmethod
    def get_presigned_url_expiration():
        """Get presigned URL expiration time in seconds."""
        value = os.environ.get('PRESIGNED_URL_EXPIRATION', str(Config.PRESIGNED_URL_EXPIRATION))
        return int(value)
    
    @staticmethod
    def get_max_image_size():
        """Get maximum image size in bytes."""
        value = os.environ.get('MAX_IMAGE_SIZE', str(Config.MAX_IMAGE_SIZE))
        return int(value)

def get_aws_endpoint(service):
    """Return LocalStack endpoint if USE_LOCALSTACK is set, else None."""
    if os.environ.get("USE_LOCALSTACK") == "1":
        return "http://localhost:4566"
    return None
