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

## Schemat Połączeń

```
ESP32-S3        INMP441        MAX98357A        WS2812
--------------- --------------- --------------- -------------
3V3             VCC             5V              VCC
GND             GND             GND             GND
GPIO6           LRC             -               -
GPIO7           BLCK            -               -
GPIO4           SD              -               -
GPIO8           -               DIN             -
GPIO16          -               -               DIN
GPIO48          -               -               (LED wbudowany)
```

**Uwagi:**
- Podłącz 5V do MAX98357A dla lepszej jakości audio
- Używaj kabli 20 AWG do połączeń
- Dodaj rezystor 20Ω do głośnika dla redukcji głośności

## Konfiguracja Oprogramowania

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

Flashuj ESP32-S3 przy użyciu web flashera ESPHome lub CLI.

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

## Licencja

Licencja MIT - Szczegóły w pliku LICENSE.