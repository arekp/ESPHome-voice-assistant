#!/usr/bin/env python3
"""Wywołania REST API panelu XiaoZhi (manager-api) z tokenem sesji z .env.

  python scripts/xiaozhi.py GET /agent/list
  python scripts/xiaozhi.py POST /device/bind/<agentId>/<kod>
  python scripts/xiaozhi.py POST /agent '{"agentName":"Polski Asystent"}'

Token: zaloguj się w przeglądarce, DevTools -> Network -> dowolne zapytanie do /xiaozhi/ ->
nagłówek Authorization (sama wartość po "Bearer "), wpisz do .env jako XIAOZHI_TOKEN.
Opcjonalnie XIAOZHI_URL (domyślnie http://192.168.1.67:8002). Wygasa po kilku godzinach.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path


def env():
    out = {}
    p = Path(__file__).resolve().parent.parent / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    e = env()
    token = e.get("XIAOZHI_TOKEN")
    if not token:
        sys.exit("Brak XIAOZHI_TOKEN w .env")
    base = e.get("XIAOZHI_URL", "http://192.168.1.67:8002").rstrip("/") + "/xiaozhi"
    method, path = sys.argv[1].upper(), sys.argv[2]
    data = sys.argv[3].encode() if len(sys.argv) > 3 else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Authorization": "Bearer " + token,
                                          "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=15)
        body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as ex:
        body = ex.read().decode("utf-8", "replace")
    try:
        print(json.dumps(json.loads(body), ensure_ascii=False, indent=2))
    except ValueError:
        print(body)


if __name__ == "__main__":
    main()
