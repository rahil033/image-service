"""Unified Lambda handler for image API routes."""
import json
from decimal import Decimal

from ..services.image_service import ImageService
from ..common.errors import ImageServiceError, ValidationError
from ..common.logger import get_logger
from ..common.utils import (
    get_path_parameter,
    get_query_parameter,
    parse_json_body
)

service = ImageService()
logger = get_logger(__name__)

def lambda_handler(event, context):
    """Route API Gateway requests to image service operations."""
    try:
        method = _get_http_method(event)
        result = _dispatch_request(method, event)
        status_code = 201 if method == "POST" else 200
        return response(status_code, result)

    except ImageServiceError as e:
        logger.error("image_handler request failed", error=e.message)
        return response(e.status_code, {"error": e.message})

    except Exception as e:
        logger.error("image_handler unexpected failure", error=str(e))
        return response(500, {"error": "Internal server error"})


def _get_http_method(event):
    method = (event.get("httpMethod") or "").upper()
    if method not in {"POST", "GET", "DELETE"}:
        raise ValidationError("Unsupported method")
    return method


def _dispatch_request(method, event):
    if method == "POST":
        return _handle_post(event)
    if method == "GET":
        return _handle_get(event)
    return _handle_delete(event)


def _handle_post(event):
    body = parse_json_body(event)
    return service.upload_image(
        user_id=body.get("user_id"),
        filename=body.get("filename"),
        image_data=body.get("image_data"),
        tags=body.get("tags"),
        description=body.get("description"),
        width=body.get("width"),
        height=body.get("height")
    )


def _handle_get(event):
    image_id = _extract_image_id(event)
    if image_id:
        return service.get_image(
            image_id,
            _parse_download_flag(event),
            _parse_expires_in(event)
        )

    return service.list_images(
        user_id=get_query_parameter(event, "user_id"),
        tags=get_query_parameter(event, "tags"),
        limit=_parse_limit(event),
        last_key=get_query_parameter(event, "last_key")
    )


def _handle_delete(event):
    image_id = _extract_image_id(event)
    if not image_id:
        raise ValidationError("image_id is required")
    return service.delete_image(image_id)


def _extract_image_id(event):
    return get_path_parameter(event, "image_id") or get_query_parameter(event, "image_id")


def _parse_download_flag(event):
    return get_query_parameter(event, "download", "false").lower() == "true"


def _parse_expires_in(event):
    expires_in_str = get_query_parameter(event, "expires_in")
    if not expires_in_str:
        return None

    try:
        expires_in = int(expires_in_str)
    except (TypeError, ValueError):
        raise ValidationError("expires_in must be a valid integer")

    if expires_in < 1 or expires_in > 604800:
        raise ValidationError("expires_in must be between 1 and 604800 seconds")
    return expires_in


def _parse_limit(event):
    limit_str = get_query_parameter(event, "limit", "50")
    try:
        limit = int(limit_str)
    except (TypeError, ValueError):
        raise ValidationError("limit must be a valid integer")

    if limit < 1 or limit > 100:
        raise ValidationError("limit must be between 1 and 100")
    return limit


def decimal_default(obj):
    """Serialize Decimal values as float for JSON responses."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def response(status, body):
    """Build API Gateway response."""
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body, default=decimal_default)
    }
