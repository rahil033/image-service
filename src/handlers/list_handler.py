"""
Lambda handler for listing images.
"""
from ..common.utils import get_query_parameter
from .base_handler import lambda_handler


@lambda_handler("list")
def handler(event, service):
    """Handle image listing requests."""
    user_id = get_query_parameter(event, 'user_id')
    tags = get_query_parameter(event, 'tags')
    limit = int(get_query_parameter(event, 'limit', '50'))
    last_key = get_query_parameter(event, 'last_key')
    
    result = service.list_images(user_id, tags, limit, last_key)
    return 200, result
