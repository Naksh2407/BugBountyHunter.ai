from pydantic import BaseModel
from typing import Dict, Any, Optional

class ScanCreate(BaseModel):
    github_url: str

class ScanResponse(BaseModel):
    id: str
    repository_id: str
    findings: Optional[Dict[str, Any]] = None
    status: str

    class Config:
        from_attributes = True
