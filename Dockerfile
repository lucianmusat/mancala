FROM arm32v7/python:3.10.14-slim
#FROM python:3.10.14-slim

WORKDIR /code

# Install system dependencies
RUN apt update && apt install -y curl build-essential

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Trunk
RUN cargo install trunk

# Install wasm32 target
RUN rustup target add wasm32-unknown-unknown

# Copy backend requirements and install Python dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy backend code
COPY ./*.py /code/

# Copy frontend code
COPY ./frontend /code/frontend

# Build frontend
WORKDIR /code/frontend
RUN cargo build --release
# RUN trunk build --release
RUN cargo install wasm-bindgen-cli --version 0.2.92 


# Move back to the main code directory
WORKDIR /code

# Copy a startup script
COPY start.sh /code/start.sh
RUN chmod +x /code/start.sh

ENTRYPOINT ["bash", "/code/start.sh"]
