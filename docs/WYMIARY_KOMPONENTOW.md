# Wymiary komponentów elektronicznych

Wymiary w mm. ✅ – potwierdzone (rysunek producenta / sprzedawca), ⚠️ – przybliżone, ❌ – brak danych.

| # | Komponent | Wymiary modułu | Szczegóły | Pewność |
|---|---|---|---|---|
| 1 | **ESP32-S3 N16R8** – klon YD-ESP32-S3 (VCC-GND), 2× USB-C, CH343 | PCB **57,15 × 27,94 × 1,6**; z wystającym modułem WROOM (antena) **63,39** długości | 2 rzędy po 22 piny, raster 2,54, rozstaw rzędów **25,40**; moduł WROOM ok. 3,3 nad PCB, elementy nad PCB do ok. 4,5 | ✅ |
| 1a | Gniazda USB-C płytki | gniazdo ok. 9 × 3,2 | na krótszym brzegu (naprzeciw anteny), środki **8,1** i **19,8** mm od krawędzi płytki | ✅ |
| 2 | **Wyświetlacz okrągły 1,28" GC9A01** (msalamon) | **38 × 45,5 × 11,5** (z goldpinami) | obszar pikseli **Ø32,4**; szkło ok. Ø35,6; 8 wyprowadzeń | ✅ / szkło ⚠️ |
| 3 | **Mikrofon INMP441** (moduł I2S) | PCB ok. **14 × 14** (wersje okrągłe Ø15), gr. ok. 3 | port akustyczny – otwór w PCB | ⚠️ |
| 4 | **Wzmacniacz MAX98357A** (moduł I2S, 3 W) | **19,4 × 17,8 × 3** (klony ok. 18 × 18) | 7 pinów + złącze głośnika | ⚠️ |
| 5 | **Głośnik 4 Ω / 3 W** | ramka **63 × 63**, głębokość **12** | membrana (kosz) **Ø45** pośrodku ramki | ✅ (zmierzone) |

Wtyki dupont nałożone na goldpiny wystają ok. 14–17 mm od PCB.

## Do zmierzenia
1. Szkło wyświetlacza (średnica) i po której stronie modułu są piny.
2. Moduł INMP441: kształt (kwadrat / koło), położenie otworu akustycznego.
3. Klon MAX98357A: wymiary i czy ma złącze śrubowe głośnika.
4. Otwory montażowe modułów (średnica, położenie) – brak danych.

## Źródła
- [YD-ESP32-S3 – rysunek wymiarowy (vcc-gnd)](https://github.com/vcc-gnd/YD-ESP32-S3/tree/main/5-public-YD-ESP32-S3-Hardware%20info)
- [Wyświetlacz GC9A01 1,28" – msalamon](https://sklep.msalamon.pl/produkt/okragly-wyswietlacz-tft-ips-128-niebiesk/)
- [Waveshare 1.28inch LCD Module](https://www.waveshare.com/1.28inch-lcd-module.htm)
- [Adafruit MAX98357A](https://www.adafruit.com/product/3006)
- [INMP441 – TinyTronics](https://www.tinytronics.nl/en/sensors/sound/inmp441-mems-microphone-i2s)
- [INMP441 – datasheet (port akustyczny)](https://www.mouser.com/datasheet/2/400/INMP441-1112508.pdf)
