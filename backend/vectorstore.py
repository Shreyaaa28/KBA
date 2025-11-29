import os
import shutil
import tempfile
from dotenv import load_dotenv
load_dotenv()

import chromadb
from chromadb import PersistentClient


class ChromaVectorStore:
    def __init__(self, collection_name="kb_store"):
        self.collection_name = collection_name

        # 🔥 brand-new temp directory every creation (Streamlit Cloud safe)
        self.path = tempfile.mkdtemp()

        self.client = chromadb.PersistentClient(path=self.path)
        self._initialize_collection()

    def _initialize_collection(self):
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
            embedding_function=None
        )

    def clear(self):
        # Delete entire vector DB
        shutil.rmtree(self.path, ignore_errors=True)

        # Recreate brand new empty directory
        self.path = tempfile.mkdtemp()

        self.client = chromadb.PersistentClient(path=self.path)
        self._initialize_collection()

    def add_vector(self, embedding, chunk, metadata):
        self.collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[metadata],
            ids=[metadata["source"] + "_" + str(metadata["chunk_id"])]
        )

    def query(self, embedding, top_k=4):
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        docs = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            docs.append({"doc": doc, "meta": meta})

        return docs
