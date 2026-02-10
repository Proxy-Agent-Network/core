# Proxy Protocol Physical Node - Official Docker Image
# Architecture: Multi-arch (supports amd64 and arm64/Raspberry Pi)
FROM python:3.11-slim-bookworm

# Metadata
LABEL org.opencontainers.image.source="https://github.com/Proxy-Agent-Network/core"
LABEL org.opencontainers.image.description="Physical Node Runtime with TPM 2.0 and OCR support"

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 1. Install Hardware & Vision Dependencies
# - tpm2-tools: For communicating with the Infineon crypto chip
# - tesseract-ocr: For reading physical mail
# - libgl1/libglib2.0: Required for OpenCV (Privacy Guard)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tpm2-tools \
    libtpm2-pkcs11-1 \
    tesseract-ocr \
    libzbar0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Application Directory
WORKDIR /app

# 3. Install Python Requirements
# Copy just the requirements first to cache the pip layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Install Proxy Node Code
COPY . .

# 5. Security: Create non-root user
# We need group 'plugdev' or 'tss' for TPM access depending on host rules
RUN useradd -m proxyuser && \
    usermod -aG plugdev proxyuser
USER proxyuser

# 6. Healthcheck
# Queries the local health endpoint to ensure the daemon is alive
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9090/health || exit 1

# 7. Start the Node Daemon
CMD ["python", "node_daemon.py"]
