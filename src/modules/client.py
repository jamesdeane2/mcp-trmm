"""
Base API client for Tactical RMM
"""
import os
import logging
from typing import Optional, Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TRMMClient:
    """Base client for Tactical RMM API interactions"""
    
    def __init__(self):
        self.api_url = os.getenv("TRMM_API_URL")
        self.api_key = os.getenv("TRMM_API_KEY")
        self.beta_enabled = os.getenv("TRMM_BETA_API_ENABLED", "false").lower() == "true"
        
        if not self.api_url or not self.api_key:
            raise ValueError("TRMM_API_URL and TRMM_API_KEY must be set in environment")
        
        # Remove trailing slash from API URL if present
        self.api_url = self.api_url.rstrip('/')
        
        self.headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to Tactical RMM
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (should start with /)
            data: JSON payload for POST/PUT/PATCH requests
            params: Query parameters
            
        Returns:
            JSON response from API
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Some endpoints may return empty responses
            if response.status_code == 204 or not response.content:
                return {"success": True, "message": "Operation completed successfully"}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error occurred: {e}"
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"HTTP {e.response.status_code}: {error_detail}"
                except:
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request"""
        return self._make_request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request"""
        return self._make_request("POST", endpoint, data=data)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request"""
        return self._make_request("PUT", endpoint, data=data)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PATCH request"""
        return self._make_request("PATCH", endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request"""
        return self._make_request("DELETE", endpoint)
