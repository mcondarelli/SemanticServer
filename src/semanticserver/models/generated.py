# generated by datamodel-codegen:
#   filename:  openapi.yaml
#   timestamp: 2025-04-10T08:29:46+00:00

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: Optional[List[float]] = Field(None, example=[0.1, -0.23, 0.42])


class Fragment(BaseModel):
    fragment_id: str
    title: Optional[str] = None
    text: str
    metadata: Optional[Dict[str, Any]] = None


class AnalysisRequest(BaseModel):
    text: str
    top_k: Optional[int] = 3
    min_score: Optional[float] = None


class Neighbor(BaseModel):
    fragment_id: Optional[str] = None
    similarity: Optional[float] = None


class AnalysisResult(BaseModel):
    neighbors: Optional[List[Neighbor]] = None
