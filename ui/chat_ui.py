import streamlit as st
from backend.ingest import ingest_file
from backend.query_engine import answer_query
from backend.db import log_query
import uuid

# NEW IMPORTS FOR PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io


# PDF GENERATOR (Option A: Simple PDF)
def create_pdf(text: str):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    for line in text.split("\n"):
        pdf.drawString(50, y, line)
        y -= 14
        if y < 40:     # new page
            pdf.showPage()
            y = height - 50

    pdf.save()
    buffer.seek(0)
    return buffer


def main_ui():
    st.set_page_config(page_title='Knowledge Base Agent', layout='wide')

    # ---------- MULTI-SESSION SUPPORT ----------
    if "sessions" not in st.session_state:
        st.session_state.sessions = [{
            "id": str(uuid.uuid4()),
            "title": "New Chat",
            "messages": [
                {
                    "role": "assistant",
                    "content": "Hi! Upload some documents on the left, then ask me questions about them.",
                    "sources": [],
                }
            ],
            "vector_store": None,
        }]
        st.session_state.active_session_index = 0

    session = st.session_state.sessions[st.session_state.active_session_index]
    messages = session["messages"]

    st.title('Knowledge Base Agent')

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header('Upload Documents')
        uploaded = st.file_uploader('Upload PDF / TXT', accept_multiple_files=True)

        if st.button('Ingest'):
            if uploaded:
                success_any = False
                for f in uploaded:
                    ok, store = ingest_file(f.name, f.getvalue())
                    if ok and store is not None:
                        session["vector_store"] = store
                        success_any = True
                        st.success(f'Ingested {f.name} into this chat session.')
                    else:
                        st.error(f'Failed to ingest {f.name}')

                st.session_state.sessions[st.session_state.active_session_index] = session
                if success_any:
                    st.rerun()
            else:
                st.warning('Please upload at least one file.')

        st.markdown("---")

        # ---------- CHATS SECTION ----------
        st.subheader("Chats")

        # List existing sessions
        for i, s in enumerate(st.session_state.sessions):
            title = s["title"]
            if i == st.session_state.active_session_index:
                st.markdown(f"**▶ {title}**")
            else:
                if st.button(title, key=f"session_{i}"):
                    st.session_state.active_session_index = i
                    st.rerun()

        # ----- NEW CHAT button (below chat list) -----
        if st.button("New +", key="new_chat_bottom"):
            new_session = {
                "id": str(uuid.uuid4()),
                "title": "New Chat",
                "messages": [
                    {
                        "role": "assistant",
                        "content": "Hi! Upload some documents on the left, then ask me questions about them.",
                        "sources": [],
                    }
                ],
                "vector_store": None,
            }
            st.session_state.sessions.append(new_session)
            st.session_state.active_session_index = len(st.session_state.sessions) - 1
            st.rerun()

        st.markdown('---')
        st.header('Admin')

        if st.button('Show last 20 logs'):
            logs = log_query(question="", answer="", sources=[], limit=20)
            for l in logs:
                st.write(l)

        if st.button("Clear chat"):
            session["messages"] = [
                {
                    "role": "assistant",
                    "content": "Hi! Upload some documents on the left, then ask me questions about them.",
                    "sources": [],
                }
            ]
            st.session_state.sessions[st.session_state.active_session_index] = session
            st.rerun()

    # ---------- MAIN CHAT AREA ----------
    st.header('Chat with your knowledge base')
    st.subheader(f"Session: {session['title']}")

    # Show chat history
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Show sources + download only for REAL answers
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("Sources"):
                    for s in msg["sources"]:
                        st.write(f"- {s}")

                download_text = msg["content"] + "\n\nSources:\n" + "\n".join(msg["sources"])

                st.download_button(
                    label="📄 Download as TXT",
                    data=download_text,
                    file_name="response.txt",
                    mime="text/plain",
                    key=f"txt_{uuid.uuid4()}"
                )

                pdf_file = create_pdf(download_text)
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_file,
                    file_name="response.pdf",
                    mime="application/pdf",
                    key=f"pdf_{uuid.uuid4()}"
                )

    # ---------- CHAT INPUT ----------
    user_input = st.chat_input("Ask a question about your documents")

    if user_input:
        session["messages"].append({"role": "user", "content": user_input, "sources": []})

        if session["title"] == "New Chat":
            session["title"] = user_input[:40]

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, sources = answer_query(
                    user_input,
                    vector_store=session.get("vector_store")
                )
                st.markdown(answer)

                if sources:
                    with st.expander("Sources"):
                        for s in sources:
                            st.write(f"- {s}")

                download_text = answer + ("\n\nSources:\n" + "\n".join(sources) if sources else "")

                st.download_button(
                    label="📄 Download as TXT",
                    data=download_text,
                    file_name="response.txt",
                    mime="text/plain",
                    key=f"new_txt_{uuid.uuid4()}"
                )

                pdf_file = create_pdf(download_text)
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_file,
                    file_name="response.pdf",
                    mime="application/pdf",
                    key=f"new_pdf_{uuid.uuid4()}"
                )

        session["messages"].append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

        try:
            log_query(question=user_input, answer=answer, sources=sources)
        except:
            pass

        st.session_state.sessions[st.session_state.active_session_index] = session
        st.rerun()
