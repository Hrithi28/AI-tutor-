"""
app/routers/ingest_router.py — Week 1: Ingestion Endpoint
-----------------------------------------------------------
Exposes:
  POST /ingest/upload  — upload a PDF and trigger the ingestion pipeline
  POST /ingest/run     — (re)ingest all PDFs already present in ./pdfs
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.models import IngestResponse
from ingest import load_pdf, split_text, store_in_chromadb

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

PDF_FOLDER = "./pdfs"


@router.post(
    "/upload",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a PDF and ingest it into ChromaDB",
)
async def upload_and_ingest(file: UploadFile = File(...)) -> IngestResponse:
    """
    Accepts a PDF upload, saves it to ./pdfs, then runs the full
    ingestion pipeline (parse → chunk → embed → store).
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    os.makedirs(PDF_FOLDER, exist_ok=True)
    save_path = os.path.join(PDF_FOLDER, file.filename)

    # Save uploaded file to disk
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run ingestion
    try:
        page_texts, metadatas = load_pdf(save_path)
        chunks, chunk_metas = split_text(page_texts, metadatas)
        store_in_chromadb(chunks, chunk_metas)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(exc)}",
        ) from exc

    return IngestResponse(
        message=f"'{file.filename}' ingested successfully.",
        files_processed=[file.filename],
        total_chunks=len(chunks),
    )


@router.post(
    "/run",
    response_model=IngestResponse,
    summary="Re-ingest all PDFs in ./pdfs folder",
)
def run_batch_ingest() -> IngestResponse:
    """
    Triggers the ingestion pipeline for every PDF already present
    in the ./pdfs directory. Useful for initial setup or re-indexing.
    """
    if not os.path.isdir(PDF_FOLDER):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF folder '{PDF_FOLDER}' does not exist.",
        )

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No PDF files found in ./pdfs. Upload one first.",
        )

    total_chunks = 0
    processed = []

    for filename in pdf_files:
        path = os.path.join(PDF_FOLDER, filename)
        try:
            page_texts, metadatas = load_pdf(path)
            chunks, chunk_metas = split_text(page_texts, metadatas)
            store_in_chromadb(chunks, chunk_metas)
            total_chunks += len(chunks)
            processed.append(filename)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed on '{filename}': {str(exc)}",
            ) from exc

    return IngestResponse(
        message=f"Batch ingestion complete. {len(processed)} file(s) processed.",
        files_processed=processed,
        total_chunks=total_chunks,
    )
