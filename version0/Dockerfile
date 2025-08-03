FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies needed for the ISX Python API (numeric libs) and Python itself
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      python3.9 python3.9-venv python3-pip python3.9-dev \
      build-essential \
      tar gzip coreutils procps \
      liblapack3 libblas3 libopenblas-base libatlas-base-dev \
      libgfortran5 libgl1 libx11-6 libxrender1 \
      libglib2.0-0 && \
    ln -sf /usr/bin/python3.9 /usr/bin/python && \
    python -m pip install --upgrade pip setuptools wheel && \
    rm -rf /var/lib/apt/lists/*

# App dir
RUN mkdir -p /app
WORKDIR /app

# Copy entrypoint and bootstrap (you can also mount bootstrap.py instead)
COPY entrypoint.sh /app/entrypoint.sh
COPY bootstrap.py /app/bootstrap.py

RUN chmod +x /app/entrypoint.sh

# Default command is the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
