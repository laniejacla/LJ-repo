#!/bin/bash
# Builds output/si-juan-mulat-ep1.mp4 from video.html. Usage: ./build.sh [workdir]
set -e
cd "$(dirname "$0")"
WORK="${1:-$(mktemp -d)}"
node render.js "$WORK/frames" 30
python3 music.py "$WORK/frames/timeline.json" "$WORK/music.wav"
mkdir -p output
ffmpeg -loglevel error -y -framerate 30 -i "$WORK/frames/f%05d.jpg" -i "$WORK/music.wav" \
  -vf "noise=alls=4:allf=t,format=yuv420p" -c:v libx264 -preset slow -crf 23 -maxrate 3M -bufsize 6M \
  -af "loudnorm=I=-16:TP=-1.5:LRA=14" -c:a aac -b:a 192k -ar 44100 -movflags +faststart -shortest \
  output/si-juan-mulat-ep1.mp4
echo "built output/si-juan-mulat-ep1.mp4"
