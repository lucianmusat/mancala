# ---------- Frontend build stage ----------
FROM rust:1.88-slim AS frontend-build
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config libssl-dev ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Use --locked so you get reproducible installs and avoid surprise dependency bumps
RUN cargo install trunk --locked \
 && rustup target add wasm32-unknown-unknown

COPY frontend ./frontend
WORKDIR /app/frontend
RUN trunk build --release


# ---------- Backend/runtime stage ----------
FROM python:3.10.14-slim AS runtime
WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /code/requirements.txt

COPY ./*.py /code/
COPY --from=frontend-build /app/frontend/dist /code/static

COPY start.sh /code/start.sh
RUN sed -i 's/\r$//' /code/start.sh  # might build on windows
RUN chmod +x /code/start.sh
RUN chmod +x /code/start.sh

ENTRYPOINT ["bash", "/code/start.sh"]
