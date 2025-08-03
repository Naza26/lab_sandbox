FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Prep: ensure basic tools and add-apt-repository
RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common wget ca-certificates gnupg2 lsb-release && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

# Install Python 3.9 and required system libraries with a simple retry loop
RUN set -e; \
    for i in 1 2 3; do \
        apt-get install -y --no-install-recommends \
          python3.9 python3.9-venv python3.9-dev python3-pip \
          build-essential \
          tar gzip coreutils procps \
          liblapack3 libblas3 libopenblas-base libatlas-base-dev \
          libgfortran5 libgl1 libx11-6 libxrender1 libglib2.0-0 && break || \
        (echo "apt install failed, retrying ($i)..." && sleep 2); \
    done

# Symlink python to python3.9 and upgrade pip tooling
RUN ln -sf /usr/bin/python3.9 /usr/bin/python && \
    python -m pip install --upgrade pip setuptools wheel

# Clean up apt cache
RUN rm -rf /var/lib/apt/lists/*

# App directory
RUN mkdir -p /app
WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
COPY bootstrap.py /app/bootstrap.py

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
