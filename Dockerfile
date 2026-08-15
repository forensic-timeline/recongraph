FROM python:3.13-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md LICENSE ./
RUN mkdir recongraph && touch recongraph/__init__.py
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /install /usr/local
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    wget \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY recongraph/ ./recongraph/
RUN pip install --no-cache-dir -e .

# Get Core Sigma Package 
RUN wget https://github.com/SigmaHQ/sigma/releases/download/r2026-01-01/sigma_core.zip -O /tmp/sigma.zip && \
    unzip /tmp/sigma.zip -d /tmp && \
    mkdir -p /app/sigma && \
    mv /tmp/rules/* /app/sigma/ && \
    rm -rf /tmp/sigma.zip /tmp/rules /tmp/version.txt

ENV SIGMA_RULES_PATH=/app/sigma

RUN mkdir -p /app/data
WORKDIR /app/data
ENTRYPOINT ["recongraph"]