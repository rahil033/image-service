"""Tests for view image handler."""
import json
import unittest
from unittest.mock import patch

from src.handlers.view_handler import handler
from src.common.errors import NotFoundError
from tests.base_test import BaseTestCase


class TestViewImage(BaseTestCase):
    """Test cases for view image handler."""
    
    @patch('src.handlers.base_handler.ImageService')
    def test_view_image_success(self, mock_service_class):
        """Test viewing an image successfully."""
        mock_service = mock_service_class.return_value
        mock_service.get_image.return_value = {
            'image_id': 'img123',
            'filename': 'test.jpg',
            'image_url': 'https://s3.amazonaws.com/bucket/image.jpg',
            'metadata': {'user_id': 'user123'}
        }
        
        event = self.create_api_event(path_params={'image_id': 'img123'})
        response = handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['image_id'], 'img123')
        self.assertIn('image_url', body)
    
    def test_view_image_missing_id(self):
        """Test viewing without image ID."""
        event = self.create_api_event()
        response = handler(event, self.mock_context)
        self.assertError(response, 400)
    
    @patch('src.handlers.base_handler.ImageService')
    def test_view_image_not_found(self, mock_service_class):
        """Test viewing non-existent image."""
        mock_service = mock_service_class.return_value
        mock_service.get_image.side_effect = NotFoundError('Image', 'nonexistent')
        
        event = self.create_api_event(path_params={'image_id': 'nonexistent'})
        response = handler(event, self.mock_context)
        self.assertError(response, 404)

    def test_view_image_invalid_expires_in_non_integer(self):
        """Test viewing image with invalid expires_in value."""
        event = self.create_api_event(
            path_params={'image_id': 'img123'},
            query_params={'expires_in': 'abc'}
        )
        response = handler(event, self.mock_context)
        self.assertError(response, 400)

    def test_view_image_invalid_expires_in_out_of_range(self):
        """Test viewing image with out-of-range expires_in value."""
        event = self.create_api_event(
            path_params={'image_id': 'img123'},
            query_params={'expires_in': '0'}
        )
        response = handler(event, self.mock_context)
        self.assertError(response, 400)


if __name__ == '__main__':
    unittest.main()
