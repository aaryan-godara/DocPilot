"""
DocPilot — Streamlit Frontend

A web interface for uploading PDF documents and asking questions
about their content. Gets answers with citations and page numbers.

Run with:
    streamlit run app/frontend/streamlit_app.py --server.port 8501
"""

import requests
import streamlit as st

# ==================================================
# Configuration
# ==================================================
BACKEND_URL = "http://localhost:8000"

# ==================================================
# Page Configuration
# ==================================================
st.set_page_config(
    page_title="DocPilot",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ==================================================
# Custom Styling
# ==================================================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #888;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .stFileUploader > div {
        padding: 1rem;
    }
    .citation-tag {
        display: inline-block;
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        border-radius: 4px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.85rem;
        color: #1565c0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Session State
# ==================================================
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# ==================================================
# Sidebar
# ==================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/book.png", width=80)
    st.title("📚 DocPilot")
    st.markdown("---")
    st.markdown("### About")
    st.markdown(
        "Upload PDF documents and ask questions. "
        "Get answers with **citations** and **page numbers**."
    )
    st.markdown("---")
    st.markdown("### Status")

    # Check backend health
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.success(f"✅ Backend: {health_data['status']}")
            st.caption(f"Version: {health_data.get('version', 'N/A')}")
        else:
            st.error("❌ Backend: Unhealthy")
    except requests.ConnectionError:
        st.warning("⚠️ Backend: Not connected")
        st.caption("Start the backend with:\n`uvicorn app.backend.main:app --reload`")

    # Show processed documents
    if st.session_state.processed_files:
        st.markdown("---")
        st.markdown("### 📂 Processed Documents")
        for fname in st.session_state.processed_files:
            st.caption(f"✅ {fname}")

    st.markdown("---")
    st.markdown(
        "<small>Built with ❤️ using FastAPI + Streamlit + Grok</small>",
        unsafe_allow_html=True,
    )

# ==================================================
# Main Content
# ==================================================
st.markdown('<p class="main-header">📚 DocPilot</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Upload a PDF and ask questions about its content</p>',
    unsafe_allow_html=True,
)

# --- File Upload Section ---
st.markdown("### 📄 Upload a Document")

uploaded_file = st.file_uploader(
    "Choose a PDF file",
    type=["pdf"],
    help="Upload a PDF document to ask questions about its content.",
)

if uploaded_file is not None:
    # Display file info
    st.info(f"📎 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    # Upload & Process button
    if st.button("⬆️ Upload & Process", type="primary", use_container_width=True):
        # Step 1: Upload
        with st.spinner("Uploading..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)

                if response.status_code != 200:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Upload failed: {error_detail}")
                    st.stop()

                result = response.json()
                st.success(f"✅ **Uploaded:** `{result['filename']}`")

            except requests.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )
                st.stop()
            except Exception as e:
                st.error(f"❌ Upload error: {str(e)}")
                st.stop()

        # Step 2: Process (parse → chunk → embed → store)
        with st.spinner("Processing PDF (parsing, chunking, embedding)... This may take a moment."):
            try:
                proc_response = requests.post(
                    f"{BACKEND_URL}/process/{uploaded_file.name}",
                    timeout=120,
                )

                if proc_response.status_code == 200:
                    proc_data = proc_response.json()
                    st.success(
                        f"✅ **Processed!** "
                        f"{proc_data['total_pages']} pages → "
                        f"{proc_data['total_chunks']} chunks → "
                        f"{proc_data['embeddings_stored']} embeddings "
                        f"({proc_data['processing_time_seconds']:.1f}s)"
                    )
                    # Track processed files
                    if uploaded_file.name not in st.session_state.processed_files:
                        st.session_state.processed_files.append(uploaded_file.name)
                else:
                    error_detail = proc_response.json().get("detail", "Unknown error")
                    st.error(f"❌ Processing failed: {error_detail}")

            except requests.ConnectionError:
                st.error("❌ Lost connection to backend during processing.")
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")

# --- Q&A Section ---
st.markdown("---")
st.markdown("### ❓ Ask a Question")

question = st.text_input(
    "Type your question here",
    placeholder="What is this document about?",
    help="Ask any question about the uploaded and processed documents.",
)

if question:
    if st.button("🔍 Get Answer", type="primary", use_container_width=True):
        with st.spinner("Thinking... (embedding → retrieving → generating)"):
            try:
                ask_response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": question},
                    timeout=60,
                )

                if ask_response.status_code == 200:
                    data = ask_response.json()

                    # Display the answer
                    st.markdown("#### 💡 Answer")
                    st.markdown(data["answer"])

                    # Display citations
                    if data.get("citations"):
                        st.markdown("#### 📖 Citations")
                        citation_html = ""
                        seen_pages = set()
                        for cite in data["citations"]:
                            for page in cite["page_numbers"]:
                                if page not in seen_pages:
                                    seen_pages.add(page)
                                    citation_html += (
                                        f'<span class="citation-tag">'
                                        f"Page {page} — {cite['source_file']}"
                                        f"</span> "
                                    )
                        st.markdown(citation_html, unsafe_allow_html=True)

                    # Display source chunks in expandable sections
                    if data.get("source_chunks"):
                        st.markdown("#### 📄 Source Chunks")
                        for i, chunk in enumerate(data["source_chunks"], 1):
                            pages_str = ", ".join(str(p) for p in chunk["page_numbers"])
                            similarity = chunk["similarity_score"]
                            with st.expander(
                                f"Chunk {i} — Pages {pages_str} "
                                f"(similarity: {similarity:.2%})"
                            ):
                                st.markdown(chunk["text_preview"])
                                st.caption(
                                    f"Source: {chunk['source_file']} | "
                                    f"ID: {chunk['chunk_id']}"
                                )

                    # Metadata
                    st.caption(
                        f"Model: {data['model']} | "
                        f"Tokens: {data['tokens_used']} | "
                        f"Time: {data['processing_time_seconds']:.1f}s"
                    )

                elif ask_response.status_code == 400:
                    error_detail = ask_response.json().get("detail", "Unknown error")
                    st.warning(f"⚠️ {error_detail}")
                else:
                    error_detail = ask_response.json().get("detail", "Unknown error")
                    st.error(f"❌ Error: {error_detail}")

            except requests.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend. "
                    "Make sure the FastAPI server is running."
                )
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

