# Dockerfile for JS Ninja Telegram Bot
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

# Copy the CLI dependency
COPY ../cli/jshunter.py ./cli/
COPY ../cli/config.py ./cli/

# Copy the Telegram bot files
COPY jshunter_bot.py .
COPY config.py .

# Create necessary directories
RUN mkdir -p temp results .bin

# Set up TruffleHog (will be downloaded on first run)
RUN cd cli && python jshunter.py --setup

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port (not needed for Telegram bot, but good practice)
EXPOSE 8080

# Health check
HEALTHCHEK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0 if __import__('config').TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 1)"

# Run the bot
CMD ["python", "jshunter_bot.py"]

# Labels
LABEL maintainer="JS Ninja Team"
LABEL description="JS Ninja Telegram Bot - JavaScript Security Scanner Bot"
LABEL version="1.0.0"
LABEL repository="https://github.com/iamunixtz/JSNinja"