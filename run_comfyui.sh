#!/bin/bash
set -e

cd /kaggle/working/ComfyUI

python main.py \
  --listen 127.0.0.1 \
  --port 8188


