import uuid
from pydantic import Field
from ..dto.base_dto import BaseRequest, BaseResponse


class TranslationRequest(BaseRequest):
    """Request model for translation API"""
    text: str
    user_name: str = "anonymous"
    ip_address: str = "anonymous"
    req_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class TranslationResponse(BaseResponse):
    """Response model for translation API"""
    translated_text: str = ""
    original_text: str = ""
    success: bool = True
    req_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_time: float = 0.0
    rel_req_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
