from typing import Dict, Any


class ClientException(Exception):
    """
    Base exception for all client exceptions.
    All custom exceptions in the ComfyUI Extension Service client inherit from this class.
    """
    pass


class APIError(ClientException):
    """
    Exception raised when the API returns an error.
    
    Attributes:
        status_code (int): HTTP status code returned by the API
        message (str): Error message from the API
        response (Dict[str, Any]): Full response from the API
    """
    def __init__(self, status_code: int = None, message: str = None, response: Dict[str, Any] = None):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"API Error: {status_code} - {message}")


class ConnectionError(ClientException):
    """Exception raised when the client fails to connect to the server."""
    pass


class AuthenticationError(ClientException):
    """Exception raised when authentication fails."""
    pass


class ValidationError(ClientException):
    """Exception raised when request validation fails."""
    pass


class RateLimitError(ClientException):
    """Exception raised when the client hits rate limits."""
    pass


class ServiceUnavailableError(ClientException):
    """
    Exception raised when a service is unavailable.
    This indicates temporary server issues or maintenance.
    """
    pass
