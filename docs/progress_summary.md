# DocPilot - Complete Progress Summary

> **This is a personal/supplementary log, not the official status doc.**  
> **Last Updated:** July 17, 2026

---

## 📖 Complete Story: From Zero to End-to-End RAG

### **What We Built**
DocPilot is a Retrieval-Augmented Generation (RAG) application that:
- Accepts PDF uploads from users via a web UI
- Parses, chunks, and embeds document content
- Stores embeddings in a ChromaDB vector database
- Retrieves the most relevant chunks for a given question
- Generates a natural-language answer with **citations and page numbers** via Grok (xAI)

**Target Use Case:** Students, researchers, and professionals who need to extract specific information from lengthy PDF documents without reading the whole thing.

---

## ✅ Week 1: Project Setup & Foundation (COMPLETE)

### **1.1 - Repository & Project Structure**

**What we did:**
- Initialized the GitHub repository with a professional folder structure
- Created comprehensive README with architecture diagrams and badges
- Wrote a detailed design document covering requirements, tech choices, risks, and timeline
- Set up `.gitignore` to exclude virtual environments, cache files, and data directories

**Repository:** `github.com/aaryan-godara/DocPilot`

**Directory structure:**
```
DocPilot/
├── app/
│   ├── frontend/              # Streamlit UI
│   │   └── streamlit_app.py
│   ├── backend/               # FastAPI server
│   │   ├── main.py            # App entry point
│   │   ├── config.py          # Settings & env vars
│   │   ├── routes/
│   │   │   ├── health.py      # Health check endpoint
│   │   │   ├── upload.py      # PDF upload endpoint
│   │   │   ├── process.py     # Parse → chunk → embed → store
│   │   │   └── ask.py         # Question answering endpoint
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
│   └── processed/             # ChromaDB vector store
│
├── docs/
│   ├── design_doc.md          # Design document
│   └── progress_summary.md    # This file
│
├── tests/                     # Unit & integration tests
│   ├── test_health.py
│   ├── test_pdf_parser.py
│   ├── test_chunker.py
│   ├── test_embedding_service.py
│   ├── test_vector_store.py
│   └── test_rag_pipeline.py
│
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

### **1.2 - FastAPI Backend Scaffold**

**What we built:**
- [x] FastAPI application with CORS middleware and lifecycle management
- [x] `GET /health` — service health check with version info
- [x] `POST /upload` — PDF file upload with size validation and duplicate handling
- [x] Centralized configuration via `pydantic-settings` (reads from `.env`)
- [x] Structured logging (timestamp | level | module | message)

**Why this matters:** The backend scaffold establishes the API contract early. All endpoints are auto-documented at `/docs` via OpenAPI.

---

### **1.3 - Streamlit Frontend (Upload-Only)**

**What we built:**
- [x] File upload widget with drag-and-drop support
- [x] Backend health check in the sidebar
- [x] Upload progress indicators and error handling
- [x] Q&A section placeholder (disabled, marked "Coming in Week 3")

---

### **1.4 - Configuration & Environment**

**Settings managed via `.env`:**
```
APP_NAME, APP_VERSION, DEBUG
BACKEND_HOST, BACKEND_PORT
UPLOAD_DIR, LOG_LEVEL
```

**Tech stack locked in:**
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.10+ | ML ecosystem, type hints, async |
| API | FastAPI | Auto-docs, type validation, async |
| Frontend | Streamlit | Rapid prototyping, built-in widgets |
| PDF Parser | PyMuPDF | Fast, accurate, page-level metadata |
| Chunking | LangChain | Configurable, respects text boundaries |
| Embeddings | Sentence Transformers | Open-source, runs locally, good quality |
| Vector DB | ChromaDB | Lightweight, Python-native, persistent |
| LLM | Grok (xAI) | OpenAI SDK-compatible, good generation quality |
| Containerization | Docker | Reproducible deployments |

---

## ✅ Week 2: PDF Processing Pipeline (COMPLETE)

### **2.1 - PDF Parser Service**

**What we built (`app/backend/services/pdf_parser.py`):**
- [x] `PDFParser` class using PyMuPDF (`fitz`) for page-level text extraction
- [x] `PageContent` dataclass: `page_number` (1-indexed), `text`, `char_count`
- [x] Error handling for missing files, invalid PDFs, and corrupted documents
- [x] Convenience function `parse_document()` for quick use

**Why this matters:** Page-number preservation is the foundation of the citation system. Every chunk traces back to its source page(s).

---

### **2.2 - Text Chunking Service**

**What we built (`app/backend/services/chunker.py`):**
- [x] `TextChunker` using LangChain's `RecursiveCharacterTextSplitter`
- [x] Configurable chunk size (default 1000) and overlap (default 200)
- [x] **Page-number tracking across chunk boundaries** — the trickiest part
  - Concatenates all page texts, tracks character offsets per page
  - When a chunk straddles two pages (due to overlap), it records both page numbers
- [x] `DocumentChunk` dataclass: `chunk_id`, `text`, `page_numbers[]`, `source_file`, `char_count`

**Design decision:** Character-offset mapping was chosen over simpler approaches because chunks near page boundaries need to cite all relevant pages for accurate citations.

---

### **2.3 - Process Endpoint**

**What we built (`app/backend/routes/process.py`):**
- [x] `POST /process/{filename}` — runs parse → chunk pipeline on an uploaded PDF
- [x] Returns page count, chunk count, and chunk previews (first 200 chars)

---

### **2.4 - Tests**

**22 unit tests, all passing:**
- `test_pdf_parser.py` (9 tests) — valid PDFs, non-PDF files, missing files, empty PDFs
- `test_chunker.py` (13 tests) — chunk counts, page tracking, overlap, single-page docs, empty input
- `test_health.py` — health endpoint returns correct status

---

## ✅ Week 3: RAG Pipeline (COMPLETE)

### **3.1 - Embedding Service**

**What we built (`app/backend/services/embedding_service.py`):**
- [x] `EmbeddingService` wrapping Sentence Transformers (`all-MiniLM-L6-v2`)
- [x] **Lazy model loading** — model downloads (~80 MB) on first use, not at import
- [x] `embed_texts(texts)` — batch embedding, returns list of 384-dim float vectors
- [x] `embed_query(query)` — single query embedding
- [x] `dimension` property for introspection

**Verified:** 10/10 tests passing — consistent embeddings, correct dimensions, empty input handling.

---

### **3.2 - Vector Store Service (ChromaDB)**

**What we built (`app/backend/services/vector_store.py`):**
- [x] `VectorStoreService` wrapping ChromaDB `PersistentClient`
- [x] Single collection (`docpilot_documents`) with cosine similarity
- [x] `add_chunks(chunks, embeddings)` — upsert (no duplicates on re-processing)
- [x] `query(embedding, top_k, filename?)` — similarity search with optional document filter
- [x] `delete_document(filename)` — remove all chunks for a specific PDF
- [x] `list_documents()` — unique filenames in the store
- [x] Metadata stored per chunk: `source_file`, `page_numbers`, `char_count`
- [x] Persistent storage at `data/processed/chroma/` (survives restarts)

**Verified:** 13/13 tests passing — add, query, top-k, metadata, filename filtering, upsert, delete, list.

---

### **3.3 - LLM Client (Grok / xAI)**

**What we built (`app/backend/services/llm_client.py`):**
- [x] `LLMClient` using the OpenAI SDK with `base_url="https://api.x.ai/v1"`
- [x] System prompt instructs the model to:
  - Answer only from the provided context
  - Cite page numbers for every claim (`[Page X]` format)
  - Say "I don't know" if the context doesn't cover the question
- [x] Context builder formats retrieved chunks with page labels
- [x] `LLMResponse` dataclass: `answer`, `citations`, `model`, `tokens_used`, `latency_seconds`
- [x] Configurable model (`grok-3-mini` default), temperature (0.2), max tokens (1000)
- [x] Error handling for missing API key, rate limits, timeouts

**Why Grok over OpenAI?** User preference — the xAI API is OpenAI SDK-compatible, so we reuse the same `openai` package with just a different `base_url`. One-line swap to switch back if needed.

---

### **3.4 - RAG Pipeline Orchestrator**

**What we built (`app/backend/services/rag_pipeline.py`):**
- [x] `RAGPipeline` class that wires together all services
- [x] **Ingestion flow:** `ingest_document(filename)` → Parse → Chunk → Embed → Store
- [x] **Query flow:** `ask_question(question, filename?)` → Embed query → Retrieve top-k → LLM → Answer + Citations
- [x] Lazy LLM initialization (API key only needed at query time, not at startup)
- [x] `RAGResponse` dataclass: `answer`, `citations`, `source_chunks`, `model`, `tokens_used`, `processing_time`
- [x] `IngestionResult` dataclass: `filename`, `total_pages`, `total_chunks`, `embeddings_stored`, `processing_time`

**Verified:** 5/5 tests passing — ingestion flow, query with mocked LLM, validation, edge cases.

---

### **3.5 - `/ask` API Endpoint**

**What we built (`app/backend/routes/ask.py`):**
- [x] `POST /ask` — accepts `{"question": "...", "filename": "..."}`, returns full answer with citations
- [x] Response includes: `answer`, `citations[]` (page numbers + source file), `source_chunks[]` (text preview + similarity score), `model`, `tokens_used`, `processing_time`
- [x] Error handling: 400 for empty questions or no indexed documents, 500 for LLM failures

---

### **3.6 - Updated Process Endpoint**

**What changed (`app/backend/routes/process.py`):**
- [x] Now runs the **full ingestion pipeline** (not just parse + chunk)
- [x] Flow: PDF → Parse → Chunk → Embed → Store in ChromaDB
- [x] Returns `embeddings_stored` count and `processing_time_seconds`
- [x] After processing, the document is immediately ready for Q&A via `/ask`

---

### **3.7 - Streamlit Frontend (Q&A Enabled)**

**What changed (`app/frontend/streamlit_app.py`):**
- [x] Upload button now auto-processes (upload → parse → chunk → embed → store in one click)
- [x] **Q&A section enabled** — text input + "Get Answer" button
- [x] Answer display with:
  - 💡 Answer text (markdown)
  - 📖 Citation tags (page numbers with source file)
  - 📄 Expandable source chunks (text preview + similarity score)
  - Metadata footer (model, tokens, processing time)
- [x] Session state tracks processed files in the sidebar
- [x] Error handling for backend connection, empty questions, no indexed docs

---

### **3.8 - Configuration & Environment Updates**

**New settings added to `config.py`:**
```python
# Embeddings
embedding_model = "all-MiniLM-L6-v2"

# xAI / Grok LLM
xai_api_key = None          # Required for Q&A
xai_base_url = "https://api.x.ai/v1"
llm_model = "grok-3-mini"
llm_temperature = 0.2
llm_max_tokens = 1000

# Retrieval
top_k = 5

# ChromaDB (now with chroma_path property)
chroma_persist_dir = "data/processed/chroma"
```

**`.env.example` updated** — replaced `OPENAI_API_KEY` with `XAI_API_KEY` and all new vars.

---

### **3.9 - Week 3 Test Results**

**28 new tests, all passing:**

| Test Suite | Tests | Time | What's Tested |
|-----------|-------|------|---------------|
| `test_embedding_service.py` | 10/10 ✅ | 78s | Single/batch embedding, dimensions, consistency, empty input |
| `test_vector_store.py` | 13/13 ✅ | 33s | Add, query, top-k, metadata, filtering, upsert, delete, list |
| `test_rag_pipeline.py` | 5/5 ✅ | 33s | Ingestion flow, query with mocked LLM, validation, edge cases |

**Total tests in project: 50 (22 from Week 2 + 28 from Week 3)**

---

## ✅ Week 4: Polish & Deploy (COMPLETE)

### **4.1 - Multi-Document Support**

**What we built:**
- [x] Document selector dropdown in the Streamlit Q&A section ("📚 All Documents" or a specific PDF)
- [x] Selected filename (or `None` for all) is passed in the `/ask` POST body as `filename`
- [x] Each Q&A history card shows a badge indicating which document was searched
- [x] Backend already supported `filename` filtering via ChromaDB — this was purely a frontend + UX addition

**Why this matters:** Users working with multiple PDFs can now pin their question to a specific document or search across all of them at once.

---

### **4.2 - Conversation History & Follow-Up Questions**

**What we built:**
- [x] `conversation_history` parameter added to `LLMClient.generate_answer()` — injects prior Q&A turns as alternating user/assistant messages
- [x] History capped at last 6 turns to stay within LLM token limits (`MAX_HISTORY_TURNS = 6`)
- [x] `conversation_history` flows through: `AskRequest` → `RAGPipeline.ask_question()` → `LLMClient.generate_answer()` → OpenAI messages array
- [x] Streamlit builds `history_payload` from `st.session_state.qa_history` and passes it with every `/ask` call
- [x] System prompt updated with Rule 7: use conversation history to understand follow-up questions

**Why this matters:** Users can now ask follow-ups like *"Elaborate on point 3"* or *"What about the conclusion?"* and the LLM understands the prior context.

---

### **4.3 - Docker Deployment**

**What we built:**
- [x] `Dockerfile` — Python 3.11-slim backend image running `uvicorn` on port 8000
- [x] `Dockerfile.frontend` — Python 3.11-slim frontend image running `streamlit` on port 8501
- [x] `.dockerignore` — excludes `data/`, `.env`, `venv/`, `.git/`, notebooks from build context
- [x] `docker-compose.yml` fully wired:
  - `backend` service with health check (`/health` endpoint, 30s start_period)
  - `frontend` service waits for backend via `depends_on: condition: service_healthy`
  - `BACKEND_URL=http://backend:8000` injected via Docker internal networking
  - `./data` mounted as a volume (ChromaDB + uploads persist across restarts)
  - `restart: unless-stopped` on both services
- [x] `BACKEND_URL` in `streamlit_app.py` now reads from `os.environ` (falls back to `localhost:8000` for local dev)

**Usage:**
```bash
docker compose up --build   # First time
docker compose up -d         # Subsequent runs (detached)
docker compose down          # Stop
```

---

### **4.4 - Week 4 What I Learned**

- **Multi-doc was already 80% done** — the vector store's `filename` filter was built in Week 3. The entire Week 4 addition was a frontend selectbox and passing the field in the payload. Good architecture pays off.
- **Conversation history in LLMs requires careful token budgeting.** Capping at 6 turns prevents the context window from overflowing on longer conversations, especially with dense document context blocks.
- **Docker's `depends_on: condition: service_healthy` is essential** — without it, Streamlit tries to connect to FastAPI before it finishes loading the embedding model, causing cryptic errors.
- **`.dockerignore` matters more than people think** — without it, Docker copies the entire `data/` directory (which can be gigabytes of ChromaDB vectors) into the build context, making builds extremely slow.
- **`os.environ.get("BACKEND_URL", "http://localhost:8000")`** is the standard pattern for making a service work both locally and in Docker without code changes.

---


### **What's Working:**
✅ PDF upload via Streamlit UI  
✅ FastAPI backend with health monitoring  
✅ PDF text extraction (PyMuPDF) with page-level metadata  
✅ Text chunking (LangChain) with page-number tracking across boundaries  
✅ **Embedding generation (Sentence Transformers, `all-MiniLM-L6-v2`, 384-dim)**  
✅ **Vector storage & retrieval (ChromaDB, cosine similarity, persistent)**  
✅ **LLM answer generation (Grok/xAI, citation-focused prompting)**  
✅ **Full RAG pipeline (ingest + query) orchestrated end-to-end**  
✅ **`POST /ask` endpoint with structured response (answer + citations + sources)**  
✅ **Streamlit Q&A interface with citation tags and expandable source chunks**  
✅ **50 tests passing across 6 test files**  

### **API Endpoints:**
```
GET  /health                — Service health check
POST /upload                — Upload a PDF document
POST /process/{filename}    — Full ingestion: parse → chunk → embed → store
POST /ask                   — Ask a question, get answer with citations
GET  /docs                  — Auto-generated API documentation
```

### **What's Next (Week 4 — Polish & Deploy):**
⏳ UI improvements and error handling polish  
⏳ Include citations with page numbers in answers (FR-10) — further refinement  
⏳ Display answers in a user-friendly web UI (FR-11) — further polish  
⏳ Support multiple document uploads (FR-12)  
⏳ Docker deployment  
⏳ Final testing and demo  

---

## 🔍 Technical Decisions Made

### **1. Why Grok (xAI) instead of OpenAI?**
- User preference — wanted to use Grok for the LLM component
- The xAI API is **OpenAI SDK-compatible** — same `openai` Python package, just change `base_url`
- Default model: `grok-3-mini` (fast, cost-effective)
- One-line change to swap to OpenAI/GPT if needed later

### **2. Why ChromaDB?**
- Lightweight, embedded vector database (no separate server)
- Python-native, easy local development
- Built-in persistent storage to disk
- Cosine similarity search out of the box
- Simple enough for a learning project, powerful enough for demo scale

### **3. Why Sentence Transformers (`all-MiniLM-L6-v2`)?**
- Small model (~80 MB), runs fast on CPU
- 384-dimensional embeddings — good quality/speed trade-off
- Standard choice for local RAG projects
- No GPU required for embedding (saves resources for LLM)
- Lazy loading — model downloads on first use, not at import

### **4. Why lazy initialization everywhere?**
- Embedding model loads on first call (not at server startup)
- LLM client initializes on first query (API key only needed then)
- This means `uvicorn` starts instantly — no 30s wait for model loading
- Tests can run without downloading models for unrelated test suites

### **5. Why upsert in ChromaDB?**
- Re-processing the same PDF updates existing embeddings rather than duplicating
- Users can safely click "Upload & Process" multiple times
- No need for a separate "delete then re-add" workflow

### **6. Why auto-process on upload in the frontend?**
- One-click workflow: upload → parse → chunk → embed → store
- Simpler UX — users don't need to know about the processing step
- The backend still exposes `/process` as a separate endpoint for API users

---

## 📊 Data Flow

```
INGESTION (POST /process/{filename}):
  PDF → Parse (PyMuPDF) → Chunk (LangChain, 1000 chars, 200 overlap)
      → Embed (Sentence Transformers, 384-dim) → Store (ChromaDB, cosine)

QUERY (POST /ask):
  Question → Embed (same model) → Retrieve top-5 (ChromaDB)
           → Build prompt (system + context + question)
           → Grok (xAI API) → Answer + [Page X] citations
```

---

## 📝 What I Learned

### **Week 1:**
- Setting up a clean project structure early saves a lot of time later.
- FastAPI's auto-generated OpenAPI docs (`/docs`) make testing endpoints very easy.
- Using `pydantic-settings` for configuration keeps environment management clean and type-safe.
- Separating routes into individual files keeps the codebase modular and readable.

### **Week 2:**
- **PyMuPDF (`fitz`)** is extremely fast for PDF text extraction — it handles page-level access natively, which is essential for building citation features later.
- **Page-number tracking through the chunking process** was the trickiest part. Since chunks can straddle page boundaries (due to overlap), I had to build a character-offset mapping to trace each chunk back to its source page(s).
- **LangChain's `RecursiveCharacterTextSplitter`** is smart about splitting — it tries paragraph and sentence boundaries before falling back to character-level splits.
- Choosing the right **chunk size and overlap** is a design trade-off: smaller chunks = more precise retrieval but lose context; larger chunks = preserve context but may dilute relevance.
- Writing tests *alongside* the code caught edge cases early — empty PDFs, single-chunk documents, page boundary tracking.

### **Week 3:**
- **The xAI API being OpenAI SDK-compatible** is a huge win — switching LLM providers is literally changing `base_url` and `api_key`. The abstraction layer in the OpenAI SDK handles the rest.
- **Lazy initialization is critical for developer experience.** Without it, every `uvicorn --reload` would download/load the 80 MB embedding model. With it, the server starts in <1 second.
- **Prompt engineering matters more than model size** for citation quality. The system prompt explicitly instructs `[Page X]` format, "only answer from context," and "say I don't know if unsure" — this grounds the LLM much more than raw retrieval alone.
- **ChromaDB's upsert** saves a lot of complexity. Without it, I'd need duplicate detection, delete-before-insert logic, and state tracking. With it, re-processing is idempotent.
- **Mocking the LLM in tests** is essential — RAG pipeline tests shouldn't require an API key or hit a real endpoint. The `unittest.mock.patch` pattern keeps tests fast and CI-friendly.

---

## 📈 Progress Timeline

| Date | Milestone | Status |
|------|-----------|--------|
| Week 1 | Project structure, README, design doc | ✅ Done |
| Week 1 | FastAPI scaffold + health/upload endpoints | ✅ Done |
| Week 1 | Streamlit frontend (upload only) | ✅ Done |
| Week 1 | Configuration, logging, Docker scaffold | ✅ Done |
| Week 2 | PDF parser service (PyMuPDF) | ✅ Done |
| Week 2 | Text chunker service (LangChain) | ✅ Done |
| Week 2 | Process endpoint (parse → chunk) | ✅ Done |
| Week 2 | 22 unit tests (parser + chunker) | ✅ Done |
| **Week 3** | **Embedding service (Sentence Transformers)** | ✅ Done |
| **Week 3** | **Vector store (ChromaDB)** | ✅ Done |
| **Week 3** | **LLM client (Grok/xAI)** | ✅ Done |
| **Week 3** | **RAG pipeline orchestrator** | ✅ Done |
| **Week 3** | **`POST /ask` endpoint** | ✅ Done |
| **Week 3** | **Streamlit Q&A enabled (citations + sources)** | ✅ Done |
| **Week 3** | **28 new tests (embedding + vector store + pipeline)** | ✅ Done |
| **Week 4** | **Multi-document support (UI selector + filename filter)** | ✅ Done |
| **Week 4** | **Conversation history (follow-up Q&A, last 6 turns)** | ✅ Done |
| **Week 4** | **Docker deployment (Dockerfile + Dockerfile.frontend + compose)** | ✅ Done |

---

## 🎓 Deliverables Checklist

### Week 1 (Foundation) — 12/12 ✅
- [x] Project repository on GitHub
- [x] Clean folder structure
- [x] README with architecture overview
- [x] Design document (requirements, tech choices, risks, timeline)
- [x] FastAPI backend with CORS and lifecycle
- [x] `GET /health` endpoint
- [x] `POST /upload` endpoint
- [x] Streamlit frontend with file upload
- [x] Structured logging
- [x] Environment-based configuration (`pydantic-settings`)
- [x] `requirements.txt` with all dependencies
- [x] `docker-compose.yml` placeholder

### Week 2 (PDF Processing) — 7/7 ✅
- [x] `PDFParser` service (PyMuPDF)
- [x] `TextChunker` service (LangChain)
- [x] Page-number tracking across chunk boundaries
- [x] `POST /process/{filename}` endpoint
- [x] `PageContent` and `DocumentChunk` dataclasses
- [x] Chunk size/overlap configuration
- [x] 22 unit tests passing

### Week 3 (RAG Pipeline) — 10/10 ✅
- [x] `EmbeddingService` (Sentence Transformers, `all-MiniLM-L6-v2`)
- [x] `VectorStoreService` (ChromaDB, persistent, cosine similarity)
- [x] `LLMClient` (Grok/xAI via OpenAI SDK)
- [x] `RAGPipeline` orchestrator (ingestion + query flows)
- [x] `POST /ask` endpoint
- [x] Updated `/process` with full ingestion (embed + store)
- [x] Streamlit Q&A section enabled (answer + citations + source chunks)
- [x] Config updated (xAI key, embedding model, LLM settings, top_k)
- [x] `.env.example` updated
- [x] 28 new tests passing (50 total)

### Week 4 (Polish & Deploy) — 7/7 ✅
- [x] Multi-document UI selector (document scoped or all-docs search)
- [x] Selected document badge shown on each Q&A turn
- [x] `conversation_history` in `LLMClient.generate_answer()` (multi-turn)
- [x] `conversation_history` in `RAGPipeline.ask_question()` (pass-through)
- [x] `conversation_history` in `AskRequest` + `/ask` endpoint
- [x] Streamlit sends history payload from `qa_history` session state
- [x] `Dockerfile` + `Dockerfile.frontend` + `.dockerignore` + wired `docker-compose.yml`

**Overall: 36/36 deliverables complete (100%)**

---

## 💡 Key Takeaways

1. **Foundation work is invisible but critical.** Clean project structure, configuration management, and testing setup in Week 1 made Weeks 2-3 much faster.

2. **Page-number tracking is the unsung hero.** Without the character-offset mapping built in Week 2, the citation system in Week 3 wouldn't work.

3. **Lazy initialization is a developer experience multiplier.** Server starts instantly, tests run without model downloads, and CI stays fast.

4. **The RAG pipeline is only as good as its prompt.** Retrieval gets you 70% there; the system prompt (cite pages, stay grounded, admit ignorance) handles the other 30%.

5. **API compatibility is a strategic advantage.** The OpenAI SDK's `base_url` parameter means switching between Grok, OpenAI, Azure, or local LLMs is a config change, not a rewrite.

---

## 📞 Project Info

**Author:** Aaryan Godara  
**GitHub:** [github.com/aaryan-godara/DocPilot](https://github.com/aaryan-godara/DocPilot)  
**License:** MIT  

**Course Context:** Foundations of Applied Machine Learning (Segment 3, Problem I2: Document Q&A / RAG)

---

**End of Progress Summary**  
*Week 3 complete — DocPilot now has a fully working RAG pipeline: upload a PDF, process it (parse → chunk → embed → store), ask questions, and get answers with page citations powered by Grok. 50 tests passing. Next up: Week 4 polish and Docker deployment.*
