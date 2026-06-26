# DocPilot — Design Document

> **Version:** 1.0  
> **Last Updated:** 2025-01-01  
> **Status:** Draft  

---

## 1. Problem

Users frequently need to extract specific information from lengthy PDF documents — research papers, textbooks, legal documents, manuals, and reports. Manual searching is:

- **Time-consuming:** Scrolling through hundreds of pages for a single fact.
- **Error-prone:** Important details are easily missed.
- **Repetitive:** The same document is re-read for different questions.

### Proposed Solution

Build a **Retrieval-Augmented Generation (RAG)** application that:
1. Accepts PDF uploads from users.
2. Parses, chunks, and embeds document content.
3. Stores embeddings in a vector database.
4. Retrieves the most relevant chunks for a given question.
5. Generates a natural-language answer with **citations and page numbers**.

---

## 2. Users

| User Persona | Description | Key Needs |
|--------------|-------------|-----------|
| **Student** | Studying from textbooks or research papers | Quick answers, page references for deeper reading |
| **Researcher** | Reviewing literature or technical reports | Accurate citations, multi-document support |
| **Professional** | Working with contracts, manuals, or policies | Precise answers, auditability of sources |
| **Developer** | Testing and evaluating RAG systems | API access, configuration flexibility |

### User Stories

1. *As a student, I want to upload my textbook PDF and ask questions so I can study more efficiently.*
2. *As a researcher, I want to get answers with page numbers so I can verify the source.*
3. *As a developer, I want a health check endpoint so I can monitor the service.*

---

## 3. Functional Requirements

| ID | Requirement | Priority | Week |
|----|-------------|----------|------|
| FR-01 | Upload PDF documents via web UI | **Must Have** | 1 |
| FR-02 | Store uploaded PDFs on the server | **Must Have** | 1 |
| FR-03 | Health check API endpoint | **Must Have** | 1 |
| FR-04 | Parse and extract text from PDFs | **Must Have** | 2 |
| FR-05 | Chunk text with configurable size and overlap | **Must Have** | 2 |
| FR-06 | Generate embeddings for document chunks | **Must Have** | 2 |
| FR-07 | Store embeddings in a vector database | **Must Have** | 3 |
| FR-08 | Retrieve top-k relevant chunks for a query | **Must Have** | 3 |
| FR-09 | Generate answers using an LLM | **Must Have** | 3 |
| FR-10 | Include citations with page numbers in answers | **Must Have** | 4 |
| FR-11 | Display answers in a user-friendly web UI | **Must Have** | 4 |
| FR-12 | Support multiple document uploads | **Nice to Have** | 4 |
| FR-13 | Conversation follow-up questions | **Nice to Have** | Future |

---

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | **Response Time** | Answer generation < 10 seconds |
| NFR-02 | **Availability** | Service uptime via health checks |
| NFR-03 | **Scalability** | Support PDFs up to 50 MB |
| NFR-04 | **Security** | API key management via environment variables |
| NFR-05 | **Maintainability** | Modular architecture, type hints, PEP 8 |
| NFR-06 | **Portability** | Docker containerization |
| NFR-07 | **Testability** | Unit tests for critical paths |
| NFR-08 | **Logging** | Structured logging at all layers |

---

## 5. Architecture

### High-Level Architecture

```
┌──────────────┐     HTTP      ┌──────────────┐
│   Streamlit  │ ────────────▶ │   FastAPI     │
│   Frontend   │ ◀──────────── │   Backend     │
└──────────────┘               └──────┬───────┘
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼           ▼
                    ┌──────────┐ ┌──────────┐ ┌──────────┐
                    │  PDF     │ │  Vector  │ │  LLM     │
                    │  Parser  │ │  Store   │ │  Client  │
                    └──────────┘ └──────────┘ └──────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Streamlit Frontend** | File upload, question input, answer display |
| **FastAPI Backend** | REST API, request routing, business logic |
| **PDF Parser** | Text extraction from uploaded PDFs |
| **Chunker** | Split text into overlapping segments |
| **Embedding Engine** | Generate vector representations of text |
| **Vector Store** | Store and retrieve embeddings by similarity |
| **LLM Client** | Send prompts to OpenAI, parse responses |
| **Citation Engine** | Map retrieved chunks back to page numbers |

### Data Flow

```
Upload Flow:  PDF → Parse → Chunk → Embed → Store
Query Flow:   Question → Embed → Retrieve → LLM → Answer + Citations
```

---

## 6. Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Language** | Python 3.10+ | ML ecosystem, type hints, async support |
| **API Framework** | FastAPI | Async, auto-docs (OpenAPI), type validation |
| **Frontend** | Streamlit | Rapid prototyping, built-in widgets for ML apps |
| **PDF Parser** | PyMuPDF (fitz) | Fast, accurate text extraction with page metadata |
| **Chunking** | LangChain RecursiveCharacterTextSplitter | Configurable size/overlap, respects text boundaries |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) | Open-source, runs locally, good quality/speed ratio |
| **Vector DB** | ChromaDB | Lightweight, Python-native, easy local development |
| **LLM** | OpenAI GPT-3.5/4 via SDK | High-quality generation, well-documented API |
| **Containerization** | Docker + Compose | Reproducible environments, multi-service orchestration |

### Alternatives Considered

| Decision | Alternative | Why Not |
|----------|------------|---------|
| Vector DB | Pinecone, Weaviate | Heavier setup; ChromaDB is simpler for a learning project |
| Frontend | React | Slower to build; Streamlit is purpose-built for ML demos |
| LLM | Local LLaMA | Higher resource requirements; OpenAI is more accessible |

---

## 7. Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **OpenAI API costs** | Medium | High | Use GPT-3.5-turbo, set token limits, cache responses |
| **Poor retrieval quality** | High | Medium | Tune chunk size/overlap, experiment with embedding models |
| **Large PDF handling** | Medium | Medium | Set file size limits, async processing |
| **API rate limits** | Low | Medium | Implement retry logic with exponential backoff |
| **Scope creep** | High | High | Strict weekly milestones, MVP-first approach |
| **ChromaDB scalability** | Low | Low | Sufficient for demo; migrate to Pinecone if needed |

---

## 8. Timeline

| Week | Focus Area | Deliverables |
|------|-----------|--------------|
| **Week 1** | Project Setup | Repository, documentation, FastAPI + Streamlit scaffold, upload endpoint |
| **Week 2** | PDF Processing | PDF parsing, text chunking, embedding generation, initial vector storage |
| **Week 3** | RAG Pipeline | Retriever integration, LLM prompting, answer generation with citations |
| **Week 4** | Polish & Deploy | UI improvements, error handling, testing, Docker deployment, demo |

### Weekly Checkpoints

- **End of Week 1:** Working upload system, professional repo.
- **End of Week 2:** PDF → embeddings pipeline functional.
- **End of Week 3:** End-to-end Q&A with citations.
- **End of Week 4:** Production-ready demo with Docker.

---

## Appendix

### API Endpoints (Planned)

| Method | Endpoint | Description | Week |
|--------|----------|-------------|------|
| `GET` | `/health` | Service health check | 1 |
| `POST` | `/upload` | Upload a PDF document | 1 |
| `POST` | `/ask` | Ask a question about uploaded documents | 3 |
| `GET` | `/documents` | List uploaded documents | 2 |
| `DELETE` | `/documents/{id}` | Delete a document | 4 |

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_SIZE` | 1000 | Characters per text chunk |
| `CHUNK_OVERLAP` | 200 | Overlap between consecutive chunks |
| `TOP_K` | 5 | Number of retrieved chunks |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence Transformer model |
| `LLM_MODEL` | `gpt-3.5-turbo` | OpenAI model for generation |
| `MAX_UPLOAD_SIZE` | 50 MB | Maximum PDF file size |
