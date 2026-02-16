import json
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

import whisper

from config import (
    QUEUE_INCOMING_DIR,
    QUEUE_PROCESSING_DIR,
    QUEUE_PROCESSED_DIR,
    QUEUE_FAILED_DIR,
    WHISPER_MODEL,
    WHISPER_WORKER_SLEEP,
    FFMPEG_BIN,
)


def ensure_dirs() -> None:
    for d in [QUEUE_INCOMING_DIR, QUEUE_PROCESSING_DIR, QUEUE_PROCESSED_DIR, QUEUE_FAILED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def job_paths(base_dir: Path, job_id: str) -> dict[str, Path]:
    root = base_dir / job_id
    return {
        "root": root,
        "meta": root / "meta.json",
        "status": root / "status.json",
        "input": root / "input",
        "wav": root / "input.wav",
        "transcript": root / "transcript.txt",
        "result": root / "result.json",
    }


def locate_job(job_id: str) -> Path | None:
    for base in [QUEUE_INCOMING_DIR, QUEUE_PROCESSING_DIR, QUEUE_PROCESSED_DIR, QUEUE_FAILED_DIR]:
        if (base / job_id).exists():
            return base
    return None


def move_job(job_id: str, src_base: Path, dst_base: Path) -> Path:
    src = src_base / job_id
    dst = dst_base / job_id
    dst_base.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    return dst


def claim_next_job() -> dict[str, Path] | None:
    ensure_dirs()
    for incoming_job in sorted(QUEUE_INCOMING_DIR.iterdir()):
        if not incoming_job.is_dir():
            continue
        job_id = incoming_job.name
        move_job(job_id, QUEUE_INCOMING_DIR, QUEUE_PROCESSING_DIR)
        return job_paths(QUEUE_PROCESSING_DIR, job_id)
    return None


def update_status(job_id: str, state: str, extra: dict[str, Any] | None = None) -> None:
    base = locate_job(job_id)
    if not base:
        return
    paths = job_paths(base, job_id)
    status = read_json(paths["status"]) if paths["status"].exists() else {}
    status.update({"job_id": job_id, "state": state, "updated_at": now_iso()})
    if extra:
        status.update(extra)
    write_json(paths["status"], status)


def convert_to_wav(input_path: Path, output_path: Path) -> None:
    cmd = [FFMPEG_BIN, "-y", "-i", str(input_path), "-ac", "1", "-ar", "16000", str(output_path)]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def process_job(paths: dict[str, Path], model: whisper.Whisper) -> None:
    job_id = paths["root"].name
    meta = read_json(paths["meta"])
    update_status(job_id, "processing", {"started_at": now_iso()})

    try:
        convert_to_wav(paths["input"], paths["wav"])
        result = model.transcribe(str(paths["wav"]), language=meta.get("language", "es"))
        text = result.get("text", "").strip()

        paths["transcript"].write_text(text, encoding="utf-8")
        write_json(
            paths["result"],
            {
                "job_id": job_id,
                "text": text,
                "segments": result.get("segments", []),
                "language": result.get("language", meta.get("language", "es")),
                "duration": result.get("duration"),
                "completed_at": now_iso(),
            },
        )

        update_status(job_id, "completed", {"completed_at": now_iso()})
        move_job(job_id, QUEUE_PROCESSING_DIR, QUEUE_PROCESSED_DIR)
    except Exception as exc:
        update_status(job_id, "failed", {"error": str(exc), "failed_at": now_iso()})
        move_job(job_id, QUEUE_PROCESSING_DIR, QUEUE_FAILED_DIR)


def run_loop() -> None:
    ensure_dirs()
    model = whisper.load_model(WHISPER_MODEL)
    while True:
        job = claim_next_job()
        if not job:
            time.sleep(WHISPER_WORKER_SLEEP)
            continue
        process_job(job, model)


if __name__ == "__main__":
    run_loop()
