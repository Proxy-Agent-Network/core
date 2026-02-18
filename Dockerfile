# STAGE 1: The Factory (Compiles Rust Hardware Bridge)
# ----------------------------------------------------
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

# Install Maturin (Rust-to-Python compiler)
RUN pip install maturin

# Copy and compile the Rust core
WORKDIR /build
COPY proxy-core /build/proxy-core
WORKDIR /build/proxy-core
RUN maturin build --release --strip

# STAGE 2: The Agent (Runs the App + Lightning)
# ----------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- NEW: Install gRPC Tools for Lightning ---
RUN pip install grpcio grpcio-tools googleapis-common-protos requests

# --- NEW: Download & Compile LND Definitions (Fixed) ---
# We use Python to fetch the file because 'curl' can fail on GitHub redirects
RUN python -c "import requests; open('rpc.proto', 'wb').write(requests.get('https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto').content)"

# Compile the .proto file into python modules
RUN python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. rpc.proto

# Copy the compiled Rust Binary from Stage 1
COPY --from=builder /build/proxy-core/target/wheels/*.whl /tmp/
RUN pip install /tmp/*.whl && rm /tmp/*.whl

# Copy the Application Code
COPY . .

# Run the Agent
EXPOSE 5000
CMD ["python", "app.py"]