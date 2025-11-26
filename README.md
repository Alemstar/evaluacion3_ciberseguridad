# evaluacion3_ciberseguridad

Proyecto de ejemplo con prácticas de seguridad: SAST, DAST y pruebas.

## OWASP ZAP - Escaneo automatizado (Jenkins + local)

Se ha integrado OWASP ZAP en el `Jenkinsfile` para ejecutar un escaneo DAST completo (`zap-full-scan.py`).

- Reportes generados en: `zap-reports/` (HTML y JSON)
-- Parámetro de job: `ZAP_FAIL_THRESHOLD` (por defecto `0`). El build fallará si el número de alertas `High`/`Critical` es mayor que este umbral. Puedes cambiarlo desde la UI del job en Jenkins antes de lanzar la ejecución.

Ejecutar localmente (PowerShell + Docker Desktop):
```powershell
# Construir y arrancar la app
docker build -t evaluacion3_ciberseguridad:local .
docker run -d -p 5000:5000 --name taskapp evaluacion3_ciberseguridad:local

# Ejecutar el escaneo ZAP (usa bash)

# En Windows PowerShell (sin WSL/Git-Bash) usa el script PowerShell incluido:
powershell -File .\scripts\run_zap_scan.ps1 -Target 'http://host.docker.internal:5000'

# Si prefieres Bash/WSL, sigue usando:
# bash ./scripts/run_zap_scan.sh http://host.docker.internal:5000

# Limpiar
docker stop taskapp; docker rm taskapp
```

Notas para Jenkins:
- El agente debe tener Docker y `python3` disponibles.
- `host.docker.internal` funciona con Docker Desktop; si el entorno no soporta este hostname, sustituir por una red Docker o exponer puertos según la configuración del runner.
- Si el escaneo es lento, incrementar el `timeout` global del pipeline.

Solución al error "pull access denied" / "repository does not exist or may require 'docker login'":

- Asegúrate que el agente/tu máquina tiene acceso a Internet y Docker puede hacer pull de imágenes.
- **Nota importante**: La imagen antigua `owasp/zap2docker-stable` ya no está disponible. Ahora ZAP usa `ghcr.io/zaproxy/zaproxy:stable`.
- Si el pull falla por límites de Docker Hub, haz `docker login` con tu cuenta y vuelve a intentar:
```powershell
docker login
docker pull ghcr.io/zaproxy/zaproxy:stable
```
- Como alternativa, prueba otras imágenes disponibles:
```powershell
docker pull softwaresecurityproject/zap-stable
docker pull zaproxy/zap-stable
```
- Si no quieres o no puedes hacer pull, instala ZAP localmente o usa WSL/Git-Bash en vez de Docker.

Diagnóstico adicional si `docker pull` falla:

- Ejecuta `docker search zap2docker` para comprobar imágenes disponibles y nombres exactos:
```powershell
docker search zap2docker
```
- Revisa el error concreto de `docker pull` (copiar la salida ayuda a diagnosticar rate limits o autenticación).
- Si estás detrás de un proxy o cortafuegos, asegúrate de que Docker tiene configuración de proxy adecuada.

Opciones futuras:
- Añadir `ZAP_FAIL_THRESHOLD` como parámetro del job para que sea configurable desde la UI de Jenkins.
- Ejecutar ZAP en modo daemon y usar la API para escaneos autenticados o contextos específicos.

Para cualquier cambio adicional en la integración ZAP, dime qué prefieres y lo implemento.

