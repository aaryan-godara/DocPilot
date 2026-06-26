"""
DocPilot — PDF Upload Endpoint

Handles PDF file uploads:
- Validates file extension (.pdf only)
- Saves to the configured upload directory (data/raw/)
- Returns upload confirmation with filename and path
"""

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.backend.config import get_settings
from app.utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__, level=settings.log_level)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, str]:
    """
    Upload a PDF document.

    Accepts a PDF file, validates the extension, and saves it
    to the upload directory (data/raw/).

    Args:
        file: The uploaded PDF file.

    Returns:
        JSON with filename, status, and storage path.

    Raises:
        HTTPException 400: If the file is not a PDF.
        HTTPException 500: If there is a server error during save.
    """
    # --- Validate file extension ---
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    if not file.filename.lower().endswith(".pdf"):
        logger.warning("Rejected non-PDF upload: %s", file.filename)
        raise HTTPException(
            status_code=400,
            detail=f"Only PDF files are accepted. Got: {file.filename}",
        )

    # --- Save file ---
    try:
        save_path: Path = settings.upload_path / file.filename
        contents = await file.read()

        with open(save_path, "wb") as f:
            f.write(contents)

        logger.info("✅ Uploaded: %s (%d bytes)", file.filename, len(contents))

        return {
            "filename": file.filename,
            "status": "uploaded",
            "path": str(save_path),
            "size_bytes": str(len(contents)),
        }

    except Exception as e:
        logger.error("❌ Upload failed for %s: %s", file.filename, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}",
        )

    finally:
        await file.close()
