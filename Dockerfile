FROM python:3.11-slim

WORKDIR /app

# Install ffmpeg and opus for voice
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    opus-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot
COPY main.py .

# Run bot
CMD ["python", "main.py"]
