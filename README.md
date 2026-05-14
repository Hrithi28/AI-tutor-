# AI Tutor — Generative AI & RAG Tutoring System
**Infotact Internship — Project 1: Education & EdTech**

An intelligent tutoring system built with **FastAPI**, **LangChain**, **OpenAI**, and **ChromaDB**.  
Upload any course PDF → ask questions → get answers derived *strictly* from your material with source citations.

---

## Project Structure

```
AI-tutor--main/
├── ingest.py                    # Week 1: PDF ingestion pipeline (run once)
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── models.py                # Pydantic request/response schemas
│   ├── rag.py                   # Week 2: RAG core logic (retrieve + generate)
│   └── routers/
│       ├── ingest_router.py     # POST /ingest/upload, POST /ingest/run
│       └── tutor.py             # POST /tutor/ask, GET /tutor/health
├── pdfs/                        # Place your course PDFs here
├── chroma_db/                   # Auto-created: persisted vector store
├── .env.example                 # Copy to .env and fill in your API key
└── requirements.txt
```

---

## Quickstart

### 1. Clone & install dependencies
```bash
git clone <your-repo-url>
cd AI-tutor--main
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set your OpenAI API key
```bash
cp .env.example .env
# Edit .env and set:  OPENAI_API_KEY=sk-...
```

### 3. Ingest your course PDFs

**Option A — Command line (batch):**
```bash
# Place PDFs inside ./pdfs/ then run:
python ingest.py
```

**Option B — Via API (single file upload):**
```bash
uvicorn app.main:app --reload
# Then POST to http://localhost:8000/ingest/upload with your PDF
```

### 4. Start the API server
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Ask the AI Tutor
```bash
curl -X POST http://localhost:8000/tutor/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main theme of chapter one?", "top_k": 4}'
```

Or open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/` | Root — service info |
| `POST` | `/ingest/upload` | Upload a PDF and ingest it |
| `POST` | `/ingest/run` | Re-ingest all PDFs in ./pdfs |
| `GET`  | `/tutor/health` | Liveness check |
| `POST` | `/tutor/ask` | Ask the AI tutor a question |

### POST `/tutor/ask` — Request body
```json
{
  "question": "Explain Newton's second law of motion.",
  "top_k": 4
}
```

### POST `/tutor/ask` — Response
```json
{
  "question": "Explain Newton's second law of motion.",
  "answer": "According to the course material, Newton's second law states...",
  "sources": [
    {
      "source": "physics_chapter3.pdf",
      "page": 12,
      "chunk_index": 2,
      "excerpt": "Newton's second law states that the net force acting on..."
    }
  ],
  "model_used": "gpt-4o-mini"
}
```

---

## Architecture

```
Student Question
      │
      ▼
[OpenAI Embeddings]  ← embed the query
      │
      ▼
[ChromaDB similarity_search]  ← retrieve top-K chunks
      │
      ▼
[Strict Prompt Template]
  "Answer ONLY from the context below..."
      │
      ▼
[GPT-4o-mini]  ← generate answer
      │
      ▼
Answer + Source Citations
```

---

## Week-by-Week Progress

| Week | Task | Status |
|------|------|--------|
| 1 | PDF ingestion pipeline (PyPDF2 → chunking → OpenAI embeddings → ChromaDB) | ✅ Complete |
| 2 | RAG retrieval endpoint (embed query → similarity search → strict prompt → LLM + citations) | ✅ Complete |
| 3 | Conversational memory + quiz generation | 🔄 Upcoming |
| 4 | Educator dashboard + evaluation metrics | 🔄 Upcoming |
