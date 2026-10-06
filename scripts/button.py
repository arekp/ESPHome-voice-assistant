"""Wciska przycisk na urządzeniu przez natywne API ESPHome (bez Home Assistant).

Użycie:
  .venv/Scripts/python.exe scripts/button.py            # lista przycisków
  .venv/Scripts/python.exe scripts/button.py RTTTL      # wciśnij przycisk, którego nazwa zawiera "RTTTL"
Host: zmienna ESP_DEVICE albo voice-assistant.local. Klucz API z secrets.yaml.
"""
import asyncio
import os
import sys
from pathlib import Path

import yaml
from aioesphomeapi import APIClient, ButtonInfo

ROOT = Path(__file__).resolve().parent.parent


async def main(name: str | None) -> int:
    key = yaml.safe_load((ROOT / "secrets.yaml").read_text(encoding="utf-8"))["api_key"]
    host = os.environ.get("ESP_DEVICE", "voice-assistant.local")
    client = APIClient(host, 6053, None, noise_psk=key)
    await client.connect(login=True)
    try:
        entities, _ = await client.list_entities_services()
        buttons = [e for e in entities if isinstance(e, ButtonInfo)]
        if not name:
            for b in buttons:
                print(b.name)
            return 0
        match = [b for b in buttons if name.lower() in b.name.lower()]
        if not match:
            print(f"Brak przycisku z '{name}'. Dostępne: {[b.name for b in buttons]}", file=sys.stderr)
            return 1
        client.button_command(match[0].key)
        print("Wciśnięto:", match[0].name)
        await asyncio.sleep(1)  # daj czas na wysłanie komendy
    finally:
        await client.disconnect()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None)))
