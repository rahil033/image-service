"""
API response models.
"""
import json


class APIResponse:
    """Standard API response for Lambda."""
    
    def __init__(self, status_code, body, headers=None):
        self.status_code = status_code
        self.body = body
        self.headers = headers
    
    def to_lambda_response(self):
        """Convert to Lambda response format."""
        return {
            'statusCode': self.status_code,
            'body': json.dumps(self.body),
            'headers': self.headers or {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            }
        }
