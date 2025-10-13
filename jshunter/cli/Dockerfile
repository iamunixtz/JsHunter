# Dockerfile for JSHunter CLI Tool - Enhanced High-Performance Version
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the enhanced CLI tool
COPY jshunter .

# Create necessary directories
RUN mkdir -p downloaded_js results .bin

# Set up TruffleHog (will be downloaded on first run)
RUN python3 jshunter --setup

# Make the script executable
RUN chmod +x jshunter

# Set the entrypoint
ENTRYPOINT ["python3", "jshunter"]

# Default command shows help
CMD ["--help"]

# Labels
LABEL maintainer="JSHunter Team"
LABEL description="JSHunter CLI - High-Performance JavaScript Security Scanner"
LABEL version="2.0.0"
LABEL repository="https://github.com/iamunixtz/JSNinja"
LABEL features="High-performance parallel processing, Discord integration, Async downloads"