"""
Base client class for the ComfyUI Extension Service.
This class provides the foundation for service-specific clients 
with common functionality for API communication.
"""
import json
import logging
import socket
import uuid
from enum import Enum
from typing import Dict, Any

import requests

from .exceptions import APIError, RateLimitError, ServiceUnavailableError, ValidationError

logger = logging.getLogger(__name__)

class HttpMethod(str, Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"

class Endpoint(str, Enum):
    """Common API endpoints."""
    HEALTH_CHECK = "health/direct"
    CLEAR_CACHE = "admin/clear-cache"
    MEMORY_CLEANUP = "admin/cleanup-memory"


class AuthenticationError:
    pass


class BaseClient:
    """
    Base client class for the ComfyUI Extension Service.
    This class provides the foundation for service-specific clients 
    with common functionality for API communication.
    """
    DEFAULT_TIMEOUT = 60
    DEFAULT_USERNAME = "anonymous"
    DEFAULT_IP = "127.0.0.1"
    DEFAULT_HOSTNAME = "localhost"
    CONTENT_TYPE_JSON = "application/json"

    # Map HTTP status codes to exception classes
    ERROR_STATUS_MAP = {
        401: AuthenticationError,
        422: ValidationError,
        429: RateLimitError,
    }

    def __init__(
            self,
            username: str = None,
            timeout: int = DEFAULT_TIMEOUT,
            headers: Dict[str, str] = None,
    ):
        """
        Initialize the base client.
        
        Args:
            username: The username to use for API calls
            timeout: Request timeout in seconds
            headers: Additional headers to include in requests
        """
        self.username = username or self.DEFAULT_USERNAME
        self.timeout = timeout
        self.headers = headers or {}
        self.headers.update({"Content-Type": self.CONTENT_TYPE_JSON})

        # Get client IP address
        self._setup_client_info()

    def _ensure_url_prefix(self,url: str) -> str:
        if not url:
            return url

        # Remove leading/trailing whitespace
        url = url.strip()

        # If URL doesn't start with http:// or https://, add http://
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        # Convert https:// to http:// for consistency
        if url.startswith("https://"):
            url = "http://" + url[8:]

        return url

    def _setup_client_info(self) -> None:
        """Set up client hostname and IP address information."""
        try:
            self.hostname = socket.gethostname()
            self.ip_address = socket.gethostbyname(self.hostname)
        except Exception as e:
            logger.warning(f"Failed to get client IP address: {e}")
            self.ip_address = self.DEFAULT_IP
            self.hostname = self.DEFAULT_HOSTNAME

    @staticmethod
    def _build_url(base_url: str, endpoint: str) -> str:
        """
        Build a complete URL from .e base URL and endpoint.

        Args:
            base_url: The base URL of the API server
            endpoint: The API endpoint

        Returns:
            The complete URL
        """
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _prepare_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare request data by adding required fields.
        
        Args:
            request_data: The request data
            
        Returns:
            The prepared request data
        """
        # Create a new dictionary to avoid modifying the original
        prepared_data = request_data.copy()

        # Add required fields if not already present
        if "req_id" not in prepared_data:
            prepared_data["req_id"] = str(uuid.uuid4())
        if "user_name" not in prepared_data:
            prepared_data["user_name"] = self.username
        if "ip_address" not in prepared_data:
            prepared_data["ip_address"] = self.ip_address

        return prepared_data

    def _handle_error_status(self, response: requests.Response) -> None:
        """
        Handle error status codes from the API.
        
        Args:
            response: The response object
            
        Raises:
            APIError: If the API returns an error
            ValidationError: If the response cannot be parsed
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ValidationError(f"Invalid JSON response: {response.text}")

        # Check if the response is a BaseResponse
        if isinstance(data, dict) and "success" in data:
            if not data["success"]:
                raise APIError(
                    status_code=response.status_code,
                    message=data.get("msg", "Unknown error"),
                    response=data,
                )

        # Check HTTP status
        if response.status_code >= 400:
            error_message = data.get("detail", "Unknown error")

            # Use the error status map to get the appropriate exception class
            exception_class = self.ERROR_STATUS_MAP.get(
                response.status_code,
                ServiceUnavailableError if response.status_code >= 500 else APIError
            )

            if exception_class == APIError:
                raise exception_class(
                    status_code=response.status_code,
                    message=error_message,
                    response=data,
                )
            else:
                raise exception_class(f"{exception_class.__name__}: {error_message}")

    def _request(
            self,
            base_url: str,
            method: HttpMethod,
            endpoint: str,
            data: Dict[str, Any] = None,
            params: Dict[str, Any] = None,
            files: Dict[str, Any] = None,
            headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        logger.debug(f"base_url:{base_url}")
        url = self._ensure_url_prefix(base_url)
        logger.debug(f"_ensure_url_prefix:{url}")
        url = self._build_url(url, endpoint)
        logger.debug(f"_build_url:{url}")
        request_headers = self.headers.copy()

        if headers:
            request_headers.update(headers)

        # Prepare request data if it's a dict and not a file upload
        if data and isinstance(data, dict) and not files:
            data = self._prepare_request_data(data)

        try:
            kwargs = {
                "method": method.value,
                "url": url,
                "params": params,
                "headers": request_headers,
                "timeout": self.timeout,
            }

            if files:
                if "Content-Type" in request_headers:
                    del request_headers["Content-Type"]
                kwargs["data"] = data
                kwargs["files"] = files
            else:
                kwargs["json"] = data if data else None

            response = requests.request(**kwargs)

            # Log request details before sending
            logger.info(f"Sending {method.value} request to {url}")
            logger.debug(f"Request headers: {request_headers}")
            if data and not files:  # Only log data for non-file requests
                logger.debug(f"Request data: {data}")
            if files:
                logger.debug(f"Files to upload: {list(files.keys())}")
            # Log response details before returning
            logger.info(f"Received response with status {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response content: {response.text[:1000]}...")  # Limit long responses
            # Handle error status codes
            self._handle_error_status(response)
            return response.json()

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Connection error: {str(e)}")
