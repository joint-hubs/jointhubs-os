FROM python:3.11-slim

# System deps for hdbscan / umap-learn compilation and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download xx_ent_wiki_sm

# Copy application code
COPY . /app/thoughtmap/

# thoughtmap is a package at /app/thoughtmap/, so /app must be on PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 8585

HEALTHCHECK --interval=10s --timeout=3s --start-period=60s \
    CMD curl -sf http://localhost:8585/api/status || exit 1

CMD ["python", "-m", "thoughtmap", "server"]
