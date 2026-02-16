# Guía de Despliegue: VoiceNote Pro PWA

## Prerrequisitos en VPS
- Docker y Docker Compose instalados.
- Puerto 8081 disponible (o configurar Traefik/Reverse Proxy).
- Carpeta `/root/voicenote` (o similar) creada.

## Pasos de Despliegue

### 1. Preparar Archivos Locales
Asegúrate de tener la carpeta `dist` generada:
```bash
cd projects/voicenote/pwa
npm run build
```

### 2. Transferir al VPS
Usa SCP (o tu método preferido) para subir los archivos:
```bash
# Estando en projects/voicenote
scp -r ./pwa/dist user@voicenote.amayu.cloud:/root/voicenote/
scp nginx.conf Dockerfile docker-compose.yml user@voicenote.amayu.cloud:/root/voicenote/
```

### 3. Ejecutar en VPS
Conéctate por SSH y levanta el servicio:
```bash
ssh user@voicenote.amayu.cloud
cd /root/voicenote

# Construir y levantar
docker-compose up -d --build
```

### 4. Verificación
- Accede a `http://voicenote.amayu.cloud:8081` (si usaste el puerto directo).
- Si usas Traefik, asegúrate de que el router apunte al puerto 80 del contenedor.

## Configuración Nginx
El archivo `nginx.conf` ya está optimizado para SPA:
- Redirige todo a `index.html`.
- Cachea assets estáticos por 1 año.
- No cachea `index.html` ni `sw.js` para asegurar actualizaciones.
