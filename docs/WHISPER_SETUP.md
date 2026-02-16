# Whisper Setup (Mac Mini)

## Requisitos
- macOS en Mac Mini
- Python 3.11
- `ffmpeg`
- Modelo Whisper (`base` recomendado para costo/velocidad)

## Instalación local
```bash
cd whisper-api
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables mínimas
```bash
export WHISPER_MODEL=base
export WHISPER_HOST=0.0.0.0
export WHISPER_PORT=5000
export WHISPER_API_KEY=REPLACE_ME
```

## Levantar servicios manualmente
Terminal 1:
```bash
cd whisper-api
source venv/bin/activate
uvicorn api:app --host ${WHISPER_HOST:-0.0.0.0} --port ${WHISPER_PORT:-5000}
```

Terminal 2:
```bash
cd whisper-api
source venv/bin/activate
python worker.py
```

## launchd (autostart)
Referencias en `docs/launchd/`:
- `com.voicenote.whisper-api.plist`
- `com.voicenote.whisper-worker.plist`

Copiar a `~/Library/LaunchAgents/`, luego:
```bash
launchctl load -w ~/Library/LaunchAgents/com.voicenote.whisper-api.plist
launchctl load -w ~/Library/LaunchAgents/com.voicenote.whisper-worker.plist
```

## Verificación
```bash
curl http://localhost:5000/health
```
Respuesta esperada:
```json
{"status":"ok"}
```

## Contrato del endpoint
### URL
`POST /transcribe`

### Método
`POST` `multipart/form-data`

### Payload
- `audio` (archivo binario)
- `language` (string, opcional)
- `source` (string, opcional)
- `priority` (string, opcional)
- `wait` (boolean, opcional)

### Response
- `wait=true`: resultado de transcripción con `text`, `segments`, `language`, `job_id`
- `wait=false`: `job_id` + estado inicial (`queued`)
