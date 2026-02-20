"""Tests for list images handler."""
import json
import unittest
from unittest.mock import patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.handlers.list_handler import handler
from tests.base_test import BaseTestCase


class TestListImages(BaseTestCase):
    """Test cases for list images handler."""
    
    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.sample_images = [
            {'image_id': 'img1', 'user_id': 'user123', 'filename': 'image1.png', 'tags': 'nature,landscape'},
            {'image_id': 'img2', 'user_id': 'user123', 'filename': 'image2.jpg', 'tags': 'portrait'}
        ]
    
    @patch('src.handlers.base_handler.ImageService')
    def test_list_all_images(self, mock_service_class):
        """Test listing all images without filters."""
        mock_service = mock_service_class.return_value
        mock_service.list_images.return_value = {'images': self.sample_images, 'count': 2}
        
        event = self.create_api_event()
        response = handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['count'], 2)
        self.assertEqual(len(body['images']), 2)
    
    @patch('src.handlers.base_handler.ImageService')
    def test_list_images_filter_by_user(self, mock_service_class):
        """Test filtering images by user_id."""
        mock_service = mock_service_class.return_value
        mock_service.list_images.return_value = {'images': self.sample_images, 'count': 2}
        
        event = self.create_api_event(query_params={'user_id': 'user123'})
        response = handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['count'], 2)
        mock_service.list_images.assert_called_once()
    
    @patch('src.handlers.base_handler.ImageService')
    def test_list_images_filter_by_tags(self, mock_service_class):
        """Test filtering images by tags."""
        mock_service = mock_service_class.return_value
        mock_service.list_images.return_value = {'images': [{'image_id': 'img1', 'tags': 'nature'}], 'count': 1}
        
        event = self.create_api_event(query_params={'tags': 'nature'})
        response = handler(event, self.mock_context)
        
        body = self.assertSuccess(response)
        self.assertEqual(body['count'], 1)

    def test_list_images_invalid_limit_non_integer(self):
        """Test listing images with non-integer limit."""
        event = self.create_api_event(query_params={'limit': 'abc'})
        response = handler(event, self.mock_context)
        self.assertError(response, 400)

    def test_list_images_invalid_limit_out_of_range(self):
        """Test listing images with out-of-range limit."""
        event = self.create_api_event(query_params={'limit': '0'})
        response = handler(event, self.mock_context)
        self.assertError(response, 400)


if __name__ == '__main__':
    unittest.main()
