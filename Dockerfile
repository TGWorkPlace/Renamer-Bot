FROM python:3.10-slim

# Install FFmpeg
RUN apt update && \
    apt install -y ffmpeg && \
    apt clean

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
