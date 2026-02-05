"""HTTP client for UnifiedTree API."""

import requests
import urllib3
from typing import Optional, Dict, Any

from unifiedtree.config import Config

# Disable SSL warnings for self-signed certs (common in enterprise)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UTClientError(Exception):
    """API client error."""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class UTClient:
    """UnifiedTree API client."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        
        # Set default headers
        if config.token:
            self.session.headers['Authorization'] = f'Bearer {config.token}'
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['Accept'] = 'application/json'
        
        # SSL verification from config
        self.session.verify = config.ssl_verify
        
        # Request timeout from config
        self.timeout = config.timeout
    
    def _url(self, endpoint: str) -> str:
        """Build full URL."""
        if not self.config.server:
            raise UTClientError("Server URL not configured")
        base_path = self.config.api_base_path.rstrip('/')
        return f"{self.config.server.rstrip('/')}{base_path}{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        try:
            data = response.json()
        except ValueError:
            data = {'message': response.text}
        
        if response.status_code == 401:
            raise UTClientError("Authentication failed. Check your API token.", 401, data)
        elif response.status_code == 403:
            raise UTClientError("Access denied. Insufficient permissions.", 403, data)
        elif response.status_code == 404:
            raise UTClientError("Resource not found.", 404, data)
        elif response.status_code >= 400:
            msg = data.get('detail') or data.get('message') or f"Request failed ({response.status_code})"
            raise UTClientError(msg, response.status_code, data)
        
        return data
    
    def get(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """GET request."""
        response = self.session.get(self._url(endpoint), params=params, timeout=self.timeout)
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: dict = None) -> Dict[str, Any]:
        """POST request."""
        response = self.session.post(self._url(endpoint), json=data, timeout=self.timeout)
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: dict = None) -> Dict[str, Any]:
        """PUT request."""
        response = self.session.put(self._url(endpoint), json=data, timeout=self.timeout)
        return self._handle_response(response)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request."""
        response = self.session.delete(self._url(endpoint), timeout=self.timeout)
        return self._handle_response(response)
