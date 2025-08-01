"""
Logging Utility Module

Provides a standardized logging interface for the application.
"""

import logging
import os
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Creates and returns a configured logger instance.
    
    Args:
        name (str): Name of the logger (typically __name__ from the calling module)
        level (int, optional): Logging level. Defaults to INFO or LOG_LEVEL env var.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # If logger already has handlers, return it as is
    if logger.handlers:
        return logger
    
    # Set level from parameter, environment variable, or default to INFO
    if level is None:
        level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Example usage:
# logger = get_logger(__name__)
# logger.info("This is an info message")
# logger.error("This is an error message")