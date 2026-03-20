# ========================================
# DOCKERFILE - BACKEND
# Sistema de Control de Visitantes
# Python 3.11 + Flask + PostgreSQL
# ========================================

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Supertiendas Cañaveral SAS"
LABEL description="Backend Flask - Sistema Control de Visitantes"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear carpetas necesarias
RUN mkdir -p logs uploads/visitantes backups && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Puerto de la aplicación
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Comando por defecto (producción con Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]
