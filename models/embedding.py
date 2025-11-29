# models/embedding.py
from sentence_transformers import SentenceTransformer

# Downloaded once, then cached locally
_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text: str):
    """
    Return a dense embedding vector (list of floats) for the given text.
    Compatible with ChromaDB.
    """
    emb = _model.encode(text, show_progress_bar=False)
    return emb.tolist()

