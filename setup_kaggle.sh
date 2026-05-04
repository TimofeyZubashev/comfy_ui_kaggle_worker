#!/bin/bash
set -e

WORKDIR="/kaggle/working"
COMFYUI_DIR="$WORKDIR/ComfyUI"
WORKER_DIR="$WORKDIR/comfyui-kaggle-worker"

COMFYUI_REPO="https://github.com/comfyanonymous/ComfyUI.git"
COSYVOICE_NODE_REPO="https://github.com/filliptm/ComfyUI_FL-CosyVoice3.git"

echo "=== Installing system dependencies ==="
apt-get update -y || true
apt-get install -y git ffmpeg libsndfile1 || true

echo "=== Cloning ComfyUI ==="
cd "$WORKDIR"

if [ ! -d "$COMFYUI_DIR" ]; then
  git clone "$COMFYUI_REPO" "$COMFYUI_DIR"
else
  echo "ComfyUI already exists: $COMFYUI_DIR"
fi

echo "=== Installing ComfyUI requirements.txt ==="
cd "$COMFYUI_DIR"
pip install -r requirements.txt

echo "=== Cloning ComfyUI_FL-CosyVoice3 into ComfyUI/custom_nodes ==="
mkdir -p "$COMFYUI_DIR/custom_nodes"
cd "$COMFYUI_DIR/custom_nodes"

if [ ! -d "ComfyUI_FL-CosyVoice3" ]; then
  git clone "$COSYVOICE_NODE_REPO"
else
  echo "ComfyUI_FL-CosyVoice3 already exists"
fi

echo "=== Installing ComfyUI_FL-CosyVoice3 requirements.txt ==="
cd "$COMFYUI_DIR/custom_nodes/ComfyUI_FL-CosyVoice3"
pip install -r requirements.txt

echo "=== Installing worker requirements ==="
cd "$WORKER_DIR"
pip install -r worker_requirements.txt

echo "=== Creating ComfyUI runtime folders ==="
mkdir -p "$COMFYUI_DIR/input"
mkdir -p "$COMFYUI_DIR/output"
mkdir -p "$COMFYUI_DIR/models"
mkdir -p "$COMFYUI_DIR/models/cosyvoice"

echo "=== Copying input audio files into ComfyUI/input/audio ==="

mkdir -p "$COMFYUI_DIR/input/audio"

if [ -d "$WORKER_DIR/input_audio" ]; then
  cp -r "$WORKER_DIR/input_audio/"* "$COMFYUI_DIR/input/audio/"
  echo "Input audio files copied to $COMFYUI_DIR/input/audio"
else
  echo "No input_audio directory found, skipping"
fi

echo "=== Setup finished ==="


