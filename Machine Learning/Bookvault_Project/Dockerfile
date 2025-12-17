# ============================================================================
# BookVault - Production Docker Image
# Optimized slim build with security best practices
# ============================================================================

FROM python:3.13-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies (including Tesseract OCR for image search)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 bookvault && \
    chown -R bookvault:bookvault /app

# Switch to non-root user
USER bookvault

# Copy requirements first for better layer caching
COPY --chown=bookvault:bookvault requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code
COPY --chown=bookvault:bookvault . .

# Create necessary directories
RUN mkdir -p logs

# Set Python path to include user site-packages
ENV PATH="/home/bookvault/.local/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
CMD ["streamlit", "run", "Bookvault_UI/App_Pro.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]