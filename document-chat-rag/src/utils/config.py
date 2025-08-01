"""
Configuration Utility Module

Provides functions for loading and accessing configuration files.
"""

import yaml
import os
from typing import Dict, Any

def get_config(config_path: str = "config/processing.yaml") -> Dict[str, Any]:
    """
    Load and return configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing the configuration
    """
    # If the path is relative, make it absolute from the project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
    
    # Load configuration from YAML file
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    return config