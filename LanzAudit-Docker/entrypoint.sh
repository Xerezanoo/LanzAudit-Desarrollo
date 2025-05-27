#!/bin/bash
echo "[LanzAudit] Esperando a que MariaDB esté disponible..."
/wait-for-it.sh db:3306 --timeout=60 --strict -- echo "[LanzAudit] MariaDB está listo."

# Inicializar migraciones solo si no existe la carpeta
if [ ! -d "migrations" ]; then
  echo "[LanzAudit] Primer uso: creando carpeta de migraciones..."
  flask db init
  flask db migrate -m "Migración inicial"
fi

echo "[LanzAudit] Aplicando migraciones si hacen falta..."
flask db upgrade

# Lanzar Gunicorn
echo "[LanzAudit] Lanzando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --timeout 600 wsgi:app
