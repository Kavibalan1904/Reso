FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including opus for voice
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    opus-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Run the bot
CMD ["python", "main.py"]
