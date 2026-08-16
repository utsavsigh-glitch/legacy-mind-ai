from pydantic import BaseModel
from typing import Any


class AnalysisResponse(BaseModel):
    project_id: str
    summary: dict[str, Any]
    files: list[dict[str, Any]]
    dependencies: list[dict[str, Any]]
    security_findings: list[dict[str, Any]]
    documentation: str
    modernization: list[dict[str, Any]]
    verification: dict[str, Any]
