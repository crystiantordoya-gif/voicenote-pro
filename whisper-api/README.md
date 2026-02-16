# Whisper API (Mac Mini)

API local para transcribir audio con Whisper y un worker de cola en disco.

## Archivos clave
- `api.py`: API FastAPI (health, transcribe, status, result)
- `worker.py`: worker secuencial para procesar la cola
- `config.py`: configuración por variables de entorno
- `requirements.txt`: dependencias Python

## Requisitos
- Python 3.11
- `ffmpeg` en PATH

## Instalación
```bash
cd whisper-api
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno
- `WHISPER_MODEL` (ej. `base`)
- `WHISPER_HOST` (default `0.0.0.0`)
- `WHISPER_PORT` (default `5000`)
- `WHISPER_API_KEY` (opcional, recomendado)
- `WHISPER_DATA_DIR` (ruta para cola y resultados)

## Ejecutar API
```bash
cd whisper-api
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 5000
```

## Ejecutar worker
```bash
cd whisper-api
source venv/bin/activate
python worker.py
```

## Endpoints
- `GET /health`
- `POST /transcribe` (multipart)
- `GET /status/{job_id}`
- `GET /result/{job_id}`

### POST /transcribe
- Header opcional: `X-API-Key`
- Form fields:
  - `audio` (archivo)
  - `language` (default `es`)
  - `source` (default `mobile`)
  - `priority` (default `normal`)
  - `wait` (`true|false`)

### Ejemplo rápido
```bash
curl -X POST \
  -H "X-API-Key: REPLACE_ME" \
  -F "audio=@/tmp/test.m4a" \
  -F "language=es" \
  -F "wait=true" \
  http://localhost:5000/transcribe
```
