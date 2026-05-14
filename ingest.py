"""
ingest.py — Week 1: Document Ingestion Pipeline
------------------------------------------------
Reads every PDF in ./pdfs, splits the text into chunks, generates
embeddings with OpenAI (as per spec), and persists them in ChromaDB.

Run:
    python ingest.py
"""

import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings          # ✅ fixed: spec requires OpenAI embeddings
from langchain_chroma import Chroma

# Load environment variables (.env must contain OPENAI_API_KEY)
load_dotenv()

CHROMA_DIR = "./chroma_db"
PDF_FOLDER = "./pdfs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ── STEP 1: Read the PDF ──────────────────────────────────────────────────────
def load_pdf(pdf_path: str):
    """
    Extract text page-by-page from a PDF and return parallel lists:
      - page_texts : raw text of each page
      - metadatas  : dict with source filename + page number for citations
    """
    print(f"\n📄 Reading PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    filename = os.path.basename(pdf_path)

    page_texts = []
    metadatas = []

    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():                       # skip blank / image-only pages
            page_texts.append(text)
            metadatas.append({
                "source": filename,
                "page": page_num,
            })

    print(f"   Extracted {len(page_texts)} non-empty pages out of "
          f"{len(reader.pages)} total")
    return page_texts, metadatas


# ── STEP 2: Split text into semantically meaningful chunks ────────────────────
def split_text(page_texts, metadatas):
    """
    Use LangChain's RecursiveCharacterTextSplitter to produce chunks.
    Metadata is propagated to every child chunk so citations stay accurate.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],   # semantic priority order
    )

    all_chunks = []
    all_metas = []

    for text, meta in zip(page_texts, metadatas):
        chunks = splitter.split_text(text)
        all_chunks.extend(chunks)
        # tag every chunk with its parent page metadata + chunk index
        for idx, _ in enumerate(chunks):
            all_metas.append({**meta, "chunk_index": idx})

    print(f"   Split into {len(all_chunks)} chunks "
          f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return all_chunks, all_metas


# ── STEP 3: Embed with OpenAI and store in ChromaDB ──────────────────────────
def store_in_chromadb(chunks, metadatas):
    """
    Generate embeddings using OpenAI's text-embedding-3-small model
    (spec: "generate embeddings using OpenAI's embedding models") and
    upsert into a persistent ChromaDB collection.
    """
    print("   Generating OpenAI embeddings and storing in ChromaDB...")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",   # cost-efficient; swap to
                                          # text-embedding-ada-002 if needed
    )

    vectordb = Chroma.from_texts(
        texts=chunks,
        metadatas=metadatas,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )

    print(f"   Stored {len(chunks)} chunks in ChromaDB at '{CHROMA_DIR}'")
    return vectordb


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.isdir(PDF_FOLDER):
        raise FileNotFoundError(f"PDF folder not found: {PDF_FOLDER}")

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
    if not pdf_files:
        print("Warning: No PDF files found in ./pdfs — place at least one PDF there.")
    else:
        for filename in pdf_files:
            path = os.path.join(PDF_FOLDER, filename)
            page_texts, metadatas = load_pdf(path)
            chunks, chunk_metas = split_text(page_texts, metadatas)
            store_in_chromadb(chunks, chunk_metas)

    print("\nIngestion complete! Your PDFs are now stored in ChromaDB.")
<<<<<<< HEAD
=======

>>>>>>> 04ed9eacdf6716f955a862a731371d2631c9ee9a
