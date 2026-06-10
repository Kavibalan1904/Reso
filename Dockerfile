FROM python:3.11-slim

WORKDIR /app

# Install Java and ffmpeg
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download Lavalink with YouTube fix
RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot
COPY main.py .

# Create Lavalink config
RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n    youtubeSearchEnabled: true\n    youtubePlaylistLoadLimit: 6\n    bufferDurationMs: 400' > application.yml

CMD java -jar Lavalink.jar & sleep 10 && python main.py
