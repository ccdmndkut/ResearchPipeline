"""
Pipeline Utilities
Configuration management, caching, and helper functions.
"""
import os
import json
import hashlib
from typing import Any, Dict


class ConfigManager:
    """Manages configuration for the pipeline."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config = {
            'chunk_size': 1000,
            'max_results': 5,
            'timeout': 10,
            'vector_dimension': 384
        }
    
    def read_config(self, config_path: str = None) -> Dict[str, Any]:
        """Read configuration from file or environment."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        
        # Override with environment variables
        env_config = {
            'openai_api_key': os.environ.get('OPENAI_API_KEY'),
            'debug': os.environ.get('DEBUG', 'false').lower() == 'true'
        }
        
        self.config.update({k: v for k, v in env_config.items() if v is not None})
        
        return self.config


def cache_result(key: str, data: Any) -> str:
    """Simple caching helper (in-memory for now)."""
    # In production, this would use Redis or similar
    cache_key = hashlib.md5(str(key).encode()).hexdigest()
    return cache_key


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text[:50]  # Limit length