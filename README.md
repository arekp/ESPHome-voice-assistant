# ESPHome Voice Assistant

Asystent głosowy oparty na ESP32-S3 N16R8 z lokalnym wykrywaniem słowa budzącego dla integracji z Home Assistant.

## Opis

Ten projekt dostarcza kompletną konfigurację ESPHome do budowy asystenta głosowego używającego ESP32-S3 z lokalnym wykrywaniem słowa budzącego. System bezproblemowo integruje się z Home Assistant do sterowania inteligentnym domem.

## 🛠️ Wymagany Sprzęt
1. **ESP32-S3 DevKitC-1** (Zalecana wersja N16R8 lub N8R8)
2. **Wyświetlacz:** 1.28" Round IPS LCD (Sterownik GC9A01)
3. **Mikrofon:** INMP441 (I2S, dookólny)
4. **Wzmacniacz/DAC:** MAX98357A (I2S, 3W)
5. Głośnik: 4Ω 3W

## 🔌 Schemat Połączeń (Pinout)

### ✅ Aktualne okablowanie (zgodne z `esp_ver2.yaml`, przetestowane)

| Moduł | Sygnał → GPIO | Zasilanie |
| :--- | :--- | :--- |
| Mikrofon INMP441 (sekcja 1_v5) | WS→4, SCK→5, SD→6, L/R→GND | 3V3 |
| Wzmacniacz MAX98357A (sekcja 2_1) | LRC→7, BCLK→8, DIN→18 | **3V3** (tymczasowo, patrz niżej) |
| Wyświetlacz GC9A01 (sekcja 3) | DC→9, CS→10, SDA→11, SCL→12, RES→13, BLK→14 | 3V3 |

⚠️ **Pin 5V na klonach ESP32-S3 N16R8 może nie mieć napięcia.** Obok pinu jest zworka
lutownicza **IN-OUT** – dopóki nie jest zlutowana, pin 5V nie dostaje zasilania z USB i
wzmacniacz milczy (firmware „gra”, ale nic nie słychać). Obecnie MAX98357A jest zasilany z 3V3
(działa, ciszej). Docelowo: zlutować IN-OUT i przepiąć Vin na 5V.

Pozostałe tabele poniżej to historia testowanych wariantów pinów.

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

### 1_v2. Mikrofon (INMP441) _V2 dla plytki ver MON16R8
| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO 15 | Word Select |
| **SCK** | GPIO 16 | Zegar |
| **SD** | GPIO 17 | Dane wyjściowe |

### 1_v3. Mikrofon (INMP441) _V3 dla plytki ver MON16R8
Zmień piny magistrali wejściowej (mikrofonu): Piny 36 i 37 na S3 z 8MB PSRAM prawie na pewno kolidują z pamięcią. Spróbuj użyć pinów, które nie należą do zakresu 33-37.
| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO 36 | Word Select |
| **SCK** | GPIO 37 | Zegar |
| **SD** | GPIO 39 | Dane wyjściowe |

### 1_v4. Mikrofon (INMP441) _V3 dla plytki ver MON16R8 - do opracowania 

| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO3  | Word Select |
| **SCK** | GPIO2  | Zegar |
| **SD** | GPIO1  | Dane wyjściowe |

### 1_v5. Mikrofon (INMP441) _V3 dla plytki ver MON16R8 - do opracowania 

| Pin INMP441 | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **VDD** | **3.3V** | ⚠️ Podłączenie pod 5V uszkodzi mikrofon! |
| **GND** | GND | |
| **L/R** | GND | Wybór kanału Lewego |
| **WS** | GPIO4  | Word Select |
| **SCK** | GPIO5  | Zegar |
| **SD** | GPIO6 | Dane wyjściowe |

----
### 2. Głośnik (MAX98357A)
| Pin MAX98357A | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **Vin** | **5V (VBUS)** | Zalecane 5V dla lepszej jakości dźwięku |
| **GND** | GND | Wspólna masa |
| **LRC** | GPIO 4 | Word Select |
| **BCLK** | GPIO 5 | Bit Clock |
| **DIN** | GPIO 6 | Dane wejściowe |

### 2_1. Głośnik (MAX98357A)
| Pin MAX98357A | Pin ESP32-S3 | Uwagi |
| :--- | :--- | :--- |
| **Vin** | **5V (VBUS)** | Zalecane 5V dla lepszej jakości dźwięku |
| **GND** | GND | Wspólna masa |
| **LRC** | GPIO 7 | Word Select |
| **BCLK** | GPIO 8 | Bit Clock |
| **DIN** | GPIO 18 | Dane wejściowe |


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
1.  **Piny 4-8 i 18 (Audio):** Nie kolidują z Octal PSRAM (GPIO 33-37) ani z pinami bootowania (GPIO 0, 3, 45, 46). Mikrofon i głośnik mają osobne magistrale I2S.
2.  **Piny 9-14 (SPI):** Są zgrupowane fizycznie blisko siebie na DevKicie, co ułatwia prowadzenie przewodów, i nie kolidują z pamięcią Octal SPI Flash/PSRAM (która zajmuje piny 26-32).
3.  **MAX98357A:** Ten układ automatycznie miksuje kanał lewy i prawy do mono, jeśli pin SD jest niepodłączony, co jest idealne dla prostego asystenta głosowego.

### 1. Konfiguracja Home Assistant

Zainstaluj wymagane dodatki Home Assistant:
- **Whisper** - Zamiana mowy na tekst
- **Piper** - Zamiana tekstu na mowę
- **Voice Assist** - Potok głosowy

W **Ustawienia → Asystenci głosowi** asystent używany przez urządzenie musi mieć istniejącego
agenta konwersacji (np. `OpenAI Conversation` albo `Home Assistant`), STT (Whisper) i TTS (Piper).
Nieistniejący agent powoduje natychmiastowy błąd `intent-not-supported` po słowie budzącym.

### 2. Konfiguracja ESPHome

Główny plik to `esp_ver2.yaml`. Sekrety (WiFi, klucz API, hasło OTA) trzymamy w `.env`
(wzór: `.env.example`), z którego `scripts/env2secrets.py` generuje `secrets.yaml`.

### 🚀3. Flashowanie i development

Pełna instrukcja budowy środowiska, kompilacji, wgrywania (kablem i przez WiFi) oraz
diagnostyki: **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**. W skrócie:

```bash
scripts/deploy.sh COM4                    # pierwszy raz kablem
scripts/deploy.sh voice-assistant.local   # potem przez WiFi
```

## Funkcje

- **Lokalne Wykrywanie Słowa Budzącego**: "Okay Nabu" przy użyciu Micro Wake Word (aktywne, gdy HA jest połączony)
- **Animowana twarz** na okrągłym wyświetlaczu, pokazująca stan asystenta
- **Przyciski testowe**: Test RTTTL (dźwięk), Wymuś Nasłuch, Restart
- **OTA Updates**: Aktualizacje oprogramowania przez sieć
- **Redukcja Szumów i auto-gain** mikrofonu

## Użycie

1. Powiedz "Okay Nabu" aby aktywować
2. Oczy robią się **zielone** – mów polecenie
3. **Żółte** podskakujące oczy – asystent myśli
4. **Niebieskie** oczy z ustami – asystent odpowiada z głośnika
5. Powrót do białych, mrugających oczu

## Szczegóły Konfiguracji

### Ustawienia Audio
```yaml
bits_per_sample: 32bit
 sample_rate: 16000
 noise_suppression_level: 2.0
 volume_multiplier: 4.0
```


## Integracja

Asystent integruje się z encjami Home Assistant dla:
- Sterowania oświetleniem
- Sterowania przełącznikami
- Odtwarzania mediów
- Własnych skryptów

## Rozwiązywanie Problemów

### Częste Problemy
- **Brak wyjścia audio** (a w logach `rtttl: Playing song` / `i2s_audio.speaker: Starting`):
  brak napięcia na pinie 5V – zlutuj zworkę IN-OUT albo zasil MAX98357A z 3V3.
  Test: `scripts/button.py RTTTL` powinien dać dwa piknięcia.
- **Oczy nie zmieniają się po "Okay Nabu"**: sprawdź logi – jeśli jest `intent-not-supported`,
  asystent w HA ma ustawionego nieistniejącego agenta konwersacji.
- **Słowo budzące w ogóle nie działa**: wykrywanie startuje dopiero po połączeniu z Home Assistant.

Pełna lista rozwiązanych problemów: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#7-rozwiązane-problemy-październik-2026).

### Tryb Debug
Logi przez WiFi: `esphome logs esp_ver2.yaml --device voice-assistant.local`
(albo kablem na COM4 – logger działa na `UART0`).

## Zasoby

- [Dokumentacja ESPHome](https://esphome.io/)
- [Micro Wake Word](https://github.com/kahrendt/microWakeWord)
- [Home Assistant Voice](https://www.home-assistant.io/blog/2023/12/13/year-of-the-voice-chapter-5/)
- [film prezentujacy asystenata](https://youtu.be/aDaSp6zaqWM?is=lCuZWlRpG83gZBLt)
- [Dokumentacja wyswietlacza](https://sklep.msalamon.pl/produkt/okragly-wyswietlacz-tft-ips-128-niebiesk/?srsltid=AfmBOor6AoACia8Q1M1vcqE8KNbGT7DDmXIn7yjRObGVehSrhEy6dq4l)
- [kolejny przyklad implementacji](https://www.instructables.com/DIY-Pocket-Size-ESP32-AI-Voice-Assistant-With-Xiao/?utm_source=newsletter&utm_medium=email)
- [Pobieranie slow wybudzenia](https://github.com/esphome/micro-wake-word-models/blob/main/models/v2/hey_jarvis.json)

## Licencja

Licencja MIT - Szczegóły w pliku LICENSE.
