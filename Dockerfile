FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN echo 'server:\n  port: 2333\n  address: 0.0.0.0\nlavalink:\n  server:\n    password: "youshallnotpass"\n    sources:\n      youtube: true\n    youtubeSearchEnabled: true' > application.yml

CMD java -jar Lavalink.jar & sleep 8 && python main.py
