"""
RAG (Retrieval-Augmented Generation) pipeline using FAISS vector store.
Indexes the financial knowledge base and retrieves relevant context for the LLM.
"""
import os
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from app.config import get_settings
from app.rag.knowledge_base import KNOWLEDGE_DOCUMENTS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HAS_HF = True
except ImportError:
    HAS_HF = False

settings = get_settings()

FAISS_INDEX_DIR = os.path.join(settings.ml_model_dir, "faiss_index")

_vector_store = None


def _get_embeddings():
    """Returns the HuggingFace local embedding model."""
    if not HAS_HF:
        print("Warning: langchain_huggingface not installed. Embeddings disabled.")
        return None
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def build_index():
    """
    Builds the FAISS index from the knowledge base documents and saves to disk.
    Should be called once during setup or when the knowledge base changes.
    """
    global _vector_store

    embeddings = _get_embeddings()
    if embeddings is None:
        print("Warning: langchain_huggingface not installed. RAG index not built.")
        return

    documents = []
    for doc in KNOWLEDGE_DOCUMENTS:
        documents.append(
            Document(
                page_content=doc["content"],
                metadata={"title": doc["title"]},
            )
        )

    _vector_store = FAISS.from_documents(documents, embeddings)

    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    _vector_store.save_local(FAISS_INDEX_DIR)
    print(f"FAISS index built and saved with {len(documents)} documents.")


def load_index():
    """Loads the FAISS index from disk if it exists."""
    global _vector_store

    embeddings = _get_embeddings()
    if embeddings is None:
        return

    if os.path.exists(os.path.join(FAISS_INDEX_DIR, "index.faiss")):
        _vector_store = FAISS.load_local(
            FAISS_INDEX_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        print("FAISS index loaded from disk.")
    else:
        print("No FAISS index found. Run build_index() first.")


def retrieve(query: str, k: int = 3) -> list[dict]:
    """
    Retrieves the top-k most relevant knowledge documents for a query.
    Returns a list of dicts with 'title' and 'content'.
    """
    global _vector_store

    if _vector_store is None:
        load_index()
    if _vector_store is None:
        return []

    results = _vector_store.similarity_search(query, k=k)
    return [
        {
            "title": doc.metadata.get("title", ""),
            "content": doc.page_content,
        }
        for doc in results
    ]
