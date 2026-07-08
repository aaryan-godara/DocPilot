"""
DocPilot — FastAPI Application Entry Point

Creates and configures the FastAPI application with:
- CORS middleware for frontend communication
- Lifecycle management (startup/shutdown logging)
- Route registration for health and upload endpoints
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.config import get_settings
from app.backend.routes import ask, health, process, upload
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    logger.info("🚀 Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("📁 Upload directory: %s", settings.upload_path)
    logger.info("🔧 Debug mode: %s", settings.debug)
    yield
    logger.info("👋 Shutting down %s", settings.app_name)


# --- Create FastAPI App ---
app = FastAPI(
    title=settings.app_name,
    description="Ask questions about your PDF documents and get answers with citations.",
    version=settings.app_version,
    lifespan=lifespan,
)

# --- CORS Middleware ---
# Allow Streamlit frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(process.router, tags=["Processing"])
app.include_router(ask.router, tags=["Q&A"])


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint — redirects to API docs."""
    return {"message": f"Welcome to {settings.app_name}. Visit /docs for API documentation."}
