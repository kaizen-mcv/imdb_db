#!/bin/bash
# Actualizacion quincenal de IMDb DB
# IMDb publica los datasets diariamente, pero con refrescar cada
# dos semanas es suficiente para la mayoria de usos.
# Ejecutar desde cron los dias 1 y 15 a las 20:00 hora Madrid.

set -e

PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$PROJECT/.venv"
LOG_DIR="$PROJECT/data/logs"
DATE=$(date +%Y%m%d)
LOG="$LOG_DIR/biweekly_update_${DATE}.log"

mkdir -p "$LOG_DIR"

source "$VENV/bin/activate"
cd "$PROJECT"

{
    echo "=== IMDb biweekly update $(date) ==="

    echo "[$(date +%H:%M)] Descargando datasets..."
    imdb download --force

    echo "[$(date +%H:%M)] Importando a PostgreSQL (truncate)..."
    imdb load --truncate

    echo "[$(date +%H:%M)] Estadisticas finales:"
    imdb status

    echo "=== Fin $(date) ==="
} >> "$LOG" 2>&1
