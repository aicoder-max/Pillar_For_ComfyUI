from fastapi import UploadFile, File, Form

from ..dto.base_dto import BaseRequest, BaseResponse
from ..util.constants import DEFAULT_TEMPERATURE, DEFAULT_MAX_NEW_TOKENS, DEFAULT_TOP_P, \
    DEFAULT_SYSTEM_PROMPT, DEFAULT_TOP_K


class JoyCaptionResponse(BaseResponse):
    """Response model for JoyCaption API"""
    enCaption: str = ""
    cnCaption: str = ""

class JoyCaptionRequest(BaseRequest):
    """Request model for generate_caption API with Form fields"""
    image_file: bytes  
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    prompt: str
    max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    top_p: float = DEFAULT_TOP_P
    top_k: int = DEFAULT_TOP_K

    @classmethod
    def as_form(
            cls,
            image_file: bytes,
            system_prompt: str = Form(DEFAULT_SYSTEM_PROMPT),
            prompt: str = Form("Describe this image"),
            max_new_tokens: int = Form(DEFAULT_MAX_NEW_TOKENS),
            temperature: float = Form(DEFAULT_TEMPERATURE),
            top_p: float = Form(DEFAULT_TOP_P),
            top_k: int = Form(DEFAULT_TOP_K),
    ):
        """Factory method to create GenCaptionRequest from .rm fields"""
        return cls(
            image_file=image_file,
            system_prompt=system_prompt,
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            user_name="testUser"  
        )
