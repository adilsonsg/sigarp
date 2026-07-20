#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose run --rm backend ruff check .
docker compose run --rm backend black --check .
docker compose run --rm backend isort --check-only .
