"""Wysyła komendy WebSocket do Home Assistant i wypisuje wyniki (diagnostyka Assist).

Wymaga HA_URL i HA_TOKEN w .env.

Przykłady:
  .venv/Scripts/python.exe scripts/ha.py '{"type":"assist_pipeline/pipeline/list"}'
  .venv/Scripts/python.exe scripts/ha.py '{"type":"conversation/process","text":"Która godzina?","language":"pl"}'
"""
import asyncio
import json
import sys
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parent.parent


def read_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip("\"'")
    return env


async def main(commands: list) -> int:
    env = read_env()
    url = env["HA_URL"].rstrip("/").replace("http", "ws", 1) + "/api/websocket"
    async with websockets.connect(url, max_size=None) as ws:
        json.loads(await ws.recv())  # auth_required
        await ws.send(json.dumps({"type": "auth", "access_token": env["HA_TOKEN"]}))
        auth = json.loads(await ws.recv())
        if auth["type"] != "auth_ok":
            print("Błąd logowania:", auth, file=sys.stderr)
            return 1
        print("HA", auth.get("ha_version"))
        for msg_id, raw in enumerate(commands, 1):
            cmd = json.loads(raw)
            cmd["id"] = msg_id
            await ws.send(json.dumps(cmd))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == msg_id and msg["type"] == "result":
                    out = msg.get("result") if msg["success"] else msg.get("error")
                    print(json.dumps(out, ensure_ascii=False, indent=1))
                    break
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(asyncio.run(main(sys.argv[1:])))
