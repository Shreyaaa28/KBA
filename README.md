📘 Knowledge Base Agent (RAG + Streamlit + Groq)

A Document-Aware Conversational Agent that lets users upload PDF/TXT files and chat with them using a clean, modern Streamlit interface.  
Powered by Retrieval-Augmented Generation (RAG), Groq Llama-3, and ChromaDB, the system answers strictly from the uploaded content—never hallucinating.

It behaves like your own ChatPDF-style assistant, with:
- Multi-chat sessions  
- Per-session document ingestion  
- Semantic search  
- AI answers grounded in your documents  
- Export answers to TXT/PDF  
- Source citations  
- Fully deployable on Streamlit Cloud  


🚀 Features

Document Handling
- Upload PDF or TXT files  
- Automatic text extraction with PyPDF2  
- Chunking + embedding via SentenceTransformers  

RAG-Based Retrieval
- Store embeddings in ChromaDB  
- Retrieve relevant chunks using semantic search  
- Generate grounded answers using Groq LLM  
- Includes a Sources section with filenames  

AI Answering (LLM)
- Powered by Groq’s Llama 3 / Llama 3.1  
- Answers include summary, detailed reasoning, and sources  
- No hallucination — answers restricted to retrieved content  

Chat System
- Modern Streamlit chat interface  
- Multiple Chat Sessions (like ChatGPT tabs)  
- Each session has its own vector store  
- Clear Chat resets messages only for the current session  

Download Responses
Each assistant response can be exported as:
- TXT (.txt)
- PDF (.pdf) via ReportLab  

Logging (Optional)
- Query logs stored in Supabase  
- Local fallback if Supabase not configured  


⚠️ Limitations

- Answers limited strictly to uploaded content  
- No multi-document merged summarization yet  
- Large PDFs may take time to process  
- Streamlit Cloud resets storage each restart  
- Groq free tier rate limits may apply  
- Vector store is isolated per session  


🛠️ Tech Stack

Frontend
- Streamlit  
- Chat UI  
- Sidebar controls  
- Multi-session UI  
- Download buttons  

Backend
- Python  
- PyPDF2 for PDF parsing  
- SentenceTransformers for embeddings  
- ChromaDB for vector storage & retrieval  
- Groq API for Llama 3 inference  
- ReportLab for PDF export  
- dotenv for environment variables  

Optional
- Supabase for persistent logs  


📐 Architecture Breakdown

Embeddings
- Model: all-MiniLM-L6-v2  
- Used for document chunks + queries  

Vector Database
- ChromaDB PersistentClient  
- Temporary directory mode for Streamlit Cloud  
- Similarity search top_k=4  

LLM (Groq)
- Llama 3 / Llama 3.1  
- Strict RAG grounding  

Chat Sessions
Each session keeps:
- ID  
- Title  
- Chat history  
- Own vector store  


📦 Installation & Setup

1. Clone the Repository
```
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

2. Create Virtual Environment
```
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

3. Install Requirements
```
pip install -r requirements.txt
```


🔐 Environment Variables

Create a .env file:

```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant

CHROMA_DIR=./chroma_store

SUPABASE_URL=
SUPABASE_KEY=
```


▶️ Running the App

Start Streamlit:
```
streamlit run app.py
```

Open browser:
```
http://localhost:8501
```


🧑‍💻 Usage

1. Upload PDFs/TXT  
2. Click Ingest  
3. Ask questions  
4. View Sources  
5. Download answers  
6. Create or switch chats  


🌟 Future Enhancements

- Merge context across documents  
- Improved retrieval reranking  
- Streaming responses  
- Rename/delete chat sessions  
- User authentication  
- Admin dashboard  
- Docker deployment  
- Analytics panel  

