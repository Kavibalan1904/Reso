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

# Download LATEST Lavalink (v4.0.1 or newer)
RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.1/Lavalink.jar

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY main.py .

# Create Lavalink config with YouTube plugins
RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n    youtubeSearchEnabled: true\n    plugins:\n      - dependency: "com.github.topi314.lavasrc:lavasrc-plugin:1.7.0"\n        repository: "https://maven.topi.wtf/releases"' > application.yml

# Start both services
CMD java -jar Lavalink.jar & sleep 15 && python main.py
