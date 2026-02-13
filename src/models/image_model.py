"""
Image metadata model.
"""


class ImageMetadata:
    """Image metadata model."""
    
    def __init__(self, image_id, user_id, filename, s3_key, content_type, size, upload_date,
                 tags=None, description=None, width=None, height=None):
        self.image_id = image_id
        self.user_id = user_id
        self.filename = filename
        self.s3_key = s3_key
        self.content_type = content_type
        self.size = size
        self.upload_date = upload_date
        self.tags = tags
        self.description = description
        self.width = width
        self.height = height
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'image_id': self.image_id,
            'user_id': self.user_id,
            'filename': self.filename,
            's3_key': self.s3_key,
            'content_type': self.content_type,
            'size': self.size,
            'upload_date': self.upload_date,
            'tags': self.tags,
            'description': self.description,
            'width': self.width,
            'height': self.height
        }
    
    def to_dynamodb_item(self):
        """Convert to DynamoDB item (removes None values)."""
        return {k: v for k, v in self.to_dict().items() if v is not None}
    
    @classmethod
    def from_dynamodb_item(cls, item):
        """Create from DynamoDB item."""
        return cls(**item)
