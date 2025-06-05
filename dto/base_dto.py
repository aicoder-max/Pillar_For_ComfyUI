

import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    user_name: str = "anonymous"
    ip_address: str = "anonymous"
    req_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class BaseResponse(BaseModel):
    res_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rel_req_id: str
    res_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    msg: str = "Request processed successfully"


# Cache management specific models
class CacheClearRequest(BaseRequest):
    service: Optional[str] = None  # If None, clear all caches


class CacheClearResponse(BaseResponse):
    cleared_count: int = 0
    cleared_services: List[str] = []


# Memory management specific models
class MemoryCleanupRequest(BaseRequest):
    service: str  # Required, must specify which service to clean up


class MemoryCleanupResponse(BaseResponse):
    freed_memory: bool = False
    cleanup_details: str = ""
