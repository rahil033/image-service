"""
Custom exception classes for the image service.
"""


class ImageServiceError(Exception):
    """Base exception for all image service errors."""
    
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(ImageServiceError):
    """Raised when an image is not found."""
    
    def __init__(self, resource, resource_id):
        message = f"{resource} not found: {resource_id}"
        super().__init__(message, status_code=404)


class StorageError(ImageServiceError):
    """Raised when S3 operations fail."""
    
    def __init__(self, message, operation=None):
        self.operation = operation
        super().__init__(f"Storage error: {message}", status_code=500)


class DatabaseError(ImageServiceError):
    """Raised when DynamoDB operations fail."""
    
    def __init__(self, message, operation=None):
        self.operation = operation
        super().__init__(f"Database error: {message}", status_code=500)


class ValidationError(ImageServiceError):
    """Raised when input validation fails."""
    
    def __init__(self, message):
        super().__init__(message, status_code=400)
