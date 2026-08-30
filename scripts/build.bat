
set -e

# Собираем базовый образ
docker build -f Dockerfile.base -t shared-base:latest .



docker build -f Dockerfile.gateway -t gateway:latest .
docker build -f Dockerfile.worker -t ads-worker:latest .

docker compose up -d