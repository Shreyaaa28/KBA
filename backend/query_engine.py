import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

from models.embedding import get_embedding
from backend.vectorstore import ChromaVectorStore

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_store():
    """
    Return the vector store for the currently active session.
    """
    try:
        idx = st.session_state.active_session_index
        session = st.session_state.sessions[idx]
    except Exception:
        if "vector_store" not in st.session_state:
            st.session_state["vector_store"] = ChromaVectorStore()
        return st.session_state["vector_store"]

    if session.get("vector_store") is None:
        session["vector_store"] = ChromaVectorStore()
        st.session_state.sessions[idx] = session

    return session["vector_store"]


# ✅ FIXED — Groq New SDK authentication
def get_client():
    if "groq_client" not in st.session_state:

        # Load from Streamlit Secrets (Cloud) or .env (local)
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("❌ GROQ_API_KEY is missing — check .env or Streamlit Secrets.")

        # NEW CORRECT SDK CALL
        client = Groq(api_key=api_key)
        st.session_state["groq_client"] = client

    return st.session_state["groq_client"]


def build_prompt(question, docs):
    prompt = (
        "You are an expert research assistant for a knowledge-base chatbot.\n"
        "Your ONLY source of truth is the document excerpts provided below.\n"
        "If the excerpts do not contain enough information to fully answer, "
        "say so clearly.\n\n"
        "When you answer:\n"
        "  - Start with 2–3 sentence summary\n"
        "  - Then give detailed explanation with bullet points\n"
        "  - Quote definitions or key points\n"
        "  - End with 'Sources:' listing filenames\n\n"
        f"User question: {question}\n\n"
        "Document excerpts:\n"
    )

    for i, d in enumerate(docs):
        prompt += f"[{i}] Source: {d['meta'].get('source','unknown')}\n{d['doc']}\n\n"

    prompt += (
        "Important:\n"
        "- Do NOT add inline citations.\n"
        "- Only use the provided excerpts.\n\n"
        "Now write a complete answer based ONLY on the excerpts.\n"
    )

    return prompt


def answer_query(question: str, vector_store=None):
    store = vector_store if vector_store else get_store()
    client = get_client()

    emb = get_embedding(question)
    docs = store.query(emb, top_k=4)

    prompt = build_prompt(question, docs)

    # NEW SDK CALL (structure unchanged)
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Use only the given excerpts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    answer = chat_completion.choices[0].message.content

    sources = list({
        d["meta"].get("source") for d in docs if d["meta"].get("source")
    })

    return answer, sources
