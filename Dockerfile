FROM python:3.11-slim

WORKDIR /app

# Install Java 21 (the correct package name for Debian Trixie)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Download Lavalink
RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Create Lavalink configuration
RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n    youtubeSearchEnabled: true' > application.yml

# Start Lavalink and then the bot
CMD java -jar Lavalink.jar & sleep 10 && python main.py
