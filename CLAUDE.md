# Instrukcje dla Claude

- Zawsze odpowiadaj po polsku.

## Projekt

Konfiguracja ESPHome asystenta głosowego na ESP32-S3 DevKitC-1 N16R8.
Główny plik: `esp_ver2.yaml`. Sekrety w `secrets.yaml` (nie commitować, wzór: `secrets.yaml.example`).

## Cykl testowania na płytce

Działa tylko w sesji uruchomionej na komputerze z podłączoną płytką
(Claude Desktop / `claude` / `claude remote-control`), nie w chmurze.

- Walidacja: `esphome config esp_ver2.yaml`
- Kompilacja: `esphome compile esp_ver2.yaml` (pierwsza z ESP-IDF trwa 10–20 min)
- Pełny cykl: `scripts/deploy.sh [DEVICE] [SEKUNDY_LOGOW]`
  - pierwszy raz przez USB: `scripts/deploy.sh /dev/ttyACM0` (Windows: `COM5`)
  - potem przez WiFi (OTA): `scripts/deploy.sh voice-assistant.local`
- Logi trafiają do `logs/latest.log` – czytaj je po każdym wgraniu i szukaj `[E]`/`[W]`.
- `esphome logs` nigdy nie kończy się sam – zawsze uruchamiaj go z `timeout` albo w tle.
- Nie można jednocześnie czytać logów i wgrywać przez ten sam port USB.
- Logger działa na `USB_SERIAL_JTAG` – płytka musi być podłączona gniazdem „USB”, nie „UART”.
