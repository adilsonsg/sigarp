#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose up -d --build
docker compose exec backend alembic upgrade head
echo "SIGARP iniciado em http://127.0.0.1:8000/docs"
