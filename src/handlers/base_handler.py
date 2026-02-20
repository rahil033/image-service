"""
Base handler with common error handling for Lambda functions.
"""
from functools import wraps
from ..models.response_model import APIResponse
from ..common.logger import get_logger
from ..common.errors import ImageServiceError
from ..services.image_service import ImageService

logger = get_logger(__name__)


def lambda_handler(handler_name):
    """
    Decorator that adds error handling and logging to Lambda handlers.
    
    Usage:
        @lambda_handler("upload")
        def handler(event, context, service):
            result = service.upload_image(...)
            return 201, result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                request_id = getattr(context, 'aws_request_id', 'None')
                logger.info(f"{handler_name} handler started", request_id=request_id)

                # Create service instance
                service = ImageService()
                
                # Call handler, get status code and body
                status_code, body = func(event, service)
                
                return APIResponse(status_code, body).to_lambda_response()
                
            except ImageServiceError as e:
                logger.error(f"{handler_name} failed", error=e.message)
                return APIResponse(
                    e.status_code,
                    {'error': e.message}
                ).to_lambda_response()
                
            except Exception as e:
                logger.error(f"Unexpected error in {handler_name}", error=str(e))
                return APIResponse(
                    500,
                    {'error': 'Internal server error'}
                ).to_lambda_response()
        
        return wrapper
    return decorator
