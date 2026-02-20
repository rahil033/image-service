"""
Lambda handler for listing images.
"""
from ..common.utils import get_query_parameter
from ..common.errors import ValidationError
from .base_handler import lambda_handler


@lambda_handler("list")
def handler(event, service):
    """Handle image listing requests."""
    user_id = get_query_parameter(event, 'user_id')
    tags = get_query_parameter(event, 'tags')
    limit_str = get_query_parameter(event, 'limit', '50')
    try:
        limit = int(limit_str)
    except (TypeError, ValueError):
        raise ValidationError('limit must be a valid integer')

    if limit < 1 or limit > 100:
        raise ValidationError('limit must be between 1 and 100')

    last_key = get_query_parameter(event, 'last_key')
    
    result = service.list_images(user_id, tags, limit, last_key)
    return 200, result
