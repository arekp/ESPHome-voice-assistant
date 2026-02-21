# ESPHome Voice Assistant

ESP32-S3 based voice assistant with local wake word detection for Home Assistant integration.

## Overview

This project provides a complete ESPHome configuration for building a voice assistant using ESP32-S3 with local wake word detection. The system integrates seamlessly with Home Assistant for smart home control.

## Hardware Requirements

- **ESP32-S3** (ESP32-S3-DevKitC-1 recommended)
- **INMP441** MEMS microphone
- **MAX98357A** audio amplifier/DAC
- **WS2812** LED strip (8 LEDs)
- **3W speaker** (Dayton Audio DMA45-4 recommended)

## Circuit Diagram

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
GPIO48          -               -               (on-board LED)
```

**Notes:**
- Connect 5V to MAX98357A for better audio quality
- Use 20 AWG wires for connections
- Add 20Ω resistor to speaker for volume reduction

## Software Setup

### 1. Home Assistant Configuration

Install required Home Assistant Addons:
- **Whisper** - Speech-to-text
- **Piper** - Text-to-speech
- **Voice Assist** - Voice pipeline

### 2. ESPHome Configuration

Copy `esphome.yaml` to your ESPHome dashboard and configure:
- WiFi credentials (`!secret wifi_ssid`, `!secret wifi_password`)
- Home Assistant API encryption key

### 3. Flashing

Flash the ESP32-S3 using ESPHome web flasher or CLI.

## Features

- **Local Wake Word Detection**: "hey_jarvis" using Micro Wake Word
- **LED Feedback**: RGB LED bar with scanning effect on wake word
- **Mute Control**: Physical mute button for privacy
- **OTA Updates**: Over-the-air firmware updates
- **Noise Suppression**: Advanced audio processing
- **Volume Control**: Configurable audio output

## Usage

1. Say "hey_jarvis" to activate
2. LED bar will scan and turn white
3. Speak your command after the tone
4. Assistant processes and responds
5. LED turns off when done

## Configuration Details

### Audio Settings
```yaml
bits_per_sample: 32bit
 sample_rate: 16000
 noise_suppression_level: 2.0
 volume_multiplier: 4.0
```

### LED Effects
- **Idle**: Green pulsing
- **Wake Word**: White scanning
- **Listening**: White solid
- **Processing**: Blue fast pulse

## Integration

The assistant integrates with Home Assistant entities for:
- Light control
- Switch control
- Media playback
- Custom scripts

## Troubleshooting

### Common Issues
- **No audio output**: Check MAX98357A 5V connection
- **Wake word not detected**: Adjust microphone gain
- **LED not working**: Verify WS2812 data pin

### Debug Mode
Enable logging in ESPHome for detailed diagnostics:
```yaml
logger:
  level: DEBUG
```

## Resources

- [ESPHome Documentation](https://esphome.io/)
- [Micro Wake Word](https://github.com/kahrendt/microWakeWord)
- [Home Assistant Voice](https://www.home-assistant.io/blog/2023/12/13/year-of-the-voice-chapter-5/)

## License

MIT License - See LICENSE file for details.