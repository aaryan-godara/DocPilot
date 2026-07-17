# ==================================================
# DocPilot — Backend Dockerfile
# Runs the FastAPI server on port 8000
# ==================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system-level dependencies needed by PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer-cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project source
COPY . .

# Create data directories (ChromaDB persistence & uploads)
RUN mkdir -p data/raw data/processed/chroma data/sample

# Expose FastAPI port
EXPOSE 8000

# Run the backend
CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
