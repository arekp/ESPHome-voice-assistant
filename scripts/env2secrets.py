"""Generuje secrets.yaml (dla !secret w ESPHome) z pliku .env.

Użycie: .venv/Scripts/python.exe scripts/env2secrets.py [.env] [secrets.yaml]
Klucz WIFI_SSID w .env trafia do secrets.yaml jako wifi_ssid itd.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ["WIFI_SSID", "WIFI_PASSWORD", "FALLBACK_AP_PASSWORD", "API_KEY", "OTA_PASSWORD"]


def read_env(path: Path) -> dict:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def main() -> int:
    env_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / ".env"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "secrets.yaml"

    if not env_path.is_file():
        print(f"Brak {env_path} - skopiuj .env.example do .env i uzupełnij.", file=sys.stderr)
        return 1

    values = read_env(env_path)
    missing = [k for k in REQUIRED if not values.get(k)]
    if missing:
        print(f"Puste lub brakujące w {env_path.name}: {', '.join(missing)}", file=sys.stderr)
        return 1

    lines = ["# Wygenerowane z .env przez scripts/env2secrets.py - nie edytuj ręcznie."]
    # json.dumps daje poprawny łańcuch YAML w cudzysłowie (escapowanie znaków specjalnych)
    lines += [f"{k.lower()}: {json.dumps(v, ensure_ascii=False)}" for k, v in values.items()]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Zapisano {out_path.name} ({len(values)} wpisów)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
