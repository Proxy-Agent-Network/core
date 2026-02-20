# STAGE 1: The Factory (Compiles Rust Hardware Bridge)
# ----------------------------------------------------
FROM python:3.11-slim as builder

# Install system build tools required for Rust
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev

# Install Rust toolchain
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Maturin (The bridge compiler between Rust and Python)
RUN pip install maturin

# Copy and compile the Rust core into a Python wheel
WORKDIR /build
# NOTE: Ensure the folder name here exactly matches your repo's Rust directory.
# Based on your previous file, it looks like it's looking for 'proxy-core'
COPY proxy-core /build/proxy-core
WORKDIR /build/proxy-core
RUN maturin build --release --strip

# STAGE 2: The Agent (Runs the App + Lightning)
# ----------------------------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# 1. Install System Dependencies (Includes our new libgl1 fix)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Install gRPC Tools for Lightning Network integration
RUN pip install grpcio grpcio-tools googleapis-common-protos requests

# 4. Download & Compile LND Definitions
# This fetches the Lightning API rules and compiles them into Python code
RUN python -c "import requests; open('rpc.proto', 'wb').write(requests.get('https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto').content)"
RUN python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. rpc.proto

# 5. Copy the compiled Rust Binary (.whl) from Stage 1 and install it
COPY --from=builder /build/proxy-core/target/wheels/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# 6. Copy the Application Code
COPY . /app

# Make the launch script executable
RUN chmod +x start_node.sh

# Run the Agent
EXPOSE 5000
EXPOSE 8000
CMD ["./start_node.sh"]