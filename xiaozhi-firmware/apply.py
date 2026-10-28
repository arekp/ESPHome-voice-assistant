#!/usr/bin/env python3
"""Dodaje płytkę alfred-s3 do sklonowanego repo 78/xiaozhi-esp32 (idempotentnie).

  python xiaozhi-firmware/apply.py C:/xz/xiaozhi-esp32
"""
import shutil
import sys
from pathlib import Path

src = Path(__file__).parent / "boards" / "alfred-s3"
up = Path(sys.argv[1])
dst = up / "main" / "boards" / "alfred-s3"
shutil.copytree(src, dst, dirs_exist_ok=True)

kc = up / "main" / "Kconfig.projbuild"
t = kc.read_text(encoding="utf-8")
if "BOARD_TYPE_ALFRED_S3" not in t:
    anchor = "    config BOARD_TYPE_BREAD_COMPACT_WIFI_LCD\n"
    add = ('    config BOARD_TYPE_ALFRED_S3\n'
           '        bool "Alfred ESP32-S3 (ESPHome-voice-assistant)"\n'
           '        depends on IDF_TARGET_ESP32S3\n')
    assert anchor in t
    kc.write_text(t.replace(anchor, add + anchor, 1), encoding="utf-8")

cm = up / "main" / "CMakeLists.txt"
t = cm.read_text(encoding="utf-8")
if "CONFIG_BOARD_TYPE_ALFRED_S3" not in t:
    anchor = "elseif(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI_LCD)\n"
    add = ('elseif(CONFIG_BOARD_TYPE_ALFRED_S3)\n'
           '    set(BOARD_DIR "alfred-s3")\n'
           '    set(BUILTIN_TEXT_FONT font_noto_sans_basic_16_4)\n'
           '    set(BUILTIN_ICON_FONT font_material_symbols_16_4)\n'
           '    set(DEFAULT_EMOJI_COLLECTION noto-color-emoji_32)\n')
    assert anchor in t
    cm.write_text(t.replace(anchor, add + anchor, 1), encoding="utf-8")
print("OK:", dst)
