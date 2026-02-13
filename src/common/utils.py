"""
Utility functions for common operations.
"""
import uuid
import json
import base64
from datetime import datetime
from .errors import ValidationError


# Supported image formats
CONTENT_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp'
}


def generate_image_id():
    """Generate a unique image ID."""
    return str(uuid.uuid4())


def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def parse_json_body(event):
    """Parse JSON body from API Gateway event."""
    try:
        body = event.get('body', '{}')
        if event.get('isBase64Encoded', False):
            body = base64.b64decode(body).decode('utf-8')
        return json.loads(body) if isinstance(body, str) else body
    except (json.JSONDecodeError, ValueError):
        raise ValidationError("Invalid JSON in request body")


def get_path_parameter(event, param_name):
    """Get path parameter from API Gateway event."""
    path_params = event.get('pathParameters') or {}
    return path_params.get(param_name)


def get_query_parameter(event, param_name, default=None):
    """Get query string parameter from API Gateway event."""
    query_params = event.get('queryStringParameters') or {}
    return query_params.get(param_name, default)


def validate_required_fields(data, required_fields):
    """Check that all required fields are present."""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")


def get_s3_key(user_id, image_id, filename):
    """Generate S3 storage path for an image."""
    extension = filename.split('.')[-1] if '.' in filename else 'jpg'
    return f"images/{user_id}/{image_id}.{extension}"


def parse_base64_image(base64_string):
    """Convert base64 string to bytes."""
    try:
        # Remove data URL prefix if present (e.g., data:image/png;base64,...)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        return base64.b64decode(base64_string)
    except Exception:
        raise ValidationError("Invalid base64 image data")


def get_content_type_from_filename(filename):
    """Get MIME type from filename extension."""
    if '.' not in filename:
        return 'image/jpeg'
    extension = filename.lower().rsplit('.', 1)[-1]
    return CONTENT_TYPES.get(extension, 'image/jpeg')


def validate_image_size(image_bytes, max_size):
    """Check if image size is within limits."""
    actual_size = len(image_bytes)
    if actual_size > max_size:
        raise ValidationError(
            f"Image size ({actual_size:,} bytes) exceeds maximum ({max_size:,} bytes)"
        )
