
#!/bin/bash

# Detener el script si algún comando falla
set -e

# Situarnos en la carpeta raíz del proyecto
cd "$(dirname "$0")/.."

# Fecha y hora para identificar cada copia
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")

# Carpeta donde guardaremos las copias
CARPETA="copias/$FECHA"
mkdir -p "$CARPETA"

echo "Iniciando copias de seguridad..."

# 1. Copia de PostgreSQL
echo "Guardando PostgreSQL..."

docker compose exec -T db sh -c \
  'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > "$CARPETA/postgres.dump"

# 2. Copia de MongoDB
echo "Guardando MongoDB..."

docker compose exec -T mongo sh -c \
  'mongodump --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --db albergues --archive --gzip' \
  > "$CARPETA/mongo.archive.gz"

echo ""
echo "Copias de seguridad terminadas."
echo "Guardadas en: $CARPETA"
