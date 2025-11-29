import os
from io import BytesIO
from PyPDF2 import PdfReader
from models.embedding import get_embedding
from backend.vectorstore import ChromaVectorStore


def extract_text_from_pdf_bytes(bytes_data):
    reader = PdfReader(BytesIO(bytes_data))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def ingest_file(filename, content_bytes):
    """
    Creates a NEW vectorstore for this ingestion.
    Returns:
        (True, store)   → success
        (False, None)  → failed
    """

    # Create a fresh vector store for THIS session's ingestion.
    store = ChromaVectorStore()

    # Extract text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf_bytes(content_bytes)
    else:
        try:
            text = content_bytes.decode("utf-8")
        except:
            return False, None

    if not text:
        return False, None

    # Chunking
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Add embeddings
    for i, chunk in enumerate(chunks):
        emb = get_embedding(chunk)
        meta = {"source": filename, "chunk_id": i}
        store.add_vector(emb, chunk, meta)

    # Return store so UI can attach it to the active chat session
    return True, store
