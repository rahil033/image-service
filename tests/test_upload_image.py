"""Tests for upload image handler."""
import json
import unittest
from unittest.mock import patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.handlers.upload_handler import handler
from src.common.errors import StorageError
from tests.base_test import BaseTestCase


class TestUploadImage(BaseTestCase):
    """Test cases for upload image handler."""
    
    @patch('src.handlers.base_handler.ImageService')
    def test_upload_image_success(self, mock_service_class):
        """Test successful image upload."""
        # Mock service response
        mock_service = mock_service_class.return_value
        mock_service.upload_image.return_value = {
            'message': 'Image uploaded successfully',
            'image_id': 'test-image-123',
            'image_url': 'https://test-bucket.s3.amazonaws.com/test-key',
            'metadata': {'image_id': 'test-image-123', 'user_id': 'user123', 'filename': 'test_image.png'}
        }
        
        event = self.create_api_event(body={
            'user_id': 'user123',
            'filename': 'test_image.png',
            'image_data': self.valid_image_data,
            'tags': 'nature,landscape',
            'description': 'A beautiful landscape',
            'width': 1920,
            'height': 1080
        })
        
        response = handler(event, self.mock_context)
        body = self.assertSuccess(response, 201)
        
        self.assertEqual(body['message'], 'Image uploaded successfully')
        self.assertEqual(body['image_id'], 'test-image-123')
        self.assertIn('image_url', body)
        mock_service.upload_image.assert_called_once()
    
    def test_upload_image_missing_required_fields(self):
        """Test upload with missing required fields."""
        event = self.create_api_event(body={'user_id': 'user123'})
        response = handler(event, self.mock_context)
        self.assertError(response, 400)
    
    def test_upload_image_invalid_json(self):
        """Test upload with invalid JSON."""
        event = {'body': 'invalid json{', 'headers': {'Content-Type': 'application/json'}}
        response = handler(event, self.mock_context)
        self.assertError(response, 400)
    
    def test_upload_image_invalid_base64(self):
        """Test upload with invalid base64 data."""
        event = self.create_api_event(body={
            'user_id': 'user123',
            'filename': 'test.png',
            'image_data': 'not-valid-base64!!!'
        })
        response = handler(event, self.mock_context)
        self.assertError(response, 400)
    
    @patch('src.handlers.base_handler.ImageService')
    def test_upload_image_storage_error(self, mock_service_class):
        """Test upload with storage error."""
        mock_service = mock_service_class.return_value
        mock_service.upload_image.side_effect = StorageError('S3 upload failed')
        
        event = self.create_api_event(body={
            'user_id': 'user123',
            'filename': 'test_image.png',
            'image_data': self.valid_image_data
        })
        
        response = handler(event, self.mock_context)
        self.assertError(response, 500)


if __name__ == '__main__':
    unittest.main()
