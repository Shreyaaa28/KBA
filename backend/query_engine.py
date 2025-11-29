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

    - If `answer_query` or UI supplies a vector_store directly, it will be used.
    - Otherwise this function ensures each session in `st.session_state.sessions`
      has its own ChromaVectorStore instance (created on-demand) and returns it.
    """
    # Prefer explicit per-session storage inside sessions list
    try:
        idx = st.session_state.active_session_index
        session = st.session_state.sessions[idx]
    except Exception:
        # Fallback: legacy single global vector_store
        if "vector_store" not in st.session_state:
            st.session_state["vector_store"] = ChromaVectorStore()
        return st.session_state["vector_store"]

    # Ensure the session dict has a vector_store key
    if session.get("vector_store") is None:
        session["vector_store"] = ChromaVectorStore()
        st.session_state.sessions[idx] = session

    return session["vector_store"]


def get_client():
    """
    Return a Groq client cached in session_state.
    Uses GROQ_API_KEY from environment or (optionally) st.secrets if set there.
    """
    if "groq_client" not in st.session_state:
        # Try st.secrets first (recommended on Streamlit Cloud), fallback to env var
        api_key = ""
        try:
            api_key = st.secrets.get("GROQ_API_KEY", "")  # type: ignore
        except Exception:
            api_key = os.getenv("GROQ_API_KEY", "")

        st.session_state["groq_client"] = Groq(api_key=api_key)
    return st.session_state["groq_client"]


def build_prompt(question, docs):
    prompt = (
        "You are an expert research assistant for a knowledge-base chatbot.\n"
        "Your ONLY source of truth is the document excerpts provided below.\n"
        "If the excerpts do not contain enough information to fully answer, "
        "say so clearly and explain what is missing instead of guessing.\n\n"
        "When you answer:\n"
        "  - Start with a 2–3 sentence high-level summary.\n"
        "  - Then give a detailed explanation broken into clear sections "
        "    with headings or bullet points where useful.\n"
        "  - Use step-by-step reasoning for any procedures, workflows or calculations.\n"
        "  - Quote or paraphrase important definitions, numbers, and key points "
        "    from the excerpts.\n"
        "  - If there are multiple interpretations or edge cases, explain them.\n"
        "  - At the end, include a line 'Sources:' followed by the filenames you used.\n"
        "  - Do NOT invent information that is not supported by the excerpts.\n\n"
        f"User question: {question}\n\n"
        "Document excerpts:\n"
    )

    for i, d in enumerate(docs):
        prompt += (
            f"[{i}] Source: {d['meta'].get('source', 'unknown')}\n"
            f"{d['doc']}\n\n"
        )

    prompt += (
        "Important:\n"
        "- Do NOT place source names or numbers next to every line.\n"
        "- Use the document chunks ONLY for answering.\n"
        "- Provide the answer normally without inline citations.\n"
        "- At the END, include a section titled 'Sources' and list all unique filenames there.\n\n"
    )

    prompt += (
        "Now, based ONLY on the excerpts above, write a thorough answer to the user question.\n"
    )

    return prompt


def answer_query(question: str, vector_store=None):
    """
    Answer a question using the per-session vector store (preferred) or a supplied one.

    Minimal changes from your original logic:
      - Accepts an optional `vector_store` argument (so UI can pass session["vector_store"])
      - Falls back to get_store() which returns the active-session store (created on demand)
      - Keeps your original prompt style and Groq call
    """
    # Use provided vector_store if passed; otherwise resolve from current session
    store = vector_store if vector_store is not None else get_store()
    client = get_client()

    # compute embedding and retrieve similar chunks
    emb = get_embedding(question)
    docs = store.query(emb, top_k=4)

    # build prompt using original template
    prompt = build_prompt(question, docs)

    # call Groq (kept as your original style)
    chat_completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Use only the given excerpts."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    # Groq response shape: keep using what you used previously
    # `message.content` matches earlier usage
    answer = chat_completion.choices[0].message.content

    # collect unique sources
    sources = list({d["meta"].get("source") for d in docs if d["meta"].get("source")})

    return answer, sources
