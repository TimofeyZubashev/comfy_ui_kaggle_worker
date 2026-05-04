# ComfyUI Kaggle Worker Architecture

## Goal

Use Kaggle GPU sessions as temporary workers for ComfyUI inference.

## Main components

1. Persistent server:
   - FastAPI API
   - Telegram bot
   - job queue
   - input file storage
   - output file storage

2. Kaggle worker:
   - installs/loads ComfyUI
   - loads custom nodes
   - loads models
   - polls server for jobs
   - runs ComfyUI workflow
   - uploads result back to server

## Data flow

Telegram user sends request.

Server creates job.

Kaggle worker polls:

GET /worker/next-job

Worker receives:

- job_id
- text
- reference_audio_url
- generation settings

Worker downloads files.

Worker patches workflow_api.json.

Worker sends workflow to local ComfyUI API:

POST http://127.0.0.1:8188/prompt

ComfyUI generates output audio.

Worker uploads result:

POST /worker/upload-result/{job_id}

Server sends audio to Telegram user.

