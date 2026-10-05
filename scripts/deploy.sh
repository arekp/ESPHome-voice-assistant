#!/usr/bin/env bash
# Cykl testowy: walidacja -> kompilacja -> wgranie -> zebranie logów.
#
# Użycie:
#   scripts/deploy.sh [DEVICE] [SEKUNDY_LOGOW]
#     DEVICE        port USB (np. /dev/ttyACM0, COM5) albo OTA (voice-assistant.local / IP)
#                   domyślnie: $ESP_DEVICE lub voice-assistant.local
#     SEKUNDY_LOGOW ile sekund zbierać logi po wgraniu (domyślnie 60, 0 = bez logów)
#
#   CONFIG=inny.yaml scripts/deploy.sh ...   # inny plik konfiguracji
#   SKIP_UPLOAD=1 scripts/deploy.sh          # tylko walidacja + kompilacja
set -euo pipefail

cd "$(dirname "$0")/.."

CONFIG="${CONFIG:-esp_ver2.yaml}"
DEVICE="${1:-${ESP_DEVICE:-voice-assistant.local}}"
LOG_SECONDS="${2:-60}"

if [[ ! -f secrets.yaml ]]; then
  echo "Brak secrets.yaml - skopiuj secrets.yaml.example i uzupełnij." >&2
  exit 1
fi

echo "==> Walidacja $CONFIG"
esphome config "$CONFIG" > /dev/null

echo "==> Kompilacja"
esphome compile "$CONFIG"

if [[ "${SKIP_UPLOAD:-0}" == "1" ]]; then
  echo "==> SKIP_UPLOAD=1 - pomijam wgranie"
  exit 0
fi

echo "==> Wgrywanie na $DEVICE"
esphome upload "$CONFIG" --device "$DEVICE"

if [[ "$LOG_SECONDS" -gt 0 ]]; then
  mkdir -p logs
  LOG_FILE="logs/$(date +%Y%m%d-%H%M%S).log"
  echo "==> Zbieram logi przez ${LOG_SECONDS}s do $LOG_FILE"
  # esphome logs nie kończy się sam - ograniczamy czasem
  timeout "$LOG_SECONDS" esphome logs "$CONFIG" --device "$DEVICE" > "$LOG_FILE" 2>&1 || true
  ln -sf "$(basename "$LOG_FILE")" logs/latest.log
  echo "==> Gotowe. Błędy i ostrzeżenia:"
  grep -E "\[(E|W)\]" "$LOG_FILE" | tail -40 || echo "(brak)"
fi
