"""Configuration management for UnifiedTree CLI."""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


CONFIG_DIR = Path.home() / ".unifiedtree"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    """CLI configuration."""
    server: Optional[str] = None
    api_base_path: str = "/api/v1"
    token: Optional[str] = None
    ssl_verify: bool = False
    timeout: int = 30
    
    @classmethod
    def load(cls) -> 'Config':
        """Load config from file and environment."""
        config = cls()
        
        # Load from file
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    config.server = data.get('server')
                    config.api_base_path = data.get('api_base_path', '/api/v1')
                    config.token = data.get('token')
                    config.ssl_verify = data.get('ssl_verify', False)
                    config.timeout = data.get('timeout', 30)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Override with environment variables
        if os.environ.get('UNIFIEDTREE_SERVER'):
            config.server = os.environ['UNIFIEDTREE_SERVER']
        if os.environ.get('UNIFIEDTREE_TOKEN'):
            config.token = os.environ['UNIFIEDTREE_TOKEN']
        if os.environ.get('UNIFIEDTREE_API_BASE_PATH'):
            config.api_base_path = os.environ['UNIFIEDTREE_API_BASE_PATH']
        if os.environ.get('UNIFIEDTREE_SSL_VERIFY'):
            config.ssl_verify = os.environ['UNIFIEDTREE_SSL_VERIFY'].lower() == 'true'
        if os.environ.get('UNIFIEDTREE_TIMEOUT'):
            config.timeout = int(os.environ['UNIFIEDTREE_TIMEOUT'])
        
        return config
    
    def save(self):
        """Save config to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'server': self.server,
                'api_base_path': self.api_base_path,
                'token': self.token,
                'ssl_verify': self.ssl_verify,
                'timeout': self.timeout
            }, f, indent=2)
    
    def validate(self):
        """Validate config has required fields."""
        errors = []
        if not self.server:
            errors.append("Server URL not configured. Run: unifiedtree configure")
        if not self.token:
            errors.append("API token not configured. Run: unifiedtree configure")
        return errors
