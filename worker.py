import json
import time
import pathlib
import requests
from typing import Optional, Dict, Any


def load_config(path: str = "config.json") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_next_job(server_url: str, worker_token: str) -> Optional[Dict[str, Any]]:
    response = requests.get(
        f"{server_url}/worker/next-job",
        params={"worker_token": worker_token},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    return data.get("job")


def download_file(url: str, target_path: pathlib.Path) -> pathlib.Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    with open(target_path, "wb") as file:
        file.write(response.content)

    return target_path


def submit_workflow_to_comfyui(comfyui_url: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(
        f"{comfyui_url}/prompt",
        json={"prompt": workflow},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def upload_result(server_url: str, worker_token: str, job_id: str, result_path: pathlib.Path) -> None:
    with open(result_path, "rb") as file:
        response = requests.post(
            f"{server_url}/worker/upload-result/{job_id}",
            params={"worker_token": worker_token},
            files={"file": file},
            timeout=300,
        )

    response.raise_for_status()


def load_workflow(workflow_path: str) -> Dict[str, Any]:
    with open(workflow_path, "r", encoding="utf-8") as file:
        return json.load(file)


def patch_workflow(workflow: Dict[str, Any], job: Dict[str, Any], input_audio_path: Optional[str]) -> Dict[str, Any]:
    """
    Здесь мы позже подставим реальные node_id из твоего workflow_api.json.

    Например:
    workflow["12"]["inputs"]["text"] = job["text"]
    workflow["17"]["inputs"]["audio"] = input_audio_path
    workflow["25"]["inputs"]["filename_prefix"] = job["job_id"]
    """
    text = job.get("text", "")

    print("TODO: patch workflow with text:", text)
    print("TODO: patch workflow with input audio:", input_audio_path)

    return workflow


def wait_for_result(output_dir: pathlib.Path, job_id: str, timeout_seconds: int = 600) -> pathlib.Path:
    """
    Упрощённый вариант.
    Позже лучше сделать ожидание через ComfyUI /history API.
    """
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        candidates = list(output_dir.glob(f"*{job_id}*.wav")) + list(output_dir.glob(f"*{job_id}*.mp3"))

        if candidates:
            return candidates[0]

        time.sleep(2)

    raise TimeoutError(f"Result file for job {job_id} was not found in {output_dir}")


def process_job(config: Dict[str, Any], job: Dict[str, Any]) -> None:
    job_id = job["job_id"]
    print(f"Processing job: {job_id}")

    input_dir = pathlib.Path(config["input_dir"])
    output_dir = pathlib.Path(config["output_dir"])

    input_audio_path = None

    if job.get("reference_audio_url"):
        input_audio_path = input_dir / f"{job_id}_reference.wav"
        download_file(job["reference_audio_url"], input_audio_path)

    workflow = load_workflow(config["workflow_path"])
    workflow = patch_workflow(
        workflow=workflow,
        job=job,
        input_audio_path=str(input_audio_path) if input_audio_path else None,
    )

    comfy_response = submit_workflow_to_comfyui(config["comfyui_url"], workflow)
    print("ComfyUI response:", comfy_response)

    result_path = wait_for_result(output_dir, job_id)

    upload_result(
        server_url=config["server_url"],
        worker_token=config["worker_token"],
        job_id=job_id,
        result_path=result_path,
    )

    print(f"Job completed: {job_id}")


def main() -> None:
    config = load_config()

    server_url = config["server_url"]
    worker_token = config["worker_token"]
    poll_interval = config.get("poll_interval_seconds", 5)

    print("Worker started")

    while True:
        try:
            job = get_next_job(server_url, worker_token)

            if not job:
                print("No jobs")
                time.sleep(poll_interval)
                continue

            process_job(config, job)

        except Exception as error:
            print("Worker error:", repr(error))
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()

