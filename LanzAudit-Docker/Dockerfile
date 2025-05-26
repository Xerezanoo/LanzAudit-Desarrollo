FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema, Nmap y WPScan
RUN apt update && apt install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    pango1.0-tools \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpq-dev \
    git \
    curl \
    nmap \
    ruby-full \
    && gem install wpscan \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias e instalar
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY app/ .

# Copiar entrypoint y wait-for-it
COPY entrypoint.sh /entrypoint.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /entrypoint.sh /wait-for-it.sh

# Entrypoint con migraciones automáticas
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000
