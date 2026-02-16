# Arquitectura: VoiceNote Pro

## Flujo de Datos

```mermaid
graph LR
    User[Usuario (iPhone)] -->|Graba Audio| PWA[PWA (React/Vite)]
    PWA -->|Offline| IDB[IndexedDB (Local)]
    PWA -->|Online Sync| Webhook[n8n Webhook]
    Webhook -->|Procesa| Whisper[Whisper Local (Mac Mini)]
    Whisper -->|Texto| GPT[OpenAI GPT-4]
    GPT -->|Resumen| Drive[Google Drive]
```

## Componentes

### Frontend (PWA)
- **Tecnología**: React, Vite, TypeScript.
- **Responsabilidad**: Interfaz de usuario, grabación de audio, gestión offline.
- **Despliegue**: Docker Nginx en VPS.

### Backend (n8n)
- **Tecnología**: n8n (Self-hosted).
- **Responsabilidad**: Orquestación del flujo. Recibe el audio, llama a Whisper, procesa con GPT y guarda en Drive.

### IA (Whisper + GPT)
- **Whisper**: Ejecución local en Mac Mini para transcripción de alta fidelidad sin coste por minuto.
- **GPT**: Generación de resúmenes estructurados y extracción de puntos clave.
