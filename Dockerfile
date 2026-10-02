# ClipSave — Dockerfile for Koyeb (free tier, no credit card)
# ffmpeg is installed via apt so video merge / MP3 conversion works.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Koyeb provides $PORT automatically
CMD gunicorn -w 2 --threads 2 --timeout 900 -b 0.0.0.0:$PORT app:app
