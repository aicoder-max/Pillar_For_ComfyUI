from .base_client import logger, HttpMethod
from typing import Dict

from .base_client import BaseClient
from ..dto.joy_caption_dto import JoyCaptionRequest
from ..dto.translate_dto import TranslationRequest

class JoyCaptionServiceClient(BaseClient):
    """
    Client for the JoyCaption service that generates captions for images.
    Inherits common functionality from BaseClient.
    """

    def generate_caption(self, base_url: str, request: JoyCaptionRequest) -> Dict[str, str]:
        try:
            data = {
                "system_prompt": request.system_prompt,
                "prompt": request.prompt,
                "max_new_tokens": str(request.max_new_tokens),
                "temperature": str(request.temperature),
                "top_p": str(request.top_p),
                "top_k": str(request.top_k),
                "user_name": self.username  # Use username from client
            }

            files = {
                "image_file": ("image.jpg", request.image_file, "image/jpeg")
            }

            # Make request using base client's _request method
            response = self._request(
                base_url=base_url,
                method=HttpMethod.POST,
                endpoint="joycaption/generate",
                data=data,
                files=files
            )

            # Extract caption data
            return {
                "enCaption": response.get("enCaption", ""),
                "cnCaption": response.get("cnCaption", "")
            }

        except Exception as e:
            logger.error(f"Error in generate_caption: {str(e)}", exc_info=True)
            # Re-raise the exception with original context
            raise e from e

    def translate(self, base_url: str, request: TranslationRequest) -> str:
        """
        Translate text between languages using the translation service.

        Args:
            base_url: The base URL of the API server
            request: The translation request containing text and parameters

        Returns:
            The translated text

        Raises:
            ConnectionError: If there's a network error communicating with the service
            ValueError: If the response format is invalid
        """

        # Build request data using fields from request object
        request_data = {
            "text": request.text,
        }

        # Make request using base client's _request method
        response = self._request(
            base_url=base_url,
            method=HttpMethod.POST,
            endpoint="translate",
            data=request_data
        )

        # Parse response
        if isinstance(response, dict) and "translated_text" in response:
            return response["translated_text"]
        else:
            raise ValueError("Invalid response format: missing translated_text field")