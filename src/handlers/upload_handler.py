"""
Lambda handler for uploading images.
"""
from ..common.utils import parse_json_body
from .base_handler import lambda_handler


@lambda_handler("upload")
def handler(event, service):
    """Handle image upload requests."""
    body = parse_json_body(event)
    
    result = service.upload_image(
        user_id=body.get('user_id'),
        filename=body.get('filename'),
        image_data=body.get('image_data'),
        tags=body.get('tags'),
        description=body.get('description'),
        width=body.get('width'),
        height=body.get('height')
    )
    
    return 201, result
