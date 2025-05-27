#!/bin/sh
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

# Lanzar Gunicorn y pasar a la siguiente línea, es decir, arrancarlo en segundo plano (&)
echo "[LanzAudit] Lanzando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --timeout 600 wsgi:app &

# Esperar a que Gunicorn escuche (máximo 30seg)
/wait-for-it.sh 127.0.0.1:8000 --timeout=30 --strict -- echo "[LanzAudit] Gunicorn está escuchando."

echo "[LanzAudit] Listo, contenedor preparado."

# Como ya está escuchando, nos traemos lo que dejamos en el background (&) al foreground (fg %1)
fg %1
