"""
Lambda handler for deleting images.
"""
from ..common.utils import get_path_parameter
from ..common.errors import ValidationError
from .base_handler import lambda_handler


@lambda_handler("delete")
def handler(event, service):
    """Handle image deletion requests."""
    image_id = get_path_parameter(event, 'image_id')
    if not image_id:
        raise ValidationError('image_id is required')
    
    result = service.delete_image(image_id)
    return 200, result
