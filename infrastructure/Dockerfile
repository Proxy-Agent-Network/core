# infrastructure/Dockerfile

# Use a lightweight Python base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# 1. Install System Dependencies
# FIX: Replaced deprecated 'libgl1-mesa-glx' with 'libgl1' for Debian Trixie support
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 3. Copy the Entire Application
COPY . /app

# 4. Network & Environment
EXPOSE 5000

# 5. The Launch Command
CMD ["python", "app.py"]