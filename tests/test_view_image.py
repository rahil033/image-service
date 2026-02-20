"""Tests for view image handler."""
import json
import unittest
from unittest.mock import patch

from src.handlers.image_handler import lambda_handler
from src.common.errors import NotFoundError
from tests.base_test import BaseTestCase


class TestViewImage(BaseTestCase):
    """Test cases for view image handler."""
    
    @patch('src.handlers.image_handler.service')
    def test_view_image_success(self, mock_service):
        """Test viewing an image successfully."""
        mock_service.get_image.return_value = {
            'image_id': 'img123',
            'filename': 'test.jpg',
            'image_url': 'https://s3.amazonaws.com/bucket/image.jpg',
            'metadata': {'user_id': 'user123'}
        }
        
        event = self.create_api_event(path_params={'image_id': 'img123'})
        response = lambda_handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['image_id'], 'img123')
        self.assertIn('image_url', body)
    
    @patch('src.handlers.image_handler.service')
    def test_get_without_image_id_routes_to_list(self, mock_service):
        """Test GET without image ID routes to list images."""
        mock_service.list_images.return_value = {'images': [], 'count': 0}

        event = self.create_api_event()
        response = lambda_handler(event, self.mock_context)

        body = self.assertSuccess(response, 200)
        self.assertEqual(body['count'], 0)
        mock_service.list_images.assert_called_once()
    
    @patch('src.handlers.image_handler.service')
    def test_view_image_not_found(self, mock_service):
        """Test viewing non-existent image."""
        mock_service.get_image.side_effect = NotFoundError('Image', 'nonexistent')
        
        event = self.create_api_event(path_params={'image_id': 'nonexistent'})
        response = lambda_handler(event, self.mock_context)
        self.assertError(response, 404)

    def test_view_image_invalid_expires_in_non_integer(self):
        """Test viewing image with invalid expires_in value."""
        event = self.create_api_event(
            path_params={'image_id': 'img123'},
            query_params={'expires_in': 'abc'}
        )
        response = lambda_handler(event, self.mock_context)
        self.assertError(response, 400)

    def test_view_image_invalid_expires_in_out_of_range(self):
        """Test viewing image with out-of-range expires_in value."""
        event = self.create_api_event(
            path_params={'image_id': 'img123'},
            query_params={'expires_in': '0'}
        )
        response = lambda_handler(event, self.mock_context)
        self.assertError(response, 400)


if __name__ == '__main__':
    unittest.main()