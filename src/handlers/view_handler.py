"""
Lambda handler for viewing/downloading images.
"""
from ..common.utils import get_path_parameter, get_query_parameter
from ..common.errors import ValidationError
from .base_handler import lambda_handler


@lambda_handler("view")
def handler(event, service):
    """Handle image view/download requests."""
    image_id = get_path_parameter(event, 'image_id')
    if not image_id:
        raise ValidationError('image_id is required')
    
    download = get_query_parameter(event, 'download', 'false').lower() == 'true'
    expires_in_str = get_query_parameter(event, 'expires_in')
    expires_in = int(expires_in_str) if expires_in_str else None
    
    result = service.get_image(image_id, download, expires_in)
    return 200, result
