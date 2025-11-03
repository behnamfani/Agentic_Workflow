import logging
import sys
from src.config import logger

# Global variable to hold the user's logger
_user_logger = None

def set_logger(user_logger):
    """
    Set a custom logger to be used throughout the application.
    
    Args:
        user_logger: A logging.Logger instance to use instead of the default logger
    """
    global _user_logger
    _user_logger = user_logger

def get_logger():
    """
    Get the current logger (user's custom logger or default logger).
    
    Returns:
        logging.Logger: The active logger instance
    """
    global _user_logger
    if _user_logger is not None:
        return _user_logger
    return logger
