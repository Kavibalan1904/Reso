FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    ffmpeg \
    wget \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Download Lavalink
RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Create Lavalink config
RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n    youtubeSearchEnabled: true\n    bufferDurationMs: 400\n    frameBufferDurationMs: 5000' > application.yml

# Start both services
CMD java -jar Lavalink.jar & sleep 15 && python main.py
