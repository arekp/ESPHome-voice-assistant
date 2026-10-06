# Środowisko developerskie

Instrukcja przygotowania komputera (Windows 11) do kompilowania, wgrywania i diagnozowania
firmware asystenta głosowego. Na Linux/macOS kroki są te same, zmieniają się tylko ścieżki
(`.venv/bin` zamiast `.venv/Scripts`, port `/dev/ttyUSB0` zamiast `COM4`).

## 1. Wymagania

| Element | Wersja / uwagi |
| :--- | :--- |
| Python | **3.12 lub nowszy** (zalecany 3.13). ESPHome 2026.9+ nie działa na 3.11 |
| ESPHome | **taka sama wersja jak dodatek ESPHome w Home Assistant** (obecnie 2026.9.1) |
| Git + Git Bash | do `scripts/deploy.sh` |
| Sterownik CH343 | gniazdo „UART” płytki widoczne jako `USB-Enhanced-SERIAL CH343 (COMx)` |
| Miejsce na dysku | ~3 GB na ESP-IDF i toolchain |

Python 3.13 bez uprawnień administratora:

```powershell
winget install --id Python.Python.3.13 --scope user
```

## 2. Środowisko Python (`.venv`)

```powershell
cd C:\Projekty\ESPHome-voice-assistant
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\esphome.exe version     # powinno pokazać 2026.9.1
```

Venv na Windows nie da się przenieść ani zmienić mu nazwy (pliki `.exe` mają zaszyte ścieżki).
Przy zmianie wersji Pythona usuń `.venv` i utwórz go od nowa.

## 3. Windows: limit długości ścieżek

ESP-IDF tworzy ścieżki dłuższe niż 260 znaków. Przy wyłączonych długich ścieżkach
(`LongPathsEnabled = 0`) kompilacja kończy się błędami typu
`fatal error: bits/c++config.h: No such file or directory` albo `WinError 206`.

Rozwiązanie bez uprawnień administratora: narzędzia ESP-IDF w krótkiej ścieżce.

```powershell
New-Item -ItemType Directory -Force C:\ESPHome\idf
[Environment]::SetEnvironmentVariable('ESPHOME_ESP_IDF_PREFIX', 'C:\ESPHome\idf', 'User')
```

(`scripts/deploy.sh` ustawia tę zmienną sam). Alternatywa: włączyć długie ścieżki w rejestrze
(PowerShell jako administrator) i zrestartować komputer:

```powershell
Set-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' LongPathsEnabled 1
```

Projekt trzymaj w krótkiej ścieżce (np. `C:\Projekty\...`), nie w `%TEMP%` ani głęboko w profilu.

## 4. Sekrety (`.env`)

```powershell
copy .env.example .env    # i uzupełnij wartości
```

| Zmienna | Opis |
| :--- | :--- |
| `WIFI_SSID`, `WIFI_PASSWORD` | sieć WiFi |
| `FALLBACK_AP_PASSWORD` | hasło zapasowego hotspotu (min. 8 znaków) |
| `API_KEY` | klucz szyfrowania API (base64, 32 bajty) – **ten sam, co zna HA** |
| `OTA_PASSWORD` | hasło OTA – **takie jak w firmware, który jest na płytce** |
| `HA_URL`, `HA_TOKEN` | opcjonalnie: adres HA i token długoterminowy (dla `scripts/ha.py`) |

ESPHome czyta sekrety tylko z `secrets.yaml` (`!secret`), więc `scripts/env2secrets.py`
generuje go z `.env`. Robi to automatycznie `scripts/deploy.sh`; ręcznie:

```powershell
.\.venv\Scripts\python.exe scripts\env2secrets.py
```

`.env` i `secrets.yaml` są w `.gitignore` – nigdy ich nie commituj.

## 5. Kompilacja, wgrywanie, logi

Pełny cykl (walidacja → kompilacja → wgranie → 60 s logów do `logs/`):

```bash
scripts/deploy.sh COM4                      # pierwszy raz kablem (gniazdo „UART”)
scripts/deploy.sh voice-assistant.local     # kolejne razy przez WiFi (OTA)
scripts/deploy.sh voice-assistant.local 0   # bez zbierania logów
SKIP_UPLOAD=1 scripts/deploy.sh             # tylko kompilacja
```

Pojedyncze kroki (PowerShell):

```powershell
$env:PYTHONUTF8 = '1'                       # polskie znaki w konsoli Windows
.\.venv\Scripts\esphome.exe config  esp_ver2.yaml
.\.venv\Scripts\esphome.exe compile esp_ver2.yaml
.\.venv\Scripts\esphome.exe upload  esp_ver2.yaml --device voice-assistant.local
.\.venv\Scripts\esphome.exe logs    esp_ver2.yaml --device voice-assistant.local
```

- Pierwsza kompilacja pobiera ESP-IDF i toolchain (~15–25 min), kolejne trwają kilka minut.
- `esphome logs` nie kończy się sam – w skryptach używaj `timeout 60 esphome logs ...`.
- W Git Bash kompilacja wymaga `unset MSYSTEM` (inaczej ESP-IDF: „MSys/Mingw is not supported”).
  `deploy.sh` robi to sam; najprościej kompilować z PowerShell.
- Logger działa na `UART0`, więc logi widać na COM4 (gniazdo „UART”) i przez WiFi.
- Nie da się jednocześnie wgrywać i czytać logów przez ten sam port COM.

## 6. Narzędzia diagnostyczne

```powershell
# Przyciski urządzenia przez API ESPHome (bez HA)
.\.venv\Scripts\python.exe scripts\button.py            # lista
.\.venv\Scripts\python.exe scripts\button.py RTTTL      # test głośnika (dwa piknięcia)

# Komendy WebSocket do Home Assistant (wymaga HA_URL/HA_TOKEN w .env)
.\.venv\Scripts\python.exe scripts\ha.py '{\"type\":\"assist_pipeline/pipeline/list\"}'
.\.venv\Scripts\python.exe scripts\ha.py '{\"type\":\"conversation/process\",\"text\":\"Która godzina?\",\"language\":\"pl\"}'

# Odczyt informacji o chipie przez kabel
.\.venv\Scripts\python.exe -m esptool --port COM4 flash-id
```

W logach urządzenia szukaj `[E]` i `[W]`. Przebieg poprawnej rozmowy:
`Detected 'Okay Nabu'` → `STT started` → `Speech recognised as: ...` → `Response: ...`
→ `TTS stream start` → `i2s_audio.speaker: Starting`.

## 7. Rozwiązane problemy (październik 2026)

| Objaw | Przyczyna | Rozwiązanie |
| :--- | :--- | :--- |
| YAML nie parsował się | dwie konfiguracje sklejone w jednym pliku | jedna spójna `esp_ver2.yaml`, sekrety przez `!secret` |
| Brak reakcji mikrofonu | w YAML piny 1/2/3, mikrofon podpięty do 4/5/6 | mikrofon na GPIO4/5/6 (README 1_v5) |
| Brak logów na COM4 | logger na `USB_SERIAL_JTAG`, kabel w gnieździe „UART” | `logger: hardware_uart: UART0` |
| Kompilacja: `WinError 206`, `c++config.h` | limit 260 znaków ścieżki w Windows | `ESPHOME_ESP_IDF_PREFIX=C:\ESPHome\idf` |
| Kompilacja: „MSys/Mingw is not supported” | uruchomienie z Git Bash | `unset MSYSTEM` / PowerShell |
| Lokalnie starsze ESPHome niż w HA | ESPHome 2026.9 wymaga Pythona ≥ 3.12 | `.venv` na Pythonie 3.13 |
| Słowo budzące „nie działa”, brak odpowiedzi | pipeline Assist „alfred” wskazywał nieistniejącego agenta `conversation.chatgpt` (HA zwracał błąd w ~20 ms, oczy mrugały na zielono niezauważalnie) | agent `conversation.openai_conversation` + „preferuj lokalne komendy” |
| Odpowiedź z innego głośnika (Atom Echo) | agent LLM użył narzędzia do wysłania komunikatu na inne urządzenie | to zachowanie LLM, nie firmware; Atom Echo odłączony |
| Cisza z głośnika (firmware odtwarza poprawnie) | pin 5V płytki bez napięcia – niezlutowana zworka **IN-OUT** na klonie N16R8 | tymczasowo Vin MAX98357A na **3V3**; docelowo zlutować IN-OUT i wrócić na 5V |
