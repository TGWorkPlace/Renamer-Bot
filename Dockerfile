FROM mwader/static-ffmpeg:7.0 AS ffmpeg

FROM python:3.10-slim-bookworm

WORKDIR /app

# Copy static ffmpeg binaries from the FFmpeg image.
COPY --from=ffmpeg /ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg /ffprobe /usr/local/bin/ffprobe

# Verify FFmpeg is available.
RUN ffmpeg -version && ffprobe -version

# Install Python dependencies.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application.
COPY . .

CMD ["python", "bot.py"]
