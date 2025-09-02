# Dockerfile for JS Ninja CLI Tool
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

# Copy the CLI tool
COPY jsninja.py .
COPY config.py .

# Create necessary directories
RUN mkdir -p downloads results .bin

# Set up TruffleHog (will be downloaded on first run)
RUN python jsninja.py --setup

# Make the script executable
RUN chmod +x jsninja.py

# Set the entrypoint
ENTRYPOINT ["python", "jsninja.py"]

# Default command shows help
CMD ["--help"]

# Labels
LABEL maintainer="JS Ninja Team"
LABEL description="JS Ninja CLI - JavaScript Security Scanner"
LABEL version="1.0.0"
LABEL repository="https://github.com/iamunixtz/JSNinja"