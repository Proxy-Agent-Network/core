# Stage 1: The Builder (Compiles Rust)
FROM python:3.11-slim as builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (The "Muscle")
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Maturin (The Bridge Builder)
RUN pip install maturin

# Copy ONLY the Rust core first (for caching)
WORKDIR /build
COPY proxy-core /build/proxy-core

# Build the Python Extension Wheel
WORKDIR /build/proxy-core
# We build for release to get maximum speed
RUN maturin build --release --strip

# --------------------------------------------------------

# Stage 2: The Runner (Slim & Fast)
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (OpenCV needed for OCR tasks)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY backend/requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# --- CRITICAL STEP: Install the Compiled Rust Core ---
# We copy the built "wheel" from the builder stage and install it
COPY --from=builder /build/proxy-core/target/wheels/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Copy the actual application code
COPY . .

# Launch the Hybrid Node
CMD ["python", "app.py"]