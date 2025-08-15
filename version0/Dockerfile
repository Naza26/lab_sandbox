FROM python:3.9-slim

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# OS libs ISX typically needs
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git unzip locales \
    libglib2.0-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6 \
    libnss3 libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 \
    libxfixes3 libdrm2 libgbm1 libxshmfence1 libasound2 libglu1-mesa \
 && rm -rf /var/lib/apt/lists/*

# Optional venv; you can also just use /usr/local/bin/python directly
RUN python -m venv /opt/venv && /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel
ENV PATH="/opt/venv/bin:${PATH}"

# (Recommended) scientific deps ISX’s API often needs
RUN python -m pip install --no-cache-dir numpy scipy h5py pandas matplotlib

WORKDIR /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
