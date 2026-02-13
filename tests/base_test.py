"""
Base test class with common setup and utilities.
"""
import os
import json
import base64
import unittest
from unittest.mock import Mock
from typing import Dict, Any


class BaseTestCase(unittest.TestCase):
    """Base test class with common setup for all tests."""
    
    def setUp(self):
        """Set up common test fixtures."""
        # Set environment variables
        os.environ['BUCKET_NAME'] = 'test-bucket'
        os.environ['TABLE_NAME'] = 'test-table'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Create mock context
        self.mock_context = self._create_mock_context()
        
        # Create valid base64 encoded image data
        self.valid_image_data = self._create_test_image()
    
    def _create_mock_context(self):
        """Create mock Lambda context."""
        context = Mock()
        context.function_name = 'test_function'
        context.aws_request_id = 'test-request-123'
        context.memory_limit_in_mb = 128
        context.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test_function'
        return context
    
    def _create_test_image(self):
        """Create test base64 image."""
        image_bytes = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00')
        return image_bytes.decode('utf-8')
    
    def create_api_event(self, body=None, path_params=None, query_params=None):
        """Create mock API Gateway event."""
        event = {
            'headers': {'Content-Type': 'application/json'},
            'requestContext': {'requestId': 'test-request-123'}
        }
        
        if body is not None:
            event['body'] = json.dumps(body)
        
        if path_params:
            event['pathParameters'] = path_params
        
        if query_params:
            event['queryStringParameters'] = query_params
        
        return event
    
    def parse_response(self, response):
        """Parse Lambda response."""
        status_code = response['statusCode']
        body = json.loads(response['body'])
        return status_code, body
    
    def assertSuccess(self, response, expected_status=200):
        """Assert successful response."""
        status_code, body = self.parse_response(response)
        self.assertEqual(status_code, expected_status)
        return body
    
    def assertError(self, response, expected_status=400):
        """Assert error response."""
        status_code, body = self.parse_response(response)
        self.assertEqual(status_code, expected_status)
        self.assertIn('error', body)
        return body
