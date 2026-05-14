<<<<<<< HEAD
"""
app/rag.py — Week 2: RAG Core Logic
--------------------------------------
Encapsulates:
  1. Loading the persisted ChromaDB vector store
  2. Embedding the user query with OpenAI
  3. Retrieving the top-K most relevant chunks (similarity search)
  4. Building the strict tutor prompt template
  5. Calling the LLM and returning answer + source citations
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

load_dotenv()

CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "text-embedding-3-small"   # must match ingest.py
LLM_MODEL   = "gpt-4o-mini"             # fast + cheap for tutoring
TOP_K       = 4                          # default chunks to retrieve


# ── Strict Tutor Prompt Template ─────────────────────────────────────────────
# The "ONLY the following context" constraint is the key RAG safety guardrail:
# it prevents the LLM from hallucinating facts outside the syllabus.
SYSTEM_TEMPLATE = """You are an expert AI tutor helping a student understand \
their course material.

IMPORTANT RULES:
1. Answer ONLY using the context passages provided below.
2. If the answer is not present in the context, say exactly:
   "I'm sorry, I couldn't find information about that in your course material. \
Please refer to your instructor."
3. Do NOT use any external knowledge beyond what is in the context.
4. Be clear, encouraging, and pedagogical — explain concepts step by step.
5. Where helpful, use bullet points or numbered steps for clarity.

--- CONTEXT START ---
{context}
--- CONTEXT END ---
"""

HUMAN_TEMPLATE = "Student question: {question}"


def get_vectorstore() -> Chroma:
    """
    Load the persisted ChromaDB collection using the same OpenAI embedding
    model that was used during ingestion.  Raises RuntimeError if the DB
    directory does not exist (i.e. ingest.py has not been run yet).
    """
    if not os.path.isdir(CHROMA_DIR):
        raise RuntimeError(
            f"ChromaDB directory '{CHROMA_DIR}' not found. "
            "Please run `python ingest.py` first to ingest your PDF documents."
        )

    embeddings = OpenAIEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )
    return vectorstore


def retrieve_context(question: str, top_k: int = TOP_K):
    """
    Embed the student's question and perform a cosine-similarity search
    against the ChromaDB vector store.

    Returns:
        docs  : list of LangChain Document objects (each has .page_content
                and .metadata with keys: source, page, chunk_index)
    """
    vectorstore = get_vectorstore()
    # similarity_search_with_score returns (Document, score) tuples
    results = vectorstore.similarity_search_with_score(question, k=top_k)
    docs = [doc for doc, _score in results]
    return docs


def build_prompt(context_text: str, question: str) -> list:
    """
    Assemble the two-message prompt:
      - SystemMessage: strict tutor rules + retrieved context
      - HumanMessage : the student's question
    """
    system_content = SYSTEM_TEMPLATE.format(context=context_text)
    return [
        SystemMessage(content=system_content),
        HumanMessage(content=HUMAN_TEMPLATE.format(question=question)),
    ]


def run_rag_query(question: str, top_k: int = TOP_K) -> dict:
    """
    Full RAG pipeline:
      1. Retrieve top-K chunks from ChromaDB
      2. Concatenate them into a single context string
      3. Feed context + question into the LLM via the strict prompt
      4. Return the answer AND structured source citations

    Returns a dict compatible with AskResponse:
        {
            "question": str,
            "answer":   str,
            "sources":  list[dict],   # source, page, chunk_index, excerpt
            "model_used": str,
        }
    """
    # ── Step 1: Retrieve relevant chunks ─────────────────────────────────────
    docs = retrieve_context(question, top_k=top_k)

    if not docs:
        return {
            "question": question,
            "answer": (
                "I'm sorry, I couldn't find information about that in your "
                "course material. Please refer to your instructor."
            ),
            "sources": [],
            "model_used": LLM_MODEL,
        }

    # ── Step 2: Build context string with numbered passages ──────────────────
    context_parts = []
    for i, doc in enumerate(docs, start=1):
        meta = doc.metadata
        header = (
            f"[Passage {i} | Source: {meta.get('source', 'unknown')} "
            f"| Page: {meta.get('page', '?')}]"
        )
        context_parts.append(f"{header}\n{doc.page_content}")

    context_text = "\n\n".join(context_parts)

    # ── Step 3: Call the LLM with the strict prompt ──────────────────────────
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0.2)
    messages = build_prompt(context_text, question)
    response = llm.invoke(messages)
    answer = response.content.strip()

    # ── Step 4: Build structured source citations ────────────────────────────
    sources = []
    for doc in docs:
        meta = doc.metadata
        sources.append({
            "source":      meta.get("source", "unknown"),
            "page":        meta.get("page", 0),
            "chunk_index": meta.get("chunk_index", 0),
            "excerpt":     doc.page_content[:200],   # first 200 chars
        })

    return {
        "question":   question,
        "answer":     answer,
        "sources":    sources,
        "model_used": LLM_MODEL,
    }
=======

>>>>>>> 04ed9eacdf6716f955a862a731371d2631c9ee9a
