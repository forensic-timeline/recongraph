# 1. Define the builder image
FROM python:3.13-slim AS builder

# 2. Set working directory
WORKDIR /app

# 3. Install system dependencies for python build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy metadata files
COPY pyproject.toml README.md LICENSE ./

# 5. Create skeleton to cache dependencies
RUN mkdir recongraph && touch recongraph/__init__.py

# 6. Install dependencies into a separate prefix to cache heavy dependencies
RUN pip install --no-cache-dir --prefix=/install .

# 7. Define runtime python image
FROM python:3.13-slim

# 8. Set working directory
WORKDIR /app

# 9. Copy the installed libraries from the builder 
COPY --from=builder /install /usr/local

# 10. Install runtime-only system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    wget \
    ca-certificates \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 11. Copy actual source code and metadata
COPY pyproject.toml README.md LICENSE ./
COPY recongraph/ ./recongraph/

# 12. Install the package (linking the source code)
RUN pip install --no-cache-dir -e .

# 13. Get Core Sigma Package 
RUN wget https://github.com/SigmaHQ/sigma/releases/download/r2026-01-01/sigma_core.zip -O /tmp/sigma.zip && \
    unzip /tmp/sigma.zip -d /tmp && \
    mkdir -p /app/sigma && \
    mv /tmp/rules/* /app/sigma/ && \
    rm -rf /tmp/sigma.zip /tmp/rules /tmp/version.txt

# 14. Set default sigma path
ENV SIGMA_RULES_PATH=/app/sigma

# 15. Create data directory and set it as final WORKDIR
RUN mkdir -p /app/data
WORKDIR /app/data

# 16. Set entrypoint for docker
ENTRYPOINT ["recongraph"]