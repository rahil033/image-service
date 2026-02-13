"""
Logging with JSON output for AWS Lambda.
"""
import logging
import json


class StructuredLogger:
    """Logger that outputs JSON-formatted logs."""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Set up console output
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
    
    def info(self, message, **kwargs):
        """Log info message with optional extra fields."""
        log_data = {'level': 'INFO', 'message': message, **kwargs}
        self.logger.info(json.dumps(log_data))
    
    def error(self, message, **kwargs):
        """Log error message with optional extra fields."""
        log_data = {'level': 'ERROR', 'message': message, **kwargs}
        self.logger.error(json.dumps(log_data))


def get_logger(name):
    """Get a logger instance."""
    return StructuredLogger(name)
