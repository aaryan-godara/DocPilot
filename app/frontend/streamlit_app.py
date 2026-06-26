"""
AskMyBook — Streamlit Frontend

A clean web interface for uploading PDF documents and (in future weeks)
asking questions about their content.

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
    page_title="AskMyBook",
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# Sidebar
# ==================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/book.png", width=80)
    st.title("📚 AskMyBook")
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

    st.markdown("---")
    st.markdown(
        "<small>Built with ❤️ using FastAPI + Streamlit</small>",
        unsafe_allow_html=True,
    )

# ==================================================
# Main Content
# ==================================================
st.markdown('<p class="main-header">📚 AskMyBook</p>', unsafe_allow_html=True)
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

    # Upload button
    if st.button("⬆️ Upload to Server", type="primary", use_container_width=True):
        with st.spinner("Uploading..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ **Uploaded successfully!**")
                    st.markdown(f"- **Filename:** `{result['filename']}`")
                    st.markdown(f"- **Size:** {int(result.get('size_bytes', 0)) / 1024:.1f} KB")
                    st.markdown(f"- **Status:** {result['status']}")
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Upload failed: {error_detail}")

            except requests.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# --- Q&A Section (Placeholder) ---
st.markdown("---")
st.markdown("### ❓ Ask a Question")
st.text_input(
    "Type your question here",
    placeholder="What is this document about?",
    disabled=True,
    help="🔒 Q&A will be enabled in Week 3 when the RAG pipeline is complete.",
)
st.caption("🚧 *Question answering will be available after the RAG pipeline is implemented (Week 3).*")
