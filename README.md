# ESPHome Voice Assistant

Asystent głosowy oparty na ESP32-S3 z lokalnym wykrywaniem słowa budzącego dla integracji z Home Assistant.

## Opis

Ten projekt dostarcza kompletną konfigurację ESPHome do budowy asystenta głosowego używającego ESP32-S3 z lokalnym wykrywaniem słowa budzącego. System bezproblemowo integruje się z Home Assistant do sterowania inteligentnym domem.

## Wymagania Sprzętowe

- **ESP32-S3** (zalecany ESP32-S3-DevKitC-1)
- **INMP441** mikrofon MEMS
- **MAX98357A** wzmacniacz audio/DAC
- **WS2812** pasek LED (8 diod)
- **Głośnik 3W** (zalecany Dayton Audio DMA45-4)

## Schemat Połączeń (Pinout)

Poniższa tabela przedstawia bezpieczne połączenia dla **ESP32-S3 DevKitC-1**, które nie kolidują z pamięcią Flash/PSRAM oraz wbudowanymi funkcjami.

### 1. Wzmacniacz Audio (MAX98357A)
Wzmacniacz obsługuje komunikację I2S dla głośnika.

| MAX98357A Pin | ESP32-S3 GPIO | Opis |
| :--- | :--- | :--- |
| **Vin** | 5V | Zasilanie (zalecane 5V dla większej mocy) |
| **GND** | GND | Masa |
| **LRC (WS)** | GPIO 45 | Word Select / Left-Right Clock |
| **BCLK** | GPIO 47 | Bit Clock |
| **DIN** | GPIO 48 | Data In |
| **SD** | Niepodłączony | Tryb Stereo/Mute (opcjonalnie) |

### 2. Wyświetlacz LCD (GC9A01 - SPI)
Okrągły wyświetlacz 1.28" IPS.

| Wyświetlacz Pin | ESP32-S3 GPIO | Opis |
| :--- | :--- | :--- |
| **VCC** | 3.3V | Zasilanie |
| **GND** | GND | Masa |
| **SCL (SCK)** | GPIO 12 | SPI Clock |
| **SDA (MOSI)** | GPIO 11 | SPI Data |
| **RES** | GPIO 13 | Reset |
| **DC** | GPIO 9 | Data / Command Selection |
| **CS** | GPIO 10 | Chip Select |
| **BLK** | GPIO 14 | Podświetlenie (PWM) |

### 3. Mikrofon I2S (np. INMP441)
Jeśli używasz mikrofonu I2S, sugerowane piny:

| Mikrofon Pin | ESP32-S3 GPIO | Opis |
| :--- | :--- | :--- |
| **SCK** | GPIO 16 | Serial Clock |
| **WS** | GPIO 15 | Word Select |
| **SD** | GPIO 17 | Serial Data |

---

## Konfiguracja Oprogramowania

Upewnij się, że w Twoim pliku `.yaml` sekcje `i2s_audio` i `display` korzystają z powyższych pinów.

### Dlaczego takie piny?
1.  **Piny 45, 47, 48 (Audio):** Są to piny często używane w zestawach deweloperskich ESP32-S3 do audio, są bezpieczne i nie kolidują z systemem bootowania (w przeciwieństwie do np. GPIO 0 czy GPIO 46 w niektórych stanach).
2.  **Piny 9-14 (SPI):** Są zgrupowane fizycznie blisko siebie na DevKicie, co ułatwia prowadzenie przewodów, i nie kolidują z pamięcią Octal SPI Flash/PSRAM (która zajmuje piny 26-32).
3.  **MAX98357A:** Ten układ automatycznie miksuje kanał lewy i prawy do mono, jeśli pin SD jest niepodłączony, co jest idealne dla prostego asystenta głosowego.

### 1. Konfiguracja Home Assistant

Zainstaluj wymagane dodatki Home Assistant:
- **Whisper** - Zamiana mowy na tekst
- **Piper** - Zamiana tekstu na mowę
- **Voice Assist** - Potok głosowy

### 2. Konfiguracja ESPHome

Skopiuj `esphome.yaml` do dashboardu ESPHome i skonfiguruj:
- Dane WiFi (`!secret wifi_ssid`, `!secret wifi_password`)
- Klucz szyfrowania API Home Assistant

### 3. Flashowanie

Flashuj ESP32-S3 DevKitC-1 przy użyciu web flashera ESPHome lub CLI.

## Funkcje

- **Lokalne Wykrywanie Słowa Budzącego**: "hey_jarvis" przy użyciu Micro Wake Word
- **Feedback LED**: Pasek LED RGB z efektem skanowania przy słowie budzącym
- **Kontrola Wyciszenia**: Przycisk wyciszenia dla prywatności
- **OTA Updates**: Aktualizacje oprogramowania przez sieć
- **Redukcja Szumów**: Zaawansowana obróbka audio
- **Kontrola Głośności**: Konfigurowalne wyjście audio

## Użycie

1. Powiedz "hey_jarvis" aby aktywować
2. Pasek LED zeskanuje i zmieni kolor na biały
3. Mów polecenie po sygnale
4. Asystent przetwarza i odpowiada
5. LED wyłącza się po zakończeniu

## Szczegóły Konfiguracji

### Ustawienia Audio
```yaml
bits_per_sample: 32bit
 sample_rate: 16000
 noise_suppression_level: 2.0
 volume_multiplier: 4.0
```

### Efekty LED
- **Bezczynność**: Zielone pulsowanie
- **Słowo Budzące**: Białe skanowanie
- **Słuchanie**: Białe stałe
- **Przetwarzanie**: Niebieskie szybkie pulsujące

## Integracja

Asystent integruje się z encjami Home Assistant dla:
- Sterowania oświetleniem
- Sterowania przełącznikami
- Odtwarzania mediów
- Własnych skryptów

## Rozwiązywanie Problemów

### Częste Problemy
- **Brak wyjścia audio**: Sprawdź połączenie 5V MAX98357A
- **Nie wykryto słowa budzącego**: Dostosuj wzmocnienie mikrofonu
- **LED nie działa**: Sprawdź pin danych WS2812

### Tryb Debug
Włącz logowanie w ESPHome dla szczegółowej diagnostyki:
```yaml
logger:
  level: DEBUG
```

## Zasoby

- [Dokumentacja ESPHome](https://esphome.io/)
- [Micro Wake Word](https://github.com/kahrendt/microWakeWord)
- [Home Assistant Voice](https://www.home-assistant.io/blog/2023/12/13/year-of-the-voice-chapter-5/)
- [film prezentujacy asystenata](https://youtu.be/aDaSp6zaqWM?is=lCuZWlRpG83gZBLt)

## Licencja

Licencja MIT - Szczegóły w pliku LICENSE.
