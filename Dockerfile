# Use the official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Run apt-get update and upgrade to prevent vulnerabilities, and install required system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy application files and switch ownership
COPY --chown=user . $HOME/app

# Ensure start.sh is executable
RUN chmod +x start.sh

# Download the 50MB of Swiss Ephemeris Data Files
RUN python scripts/download_ephemeris.py

# Hugging Face Spaces Docker environments run on port 7860 by default
ENV PORT=7860

# Expose the port
EXPOSE 7860

# Start both API and Bot using start.sh
CMD ["./start.sh"]
