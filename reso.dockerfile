FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Java for Lavalink
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download Lavalink
RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar -O Lavalink.jar

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Create Lavalink config
RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n      spotify: true\n    bufferDurationMs: 400\n    youtubePlaylistLoadLimit: 6\n    youtubeSearchEnabled: true' > application.yml

# Expose Lavalink port
EXPOSE 2333

# Start Lavalink and bot
CMD java -jar Lavalink.jar & sleep 10 && python main.py