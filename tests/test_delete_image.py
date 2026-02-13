"""Tests for delete image handler."""
import json
import unittest
from unittest.mock import patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.handlers.delete_handler import handler
from src.common.errors import NotFoundError
from tests.base_test import BaseTestCase


class TestDeleteImage(BaseTestCase):
    """Test cases for delete image handler."""
    
    @patch('src.handlers.base_handler.ImageService')
    def test_delete_image_success(self, mock_service_class):
        """Test deleting an image successfully."""
        mock_service = mock_service_class.return_value
        mock_service.delete_image.return_value = {
            'message': 'Image deleted successfully',
            'image_id': 'img123'
        }
        
        event = self.create_api_event(path_params={'image_id': 'img123'})
        response = handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['message'], 'Image deleted successfully')
        self.assertEqual(body['image_id'], 'img123')
    
    def test_delete_image_missing_id(self):
        """Test deleting without image ID."""
        event = self.create_api_event()
        response = handler(event, self.mock_context)
        self.assertError(response, 400)
    
    @patch('src.handlers.base_handler.ImageService')
    def test_delete_image_not_found(self, mock_service_class):
        """Test deleting non-existent image."""
        mock_service = mock_service_class.return_value
        mock_service.delete_image.side_effect = NotFoundError('Image', 'nonexistent')
        
        event = self.create_api_event(path_params={'image_id': 'nonexistent'})
        response = handler(event, self.mock_context)
        self.assertError(response, 404)


if __name__ == '__main__':
    unittest.main()
