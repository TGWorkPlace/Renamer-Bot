FROM python:3.10-slim-bookworm

# Pinned to -bookworm (Debian 12) instead of the untagged `python:3.10-slim`,
# which recently started resolving to Debian trixie (13). Trixie's apt
# stages package extraction under /tmp before installing, and on Koyeb's
# build sandbox /tmp sits on a different filesystem/mount than the rest of
# the build root - so every single dpkg unpack rename() fails with
# "Invalid cross-device link", regardless of which packages are installed.
# Bookworm's apt doesn't use that staged-extraction path, so this sidesteps
# the issue entirely rather than working around it package-by-package.

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
