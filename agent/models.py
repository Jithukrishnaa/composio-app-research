from typing import List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    claim: str
    url: str
    source_type: str
    notes: Optional[str] = None


class AppResearch(BaseModel):
    id: int
    app: str
    category: str
    website: str

    description: str

    auth_methods: List[str] = Field(default_factory=list)

    credential_access: str

    api_types: List[str] = Field(default_factory=list)
    api_breadth: str

    mcp_status: str

    buildability: str
    main_blocker: Optional[str] = None

    evidence: List[Evidence] = Field(default_factory=list)

    confidence: float = 0.0

    verified: bool = False
    verification_notes: Optional[str] = None