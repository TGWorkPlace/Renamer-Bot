FROM python:3.10-slim

# --no-install-recommends is the key fix here: a plain `apt install ffmpeg`
# pulls in ~200MB of unrelated "recommended" packages (GTK, Mesa Vulkan
# drivers, pocketsphinx speech-recognition data, VA-API/VDPAU video
# drivers, systemd-cryptsetup, etc.) via ffmpeg's optional dependency
# chain (e.g. libsdl2 for ffplay). None of that is needed for a headless
# bot - it just bloats the image/build and was very likely what triggered
# the "Invalid cross-device link" dpkg error on Koyeb's builder. Skipping
# recommends installs only the actual codec/format libraries ffmpeg needs.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "bot.py"]
