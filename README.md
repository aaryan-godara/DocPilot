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

## ✨ Features (Planned)

- [x] PDF document upload via web UI
- [x] FastAPI backend with health monitoring
- [x] Structured logging and configuration
- [x] PDF parsing and text extraction
- [x] Intelligent text chunking with overlap
- [ ] Embedding generation using Sentence Transformers
- [ ] Vector storage and retrieval with ChromaDB
- [ ] LLM-powered answer generation with OpenAI
- [ ] Citations with page numbers in responses
- [ ] Multi-document support
- [ ] Conversation history and follow-up questions
- [ ] Dockerized deployment

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

> **Current scope (Week 1):** Only the PDF Upload → Backend storage path is implemented. The full RAG pipeline will be built in Weeks 2–4.

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.10+ | Core application language |
| **Backend** | FastAPI | REST API server |
| **Frontend** | Streamlit | Interactive web interface |
| **PDF Processing** | PyMuPDF | Text extraction from PDFs |
| **LLM Framework** | LangChain | RAG pipeline orchestration |
| **LLM Provider** | OpenAI SDK | Answer generation |
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
│   │   └── routes/
│   │       ├── health.py      # Health check endpoint
│   │       └── upload.py      # PDF upload endpoint
│   └── utils/
│       └── logger.py          # Logging configuration
│
├── data/
│   ├── raw/                   # Uploaded PDFs
│   ├── processed/             # Chunked & embedded data
│   └── sample/                # Sample documents for testing
│
├── docs/
│   ├── design_doc.md          # Design document
│   ├── architecture.md        # Architecture deep-dive
│   └── adr/                   # Architecture Decision Records
│
├── notebooks/                 # Jupyter notebooks for experiments
├── tests/                     # Unit & integration tests
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
| Architecture document | ✅ Complete |
| FastAPI server | ✅ Complete |
| Health endpoint | ✅ Complete |
| Upload endpoint | ✅ Complete |
| Streamlit frontend | ✅ Complete |
| Logging & configuration | ✅ Complete |
| PDF parsing | ✅ Complete |
| Text chunking | ✅ Complete |
| Process endpoint | ✅ Complete |
| Embeddings | 🔲 Week 2 |
| Vector database | 🔲 Week 3 |
| RAG pipeline | 🔲 Week 3 |
| Answer generation | 🔲 Week 4 |

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

---

## 🚀 Upcoming Milestones

| Week | Milestone | Key Deliverables |
|------|-----------|-----------------|
| **Week 2** | PDF Processing Pipeline | Text extraction, chunking, embedding generation |
| **Week 3** | RAG Core | Vector database integration, retriever, LLM integration |
| **Week 4** | Polish & Deploy | Citations, UI improvements, Docker deployment, testing |

---

## 🔮 Future Scope

- 🔄 **Multi-document Q&A** — Query across multiple uploaded PDFs simultaneously
- 💬 **Conversational Memory** — Follow-up questions with context retention
- 📊 **Analytics Dashboard** — Track query patterns and document usage
- 🔐 **Authentication** — User accounts and document access control
- 🌐 **Cloud Deployment** — AWS/GCP deployment with CI/CD pipeline
- 📱 **Responsive UI** — Mobile-friendly interface
- 🧪 **Evaluation Framework** — Automated RAG quality metrics (faithfulness, relevance)

---

## 🚀 Quick Start

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

# Copy environment variables
cp .env.example .env

# Start the backend
uvicorn app.backend.main:app --reload --port 8000

# In a new terminal — start the frontend
streamlit run app/frontend/streamlit_app.py --server.port 8501
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
