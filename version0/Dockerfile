FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common wget ca-certificates gnupg2 lsb-release \
    build-essential curl git unzip locales \
    python3.9 python3.9-venv python3.9-dev python3-pip \
    libglib2.0-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6 \
    libnss3 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libxfixes3 libdrm2 libgbm1 libxshmfence1 libasound2 libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

RUN python3.9 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV INSTALL_BASE=/tmp/inscopix \
    ISX_API_DIR="" \
    LOCAL_EDITABLE_DIR="" \
    EXPECTED_OUTPUT_FILE=/output/done.marker

ENTRYPOINT ["/app/entrypoint.sh"]
