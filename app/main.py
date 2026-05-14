"""
app/main.py — FastAPI Application Entry Point
----------------------------------------------
Wires together the FastAPI app, mounts all routers, and exposes
auto-generated OpenAPI docs at /docs.

Run development server:
    uvicorn app.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.tutor import router as tutor_router
from app.routers.ingest_router import router as ingest_router

# ── Application factory ───────────────────────────────────────────────────────
app = FastAPI(
    title="AI Tutor — Generative AI & RAG Tutoring System",
    description=(
        "An intelligent tutoring system powered by Retrieval-Augmented Generation (RAG). "
        "Upload course PDFs, then ask questions — the AI answers ONLY from your material."
    ),
    version="2.0.0",
    contact={
        "name": "Infotact Internship — Project 1",
    },
)

# ── CORS (allow all origins for development; restrict in production) ──────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──────────────────────────────────────────────────────────
app.include_router(ingest_router)   # /ingest/*   — Week 1
app.include_router(tutor_router)    # /tutor/*    — Week 2


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "AI Tutor is running!",
        "docs":    "Visit /docs for the interactive API documentation.",
        "week_1":  "POST /ingest/upload  — Upload and ingest a course PDF",
        "week_2":  "POST /tutor/ask      — Ask the AI tutor a question",
    }
