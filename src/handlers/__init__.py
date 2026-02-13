"""Lambda function handlers."""

from .upload_handler import handler as upload_handler
from .list_handler import handler as list_handler
from .view_handler import handler as view_handler
from .delete_handler import handler as delete_handler

__all__ = ['upload_handler', 'list_handler', 'view_handler', 'delete_handler']
