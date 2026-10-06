# Instrukcje dla Claude

- Zawsze odpowiadaj po polsku.

## Projekt

Konfiguracja ESPHome asystenta głosowego na ESP32-S3 DevKitC-1 N16R8.
Główny plik: `esp_ver2.yaml`. Sekrety w `.env` (nie commitować, wzór: `.env.example`); `scripts/env2secrets.py`
generuje z niego `secrets.yaml` dla `!secret` (robi to `scripts/deploy.sh`).

## Cykl testowania na płytce

Działa tylko w sesji uruchomionej na komputerze z podłączoną płytką
(Claude Desktop / `claude` / `claude remote-control`), nie w chmurze.

- ESPHome jest zainstalowany w `.venv` (Python 3.13, ESPHome 2026.9.1 – ta sama wersja co w HA) – używaj `.venv/Scripts/esphome.exe`
  (`scripts/deploy.sh` dodaje `.venv` do PATH sam). Na Windows ustaw `PYTHONUTF8=1`.
- Kompilacja z Git Bash wymaga `unset MSYSTEM` (inaczej ESP-IDF: „MSys/Mingw is not supported”),
  najprościej kompilować z PowerShell. Długie ścieżki w Windows są wyłączone – nie budować
  w głęboko zagnieżdżonych katalogach (np. %TEMP%), tylko w katalogu projektu.
  Narzędzia ESP-IDF leżą w `C:\ESPHome\idf` (zmienna użytkownika `ESPHOME_ESP_IDF_PREFIX`).
- Na komputerze z Windows płytka widoczna jest jako `COM4` (CH343, gniazdo „UART”).
- Walidacja: `esphome config esp_ver2.yaml`
- Kompilacja: `esphome compile esp_ver2.yaml` (pierwsza z ESP-IDF trwa 10–20 min)
- Pełny cykl: `scripts/deploy.sh [DEVICE] [SEKUNDY_LOGOW]`
  - pierwszy raz przez USB: `scripts/deploy.sh /dev/ttyACM0` (Windows: `COM4`)
  - potem przez WiFi (OTA): `scripts/deploy.sh voice-assistant.local`
- Logi trafiają do `logs/latest.log` – czytaj je po każdym wgraniu i szukaj `[E]`/`[W]`.
- `esphome logs` nigdy nie kończy się sam – zawsze uruchamiaj go z `timeout` albo w tle.
- Nie można jednocześnie czytać logów i wgrywać przez ten sam port USB.
- Logger działa na `UART0` – logi widać na COM4 (gniazdo „UART”, CH343) albo przez WiFi.

## Diagnostyka

- Instrukcja środowiska i lista rozwiązanych problemów: `docs/DEVELOPMENT.md`.
- `scripts/button.py [NAZWA]` – wciska przycisk urządzenia przez API ESPHome (np. `RTTTL` = test głośnika).
- `scripts/ha.py '<json>'` – komendy WebSocket do HA (pipeline'y Assist, `conversation/process`);
  wymaga `HA_URL`/`HA_TOKEN` w `.env`. Zmiany w konfiguracji HA rób tylko za zgodą użytkownika.
