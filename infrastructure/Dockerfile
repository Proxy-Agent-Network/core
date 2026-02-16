# Proxy Protocol Physical Node - Reference Implementation
# Base image: Lightweight Python for IoT/Edge devices
FROM python:3.11-slim-buster

# Set Metadata
LABEL maintainer="engineering@proxy.agent.network"
LABEL version="1.0.0"
LABEL description="Official container for running a Proxy Protocol Physical Verification Node"

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROXY_ENV=production

# Install System Dependencies (TPM2 tools, Tesseract OCR, ZBar for QR)
RUN apt-get update && apt-get install -y \
    tpm2-tools \
    libtpm2-pkcs11-1 \
    tesseract-ocr \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*

# Set Work Directory
WORKDIR /app

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Source Code
COPY . .

# Create non-root user for security
RUN useradd -m proxyuser && chown -R proxyuser:proxyuser /app
USER proxyuser

# Expose Metrics Port
EXPOSE 9090

# Entrypoint: Start the Node Daemon
CMD ["python", "node_daemon.py"]
