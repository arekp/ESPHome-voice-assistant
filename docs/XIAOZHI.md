# Przejście na serwer XiaoZhi – analiza

Branch: `xiaozhi-server`. Serwer: `http://192.168.1.67:8002` (panel „智控台” = xiaozhi-esp32-server w wersji pełnej, z bazą i Java API).

## Stan obecny

ESP32-S3 + ESPHome (`esp_ver2.yaml`): `micro_wake_word` (model „Alfred") → `voice_assistant` → Home Assistant
(Assist: STT → konwersacja → TTS). Mikrofon INMP441 (I2S, 16 kHz, 32 bit), głośnik I2S 16 bit mono,
wyświetlacz z „twarzą" sterowany zmienną `va_state`.

## Kluczowa różnica: protokół

ESPHome `voice_assistant` mówi **natywnym API ESPHome do Home Assistanta**. Serwer XiaoZhi używa **innego protokołu**:

| | ESPHome → HA | XiaoZhi |
|---|---|---|
| Aktywacja/konfiguracja | API ESPHome (encrypted, port 6053) | `POST /xiaozhi/ota/` (HTTP) → zwraca adres WebSocket + token |
| Transport audio | strumień PCM/Opus przez API ESPHome | **WebSocket** `ws://host:8001/xiaozhi/v1/`, ramki **Opus** (16 kHz mono wejście, 24 kHz wyjście, 60 ms) |
| Sterowanie | zdarzenia `voice_assistant` | JSON: `hello`, `listen` (start/stop/detect), `tts` (start/stop/sentence_start), `stt`, `llm` (emocje), `abort` |
| STT/LLM/TTS | pipeline HA | po stronie serwera (konfigurowane w panelu) |

**Wniosek: samego `voice_assistant` nie da się przekierować na XiaoZhi.** ESPHome nie ma komponentu klienta XiaoZhi.
Trzeba albo (A) napisać własny komponent/klienta WebSocket+Opus, albo (B) wgrać oryginalne firmware `xiaozhi-esp32` (ESP-IDF, C++).

## Co sprawdziłem na serwerze

- `GET :8002/` → panel zarządzania (nginx), działa.
- `POST :8002/xiaozhi/ota/` (z `Device-Id`) → odpowiada poprawnie, **ale zwraca adresy placeholderowe**:
  - `websocket.url = ws://xiaozhi.server.com:8001/xiaozhi/v1/`
  - `activation.message = http://xiaozhi.server.com ...`
  - GET na OTA bez nagłówków: „OTA接口不正常，缺少websocket地址 … 参数管理 → server.websocket".
  - Czyli w panelu **nie jest ustawiony parametr `server.websocket`** (i `server.fronted_url`).
- `:8001/xiaozhi/v1/` – zwykły GET i próba handshake WebSocket dają `404 Not found` (tekst w stylu Go/nginx, nie typowa odpowiedź
  Pythonowego serwera XiaoZhi). **Nie wiem, czy port 8000 jest w ogóle serwerem WebSocket XiaoZhi** – wymaga weryfikacji
  (docker-compose / reverse proxy). W instalacji standardowej `xiaozhi-server` słucha na 8000 (WS) i 8003 (HTTP/vision);
  8003 u Ciebie nie odpowiada.
- Uwaga: moje testowe żądanie OTA zarejestrowało w panelu fikcyjne urządzenie `aa:bb:cc:dd:ee:ff` (kod aktywacji 103680).
  Można je usunąć w panelu (Zarządzanie urządzeniami).

## Czego potrzebuję / co musisz zrobić na serwerze

1. **Panel → Zarządzanie parametrami**: ustaw
   - `server.websocket` = `ws://192.168.1.67:8001/xiaozhi/v1/` (i ewentualnie drugi adres po przecinku/średniku),
   - `server.ota` = `http://192.168.1.67:8002/xiaozhi/ota/`,
   - `server.fronted_url` = `http://192.168.1.67:8002`.
2. Potwierdź, że **port 8000 jest otwarty i obsługuje WebSocket** (`docker ps`, mapowanie portów, logi kontenera `xiaozhi-esp32-server`).
3. W panelu skonfiguruj modele (to decyduje o jakości!):
   - **ASR**: FunASR/SenseVoice (lokalnie) albo chmurowe (Azure/Google/OpenAI Whisper) – **sprawdź obsługę polskiego**; SenseVoice
     obsługuje głównie zh/en/ja/ko/yue, polski jest słaby → dla PL lepszy Whisper/Azure/Google.
   - **LLM**: OpenAI/Gemini/Ollama itd. (u mnie w repo są już sensory kosztów OpenAI – można zostać przy OpenAI).
   - **TTS**: Edge TTS (`pl-PL-ZofiaNeural`/`MarekNeural`) – darmowy i dobry po polsku; alternatywnie Azure/OpenAI TTS.
4. Utwórz agenta (osobowość, prompt po polsku, język) i **dodaj urządzenie**: po pierwszym połączeniu płytka dostaje 6-cyfrowy
   kod aktywacji (pokazywany na ekranie/w logach) → wpisz go w panelu.
5. (Opcjonalnie) Integracja z Home Assistant: XiaoZhi ma plugin `hass_get_state`/`hass_set_state` (potrzebny `HA_URL` + long-lived token,
   który już mam w `.env` jako `HA_TOKEN`) – sterowanie domem przez głos zostaje.

## Opcje wdrożenia na płytce

### A. Własny klient XiaoZhi w ESPHome (custom component)
- Zostaje: ESPHome, wyświetlacz, `micro_wake_word` („Alfred"), HA jako urządzenie (przyciski, sensory, OTA).
- Do napisania (C++ external component): klient WebSocket (`esp_websocket_client` z ESP-IDF), kodek **Opus** (biblioteka `esp-opus`/
  `esp_audio_codec`), maszyna stanów `hello → listen → tts`, mapowanie na `va_state`.
- Zalety: zachowujemy cały obecny projekt. Wady: **największy nakład pracy**, RAM (Opus enkoder + bufory; mamy 8 MB PSRAM – OK),
  ryzyko niezgodności z wersją protokołu serwera; WS w ESPHome 2026.10 nie ma gotowego komponentu.

### B. Oryginalne firmware `xiaozhi-esp32` (ESP-IDF)
- Wgrywamy gotowy projekt, konfigurujemy własną płytkę (piny z `esp_ver2.yaml`: mic GPIO4/5/6, głośnik GPIO7/8/18, wyświetlacz),
  podajemy URL OTA `http://192.168.1.67:8002/xiaozhi/ota/`.
- Zalety: działa od ręki, pełna zgodność z serwerem, wake word (ESP-SR), AEC, emocje na wyświetlaczu.
- Wady: **tracimy ESPHome** (HA-owe encje, nasz wake word „Alfred", twarz robota, wygaszacz Matrix – trzeba przepisać);
  wake word w ESP-SR to tylko wybrane słowa (własne wymaga treningu w ekosystemie Espressif); polski wake word problematyczny.

### C. Hybryda (rekomendowana do rozważenia)
Zostać na ESPHome + HA, a **poprawę jakości uzyskać wewnątrz pipeline'u HA**, wskazując lepsze STT/TTS/LLM
(np. Whisper/Piper albo chmurowe) – bez zmiany protokołu. Jeśli XiaoZhi ma być wartością samą w sobie (osobowość agenta, pamięć,
emocje, MCP, voiceprint), to opcja A lub B.

## Rekomendacja

Jakość odpowiedzi zależy głównie od wybranych ASR/LLM/TTS, a nie od serwera jako takiego. XiaoZhi daje wygodny panel i strumieniowanie
(niska latencja), ale **polski wymaga świadomego doboru ASR/TTS**.
- Najszybsza droga do testu jakości: **B na drugiej płytce / tymczasowo** (backup obecnego YAML jest w git) – pozwala ocenić serwer
  bez pisania kodu.
- Docelowo przy zachowaniu ESPHome: **A**, ale to projekt na kilka dni pracy.

## Plan prac na branchu

1. [ ] Naprawa `server.websocket` / weryfikacja portu 8000 na serwerze (po Twojej stronie / za zgodą).
2. [ ] Wybór ASR/LLM/TTS w panelu i test z przeglądarki/klienta testowego (`test_page.html` z repo xiaozhi-server).
3. [ ] Decyzja A vs B vs C.
4. [ ] (A) szkielet komponentu `components/xiaozhi/` + testowe połączenie WS z `Device-Id` = MAC płytki.
5. [ ] Mapowanie stanów na `va_state`, wyświetlacz i wake word.

## Pytania do Ciebie

- Który wariant: A (klient w ESPHome), B (stock firmware na drugiej płytce) czy C?
- Czy XiaoZhi jest wdrożone w Dockerze i mam dostęp (SSH/`docker logs`) albo mogę zalogować się do panelu (login/hasło)?
- Jakie ASR/LLM/TTS chcesz użyć (język: polski)?

## Status (aktualizacja)

- Serwer naprawiony: OTA `http://192.168.1.67:8002/xiaozhi/ota/`, WebSocket **`ws://192.168.1.67:8001/xiaozhi/v1/`**
  (port 8000 był błędny). ASR: OpenAI `gpt-4o-mini-transcribe`, LLM: HA Conversation, TTS: Edge `pl-PL-ZofiaNeural`.
- Test serwera bez płytki: `scripts/xiaozhi_test.py` (wymaga aktywacji urządzenia testowego w panelu).
- **Wariant B** (stock firmware `78/xiaozhi-esp32`): płytka `alfred-s3` w `xiaozhi-firmware/` (piny z `esp_ver2.yaml`).

### Budowanie firmware (wariant B)

Stock firmware wymaga ESP-IDF >= 6.0.1 (zalecane `release/v6.1`); ESPHome używa IDF 5.5, więc potrzebny jest osobny.

```
git clone -b release/v6.1 --depth 1 --recursive --shallow-submodules https://github.com/espressif/esp-idf.git C:/xz/esp-idf
git clone --depth 1 https://github.com/78/xiaozhi-esp32.git C:/xz/xiaozhi-esp32
# PowerShell, krótkie ścieżki:
$env:IDF_TOOLS_PATH='C:\xz\idf-tools'; C:\xz\esp-idf\install.ps1 esp32s3; . C:\xz\esp-idf\export.ps1
python xiaozhi-firmware/apply.py C:/xz/xiaozhi-esp32
cd C:/xz/xiaozhi-esp32; python scripts/build.py alfred-s3 --language pl-PL
idf.py -p COM4 flash   # pierwsze wgranie przez USB; potem OTA z serwera (panel: zarządzanie firmware)
```

Powrót do ESPHome: `scripts/deploy.sh COM4` (nadpisuje firmware przez USB).
