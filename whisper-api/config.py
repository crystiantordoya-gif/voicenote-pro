import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("WHISPER_DATA_DIR", BASE_DIR / "data"))

QUEUE_INCOMING_DIR = DATA_DIR / "queue" / "incoming"
QUEUE_PROCESSING_DIR = DATA_DIR / "queue" / "processing"
QUEUE_PROCESSED_DIR = DATA_DIR / "queue" / "processed"
QUEUE_FAILED_DIR = DATA_DIR / "queue" / "failed"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_HOST = os.getenv("WHISPER_HOST", "0.0.0.0")
WHISPER_PORT = int(os.getenv("WHISPER_PORT", "5000"))
WHISPER_API_KEY = os.getenv("WHISPER_API_KEY", "")
WHISPER_MAX_FILE_MB = int(os.getenv("WHISPER_MAX_FILE_MB", "250"))
WHISPER_WORKER_SLEEP = int(os.getenv("WHISPER_WORKER_SLEEP", "3"))

DEFAULT_LANGUAGE = os.getenv("WHISPER_DEFAULT_LANGUAGE", "es")
DEFAULT_SOURCE = os.getenv("WHISPER_DEFAULT_SOURCE", "mobile")
DEFAULT_PRIORITY = os.getenv("WHISPER_DEFAULT_PRIORITY", "normal")

ALLOWED_AUDIO_EXTENSIONS = {".webm", ".m4a", ".mp3", ".wav", ".ogg", ".aac"}
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
