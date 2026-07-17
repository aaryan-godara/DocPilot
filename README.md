<div align="center">

# 📚 DocPilot

**Ask questions about any PDF document and get answers with citations and page numbers.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Problem Statement

Reading through long PDF documents to find specific information is time-consuming and inefficient. **DocPilot** solves this by building a Retrieval-Augmented Generation (RAG) pipeline that lets users upload PDF documents, ask natural-language questions, and receive precise answers with **citations and page numbers** — grounded in the actual document content.

## 🏷️ Project Info

| Field | Value |
|-------|-------|
| **Segment** | Foundations of Applied Machine Learning |
| **Project Code** | I2 – Document Q&A (RAG) |
| **Author** | [Aaryan Godara](https://github.com/aaryan-godara) |

---

## ✨ Features

- [x] PDF document upload via web UI
- [x] FastAPI backend with health monitoring
- [x] Structured logging and configuration
- [x] PDF parsing and text extraction
- [x] Intelligent text chunking with overlap
- [x] Embedding generation using Sentence Transformers
- [x] Vector storage and retrieval with ChromaDB
- [x] LLM-powered answer generation with Grok (xAI)
- [x] Citations with page numbers in responses
- [x] Multi-document support
- [x] Conversation history and follow-up questions
- [x] Dockerized deployment

---

## 🏗️ Architecture Overview

```
                    ┌─────────────────┐
                    │   PDF Upload    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   PDF Parsing   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Chunking     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Embedding     │
                    │   Generation    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Vector Database │◄──────┐
                    └────────┬────────┘       │
                             │                │
  ┌──────────────┐  ┌────────▼────────┐       │
  │ User Question├──►   Retriever     │───────┘
  └──────────────┘  └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │      LLM        │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Answer +        │
                    │ Citation        │
                    └─────────────────┘
```

> **Current scope (Week 4):** All features complete — full RAG pipeline, multi-document support, conversation history, and Docker deployment.

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.10+ | Core application language |
| **Backend** | FastAPI | REST API server |
| **Frontend** | Streamlit | Interactive web interface |
| **PDF Processing** | PyMuPDF | Text extraction from PDFs |
| **LLM Framework** | LangChain | Text chunking |
| **LLM Provider** | Grok (xAI) via OpenAI SDK | Answer generation |
| **Embeddings** | Sentence Transformers | Document & query embeddings |
| **Vector Database** | ChromaDB | Similarity search & storage |
| **Containerization** | Docker | Deployment & reproducibility |
| **Version Control** | Git + GitHub | Source management |

---

## 📁 Folder Structure

```
DocPilot/
│
├── app/
│   ├── frontend/              # Streamlit UI
│   │   └── streamlit_app.py
│   ├── backend/               # FastAPI server
│   │   ├── main.py            # App entry point
│   │   ├── config.py          # Settings & env vars
│   │   ├── routes/
│   │   │   ├── health.py      # GET /health
│   │   │   ├── upload.py      # POST /upload
│   │   │   ├── process.py     # POST /process/{filename}
│   │   │   └── ask.py         # POST /ask
│   │   └── services/
│   │       ├── pdf_parser.py       # PyMuPDF text extraction
│   │       ├── chunker.py          # LangChain text splitting
│   │       ├── embedding_service.py # Sentence Transformers
│   │       ├── vector_store.py     # ChromaDB wrapper
│   │       ├── llm_client.py       # Grok/xAI LLM client
│   │       └── rag_pipeline.py     # Orchestrates everything
│   └── utils/
│       └── logger.py          # Logging configuration
│
├── data/
│   ├── raw/                   # Uploaded PDFs
│   ├── processed/             # ChromaDB vector store
│   └── sample/                # Sample documents for testing
│
├── docs/
│   ├── design_doc.md          # Design document
│   ├── progress_summary.md    # Complete progress log
│   └── adr/                   # Architecture Decision Records
│
├── tests/                     # Unit & integration tests (50 tests)
├── notebooks/                 # Jupyter notebooks for experiments
├── scripts/                   # Utility scripts
│
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Container orchestration
├── .env.example               # Environment variable template
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📊 Current Progress

| Component | Status |
|-----------|--------|
| Project structure | ✅ Complete |
| README & documentation | ✅ Complete |
| Design document | ✅ Complete |
| FastAPI server | ✅ Complete |
| Health endpoint | ✅ Complete |
| Upload endpoint | ✅ Complete |
| Streamlit frontend | ✅ Complete |
| Logging & configuration | ✅ Complete |
| PDF parsing | ✅ Complete |
| Text chunking | ✅ Complete |
| Process endpoint | ✅ Complete |
| Embeddings (Sentence Transformers) | ✅ Complete |
| Vector database (ChromaDB) | ✅ Complete |
| RAG pipeline | ✅ Complete |
| LLM answer generation (Grok) | ✅ Complete |
| `/ask` endpoint | ✅ Complete |
| Q&A UI with citations | ✅ Complete |
| Docker deployment | ✅ Week 4 |

---

## 📅 Week 1 Progress

- [x] Initialized project repository with clean folder structure
- [x] Created comprehensive README with architecture overview
- [x] Wrote design document with requirements and timeline
- [x] Wrote architecture document with component breakdown
- [x] Set up FastAPI backend with CORS and lifecycle management
- [x] Implemented `GET /health` endpoint
- [x] Implemented `POST /upload` endpoint for PDF files
- [x] Built Streamlit frontend with file upload widget
- [x] Configured structured logging
- [x] Set up environment-based configuration with pydantic-settings
- [x] Added requirements.txt with all dependencies
- [x] Created docker-compose.yml placeholder

---

## 📅 Week 2 Progress

- [x] Built `PDFParser` service using PyMuPDF for page-level text extraction
- [x] Built `TextChunker` service using LangChain's `RecursiveCharacterTextSplitter`
- [x] Implemented page-number tracking across chunk boundaries (for citations)
- [x] Added `POST /process/{filename}` endpoint to run the parse → chunk pipeline
- [x] Added `chunk_size`, `chunk_overlap`, and `processed_dir` to app configuration
- [x] Created `PageContent` and `DocumentChunk` dataclasses for structured data flow
- [x] Wrote 22 unit tests (9 for parser, 13 for chunker) — all passing ✅

---

## 📅 Week 3 Progress

- [x] Built `EmbeddingService` using Sentence Transformers (`all-MiniLM-L6-v2`, 384-dim)
- [x] Built `VectorStoreService` using ChromaDB (persistent, cosine similarity, upsert)
- [x] Built `LLMClient` for Grok/xAI via OpenAI SDK (citation-focused prompting)
- [x] Built `RAGPipeline` orchestrator (ingestion + query flows)
- [x] Added `POST /ask` endpoint for question answering
- [x] Updated `/process` to run full ingestion pipeline (embed + store)
- [x] Enabled Q&A in Streamlit UI with answer display, citation tags, and source chunks
- [x] Updated configuration for xAI, embeddings, LLM, and retrieval settings
- [x] Wrote 28 new tests (50 total) — all passing ✅

---

## 📅 Week 4 Progress

- [x] Added **multi-document support** — document selector in Q&A UI (search one PDF or all at once)
- [x] Added **conversation history** — LLM receives prior Q&A turns for follow-up question support (capped at 6 turns)
- [x] Added `conversation_history` to `AskRequest`, `RAGPipeline`, and `LLMClient` — full pipeline support
- [x] Shows searched-document badge on each Q&A history card
- [x] `BACKEND_URL` now reads from `os.environ` for Docker/cloud compatibility
- [x] Wrote `Dockerfile` (backend, Python 3.11-slim, port 8000)
- [x] Wrote `Dockerfile.frontend` (Streamlit, Python 3.11-slim, port 8501)
- [x] Wired `docker-compose.yml` with health check, data volume, and internal networking
- [x] Added `.dockerignore` to keep builds fast and secure
- [x] Total: **59 tests passing** ✅ — all existing tests still green after Week 4 changes

---

## 📝 What I Learned

- **Week 1:**
  - Setting up a clean project structure early saves a lot of time later.
  - FastAPI's auto-generated OpenAPI docs (`/docs`) make testing endpoints very easy.
  - Using `pydantic-settings` for configuration keeps environment management clean and type-safe.
  - Separating routes into individual files (health, upload) keeps the codebase modular and readable.

- **Week 2:**
  - **PyMuPDF (`fitz`)** is extremely fast for PDF text extraction — it handles page-level access natively, which is essential for building citation features later.
  - **Page-number tracking through the chunking process** was the trickiest part. Since chunks can straddle page boundaries (due to overlap), I had to build a character-offset mapping to trace each chunk back to its source page(s).
  - **LangChain's `RecursiveCharacterTextSplitter`** is smart about splitting — it tries paragraph and sentence boundaries before falling back to character-level splits, which produces more meaningful chunks.
  - Choosing the right **chunk size and overlap** is a design trade-off: smaller chunks give more precise retrieval but lose context; larger chunks preserve context but may dilute relevance. The defaults (1000 chars / 200 overlap) are a good starting point.
  - **Dataclasses** (`PageContent`, `DocumentChunk`) make it much easier to pass structured data between services compared to raw dictionaries.
  - Writing tests *alongside* the code (not after) caught edge cases early — e.g., empty PDFs, single-chunk documents, and page boundary tracking.

- **Week 3:**
  - **The xAI API being OpenAI SDK-compatible** is a huge win — switching LLM providers is literally changing `base_url` and `api_key`.
  - **Lazy initialization is critical for developer experience.** Without it, every `uvicorn --reload` would load the 80 MB embedding model. With it, the server starts in <1 second.
  - **Prompt engineering matters more than model size** for citation quality. The system prompt explicitly instructs `[Page X]` format and "only answer from context."
  - **ChromaDB's upsert** saves a lot of complexity — re-processing is idempotent, no duplicate detection needed.
  - **Mocking the LLM in tests** is essential — pipeline tests shouldn't require an API key or hit a real endpoint.

- **Week 4:**
  - **Multi-doc was already 80% done** — the vector store's `filename` filter was built in Week 3. The entire Week 4 addition was a frontend selectbox and passing the field in the payload. Good architecture pays off.
  - **Conversation history requires careful token budgeting.** Capping at 6 turns prevents the context window from overflowing on longer conversations with dense document context.
  - **Docker's `depends_on: condition: service_healthy`** is essential — without it, Streamlit tries to connect before FastAPI finishes loading the embedding model, causing cryptic errors.
  - **`.dockerignore` matters** — without it, Docker copies the entire `data/` directory (gigabytes of ChromaDB vectors) into the build context, making builds very slow.
  - **`os.environ.get("BACKEND_URL", "http://localhost:8000")`** is the standard pattern for making a service work both locally and in Docker without code changes.

---

## 🚀 Upcoming Milestones

| Week | Milestone | Key Deliverables | Status |
|------|-----------|-----------------|---------|
| **Week 1** | Project Setup | Repository, docs, FastAPI + Streamlit scaffold, upload | ✅ Done |
| **Week 2** | PDF Processing | Text extraction, chunking, process endpoint | ✅ Done |
| **Week 3** | RAG Pipeline | Embeddings, ChromaDB, Grok LLM, /ask endpoint, Q&A UI | ✅ Done |
| **Week 4** | Polish & Deploy | Multi-doc, conversation history, Docker deployment | ✅ Done |

---

## 🔮 Future Scope

- 📊 **Analytics Dashboard** — Track query patterns and document usage
- 🔐 **Authentication** — User accounts and document access control
- 🌐 **Cloud Deployment** — AWS/GCP deployment with CI/CD pipeline
- 📱 **Responsive UI** — Mobile-friendly interface
- 🧪 **Evaluation Framework** — Automated RAG quality metrics (faithfulness, relevance)
- 📄 **More File Formats** — Support DOCX, TXT, and web URLs alongside PDFs

---

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/aaryan-godara/DocPilot.git
cd DocPilot

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables and set your xAI API key
cp .env.example .env
# Edit .env and set XAI_API_KEY=xai-your-actual-key

# Start the backend
uvicorn app.backend.main:app --reload --port 8000

# In a new terminal — start the frontend
streamlit run app/frontend/streamlit_app.py --server.port 8501
```

### Docker (Recommended)

```bash
# Copy environment variables and set your xAI API key
cp .env.example .env
# Edit .env and set XAI_API_KEY=xai-your-actual-key

# Build and start both services (one command!)
docker compose up --build

# Backend  → http://localhost:8000
# Frontend → http://localhost:8501

# Stop
docker compose down
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
