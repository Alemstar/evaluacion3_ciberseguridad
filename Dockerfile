FROM python:3.11-slim

# Labels para metadatos de seguridad
LABEL maintainer="DevSecOps Team"
LABEL security.scan="enabled"
LABEL security.policies="strict"

WORKDIR /app

# Actualizar e instalar solo dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Crear usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
# Copiar código de la aplicación
COPY --chown=appuser:appuser src/secure_app.py .
COPY --chown=appuser:appuser src/secure_create_db.py .
COPY --chown=appuser:appuser templates/ templates/

# Inicializar base de datos
RUN python secure_create_db.py

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Usar gunicorn en lugar de Flask dev server
CMD ["gunicorn", \
    "--bind", "0.0.0.0:5000", \
    "--workers", "4", \
    "--worker-class", "sync", \
    "--timeout", "30", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "secure_app:app"]