# ESPHome Voice Assistant

Asystent głosowy oparty na ESP32-S3 z lokalnym wykrywaniem słowa budzącego dla integracji z Home Assistant.

## Opis

Ten projekt dostarcza kompletną konfigurację ESPHome do budowy asystenta głosowego używającego ESP32-S3 z lokalnym wykrywaniem słowa budzącego. System bezproblemowo integruje się z Home Assistant do sterowania inteligentnym domem.

## 🛠️ Wymagany Sprzęt
1. **ESP32-S3 DevKitC-1** (Zalecana wersja N16R8 lub N8R8)
2. **Wyświetlacz:** 1.28" Round IPS LCD (Sterownik GC9A01)
3. **Mikrofon:** INMP441 (I2S, dookólny)
4. **Wzmacniacz/DAC:** MAX98357A (I2S, 3W)
5. Głośnik: 4Ω 3W

## 🔌 Schemat Połączeń (Pinout)

Poniższa tabela przedstawia bezpieczne połączenia dla **ESP32-S3 DevKitC-1**, które nie kolidują z pamięcią Flash/PSRAM oraz wbudowanymi funkcjami.

### 1. Mikrofon (INMP441)
⚠️ Krytyczne ostrzeżenie o pinach
W układach ESP32-S3 z Octal PSRAM (N16R8), piny od GPIO 33 do GPIO 37 oraz GPIO 40, 41 i 42 są wykorzystywane wewnętrznie do komunikacji z pamięcią RAM i Flash.
| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO 40 | Word Select |
| **SCK** | GPIO 41 | Zegar |
| **SD** | GPIO 42 | Dane wyjściowe |

### 1. Mikrofon (INMP441) _V2 dla plytki ver MON16R8
| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO 15 | Word Select |
| **SCK** | GPIO 16 | Zegar |
| **SD** | GPIO 17 | Dane wyjściowe |

### 1. Mikrofon (INMP441) _V3 dla plytki ver MON16R8
| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO 36 | Word Select |
| **SCK** | GPIO 37 | Zegar |
| **SD** | GPIO 39 | Dane wyjściowe |

### 2. Głośnik (MAX98357A)
| Pin MAX98357A | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **Vin** | **5V (VBUS)** | Zalecane 5V dla lepszej jakości dźwięku |
| **GND** | GND | Wspólna masa |
| **LRC** | GPIO 4 | Word Select |
| **BCLK** | GPIO 5 | Bit Clock |
| **DIN** | GPIO 6 | Dane wejściowe |

### 3. Wyświetlacz (GC9A01)
| Pin GC9A01 | Pin ESP32-S3 | Funkcja |
| :--- | :--- | :--- |
| **VCC** | 3.3V | Zasilanie |
| **GND** | GND | Masa |
| **DC** | GPIO 9 | Data/Command |
| **CS** | GPIO 10 | Chip Select |
| **SDA** | GPIO 11 | SPI MOSI |
| **SCL** | GPIO 12 | SPI Clock |
| **RES** | GPIO 13 | Reset |
| **BLK** | GPIO 14 | Podświetlenie (PWM) |


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

### 🚀3. Flashowanie

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
- [Dokumentacja wyswietlacza](https://sklep.msalamon.pl/produkt/okragly-wyswietlacz-tft-ips-128-niebiesk/?srsltid=AfmBOor6AoACia8Q1M1vcqE8KNbGT7DDmXIn7yjRObGVehSrhEy6dq4l)
- [Pobieranie slow wybudzenia](https://github.com/esphome/micro-wake-word-models/blob/main/models/v2/hey_jarvis.json)

## Licencja

Licencja MIT - Szczegóły w pliku LICENSE.
