"""
app/models.py — Pydantic request / response schemas
-----------------------------------------------------
Defines the data shapes for all API endpoints so FastAPI
can auto-validate inputs and auto-document via /docs.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ── /ingest ───────────────────────────────────────────────────────────────────
class IngestResponse(BaseModel):
    message: str
    files_processed: List[str]
    total_chunks: int


# ── /ask (RAG query) ──────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The student's question to the AI tutor.",
        examples=["What is the main theme of the first chapter?"],
    )
    top_k: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Number of document chunks to retrieve from the vector DB.",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID for multi-turn conversational memory.",
    )


class SourceCitation(BaseModel):
    source: str          # filename
    page: int            # page number inside the PDF
    chunk_index: int     # which chunk on that page
    excerpt: str         # first 200 chars of the retrieved chunk


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation]
    model_used: str
<<<<<<< HEAD
=======

>>>>>>> 04ed9eacdf6716f955a862a731371d2631c9ee9a
