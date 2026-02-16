import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from config import (
    QUEUE_INCOMING_DIR,
    QUEUE_PROCESSING_DIR,
    QUEUE_PROCESSED_DIR,
    QUEUE_FAILED_DIR,
    DEFAULT_LANGUAGE,
    DEFAULT_SOURCE,
    DEFAULT_PRIORITY,
    ALLOWED_AUDIO_EXTENSIONS,
    WHISPER_API_KEY,
    WHISPER_MAX_FILE_MB,
    WHISPER_MODEL,
)
from worker import process_job, job_paths
import whisper

app = FastAPI(title="VoiceNote Whisper API", version="1.0.0")


def ensure_dirs() -> None:
    for d in [QUEUE_INCOMING_DIR, QUEUE_PROCESSING_DIR, QUEUE_PROCESSED_DIR, QUEUE_FAILED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_api_key(x_api_key: str | None) -> None:
    if WHISPER_API_KEY and x_api_key != WHISPER_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


def locate_job(job_id: str) -> Path | None:
    for base in [QUEUE_INCOMING_DIR, QUEUE_PROCESSING_DIR, QUEUE_PROCESSED_DIR, QUEUE_FAILED_DIR]:
        if (base / job_id).exists():
            return base
    return None


def create_job(meta: dict[str, Any], filename: str) -> dict[str, Any]:
    ensure_dirs()
    job_id = uuid.uuid4().hex
    paths = job_paths(QUEUE_INCOMING_DIR, job_id)
    paths["root"].mkdir(parents=True, exist_ok=True)

    write_json(paths["meta"], {**meta, "job_id": job_id, "filename": filename, "created_at": now_iso()})
    write_json(paths["status"], {"job_id": job_id, "state": "queued", "created_at": now_iso()})
    return {"job_id": job_id, "paths": paths}


def update_status(job_id: str, state: str, extra: dict[str, Any] | None = None) -> None:
    base = locate_job(job_id)
    if not base:
        return
    paths = job_paths(base, job_id)
    payload = read_json(paths["status"]) if paths["status"].exists() else {"job_id": job_id}
    payload.update({"state": state, "updated_at": now_iso()})
    if extra:
        payload.update(extra)
    write_json(paths["status"], payload)


def get_status(job_id: str) -> dict[str, Any] | None:
    base = locate_job(job_id)
    if not base:
        return None
    status_path = job_paths(base, job_id)["status"]
    if not status_path.exists():
        return None
    return read_json(status_path)


def get_result(job_id: str) -> dict[str, Any] | None:
    base = locate_job(job_id)
    if not base:
        return None
    result_path = job_paths(base, job_id)["result"]
    if not result_path.exists():
        return None
    return read_json(result_path)


def move_to_processing(job_id: str) -> dict[str, Path] | None:
    src = QUEUE_INCOMING_DIR / job_id
    if not src.exists():
        return None
    dst = QUEUE_PROCESSING_DIR / job_id
    src.rename(dst)
    return job_paths(QUEUE_PROCESSING_DIR, job_id)


def save_upload_file(upload: UploadFile, destination: Path) -> None:
    max_bytes = WHISPER_MAX_FILE_MB * 1024 * 1024
    total = 0
    with destination.open("wb") as out:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise HTTPException(status_code=413, detail="File too large")
            out.write(chunk)


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.post("/transcribe")
def transcribe(
    audio: UploadFile = File(...),
    language: str = Form(DEFAULT_LANGUAGE),
    source: str = Form(DEFAULT_SOURCE),
    priority: str = Form(DEFAULT_PRIORITY),
    wait: bool = Form(False),
    x_api_key: str | None = Header(default=None),
) -> JSONResponse:
    verify_api_key(x_api_key)
    ensure_dirs()

    extension = Path(audio.filename).suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {extension}")

    job = create_job({"language": language, "source": source, "priority": priority}, audio.filename)
    save_upload_file(audio, job["paths"]["input"])

    if wait:
        paths = move_to_processing(job["job_id"])
        if not paths:
            raise HTTPException(status_code=500, detail="Failed to claim queued job")
        model = whisper.load_model(WHISPER_MODEL)
        process_job(paths, model)
        result = get_result(job["job_id"])
        return JSONResponse(result or {"job_id": job["job_id"], "state": "failed"})

    return JSONResponse({"job_id": job["job_id"], "status": get_status(job["job_id"])})


@app.get("/status/{job_id}")
def status(job_id: str, x_api_key: str | None = Header(default=None)) -> JSONResponse:
    verify_api_key(x_api_key)
    status_payload = get_status(job_id)
    if not status_payload:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(status_payload)


@app.get("/result/{job_id}")
def result(job_id: str, x_api_key: str | None = Header(default=None)) -> JSONResponse:
    verify_api_key(x_api_key)
    result_payload = get_result(job_id)
    if not result_payload:
        raise HTTPException(status_code=404, detail="Result not found")
    return JSONResponse(result_payload)
