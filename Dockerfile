# STAGE 1: The Factory (Compiles Rust)
FROM python:3.11-slim as builder

# Install build tools
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Maturin
RUN pip install maturin

WORKDIR /build
COPY proxy-core /build/proxy-core
WORKDIR /build/proxy-core

# Compile the "Fortress"
RUN maturin build --release --strip

# -------------------------------------------

# STAGE 2: The Agent (Runs the App)
FROM python:3.11-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the compiled binary from Stage 1
COPY --from=builder /build/proxy-core/target/wheels/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]