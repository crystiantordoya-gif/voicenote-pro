# VoiceNote Pro

PWA profesional para grabación de audio en campo, transcripción offline/híbrida y generación de resúmenes con IA.

## Arquitectura
La aplicación sigue un flujo "Offline First":
1.  **Captura**: El usuario graba audio desde la PWA (funciona sin internet).
2.  **Sincronización**: Al recuperar conexión, la PWA sube los audios a n8n.
3.  **Procesamiento**:
    *   **Whisper (Local)**: Transcribe el audio.
    *   **OpenAI**: Genera un resumen ejecutivo.
4.  **Almacenamiento**: Guarda el resultado en Google Drive.

## Quick Start (Desarrollo)

### Frontend (PWA)
```bash
cd pwa
npm install
npm run dev
```

### Despliegue (Docker)
```bash
cd docker
docker-compose up -d --build
```

## Estructura del Repositorio
- `pwa/`: Código fuente de la aplicación (Vite + React).
- `docker/`: Configuración de despliegue (Nginx, Dockerfile).
- `docs/`: Documentación del proyecto (Deploy, Arquitectura).
- `n8n/`: Flujos de automatización exportados.
- `whisper-api/`: API wrapper para Whisper local (si aplica).
