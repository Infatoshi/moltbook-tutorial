# Moltbook Bot Sandbox
# A safe, isolated environment for running your Moltbook bot

FROM python:3.12-slim

# No root access after setup
RUN useradd -m -s /bin/bash botuser

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    httpx \
    rich \
    python-dotenv

# Create app directory
WORKDIR /app

# Copy bot files
COPY LLMs.md /app/
COPY bot.py /app/
COPY examples/ /app/examples/

# Create config directory
RUN mkdir -p /home/botuser/.config/moltbook && \
    chown -R botuser:botuser /app /home/botuser

# Switch to non-root user
USER botuser

# Set environment
ENV HOME=/home/botuser
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "bot.py"]
