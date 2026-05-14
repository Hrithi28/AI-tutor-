"""
app/routers/tutor.py — Week 2: RAG Query Endpoint
---------------------------------------------------
Exposes:
  POST /ask   — student submits a question, gets answer + citations
  GET  /health — liveness check
"""

from fastapi import APIRouter, HTTPException, status
from app.models import AskRequest, AskResponse, SourceCitation
from app.rag import run_rag_query

router = APIRouter(prefix="/tutor", tags=["Tutor"])


@router.get("/health", summary="Health check")
def health_check():
    """Simple liveness probe — confirm the tutor service is running."""
    return {"status": "ok", "service": "AI Tutor"}


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the AI Tutor a question",
    description=(
        "Embeds the student's question, retrieves the top-K most relevant "
        "chunks from ChromaDB, and passes them through a strict RAG prompt "
        "to the LLM. Returns the answer and source document citations."
    ),
)
def ask_tutor(request: AskRequest) -> AskResponse:
    """
    RAG Query endpoint — the core Week 2 deliverable.

    Steps performed internally:
      1. Embed the query using OpenAI embeddings
      2. Similarity-search ChromaDB for top_k chunks
      3. Build strict prompt: ONLY answer from the retrieved context
      4. Call GPT-4o-mini and return answer + structured citations
    """
    try:
        result = run_rag_query(question=request.question, top_k=request.top_k)
    except RuntimeError as exc:
        # ChromaDB not initialised yet
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG pipeline error: {str(exc)}",
        ) from exc

    # Map raw dicts to Pydantic SourceCitation objects
    citations = [SourceCitation(**s) for s in result["sources"]]

    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        sources=citations,
        model_used=result["model_used"],
    )
