#!/usr/bin/env python3
"""Test end-to-end serwera XiaoZhi bez płytki: OTA -> WebSocket -> polskie audio (Opus) -> odpowiedź.

Zależności (osobny venv, nie .venv ESPHome): pip install websockets av edge-tts

  python scripts/xiaozhi_test.py --mac 02:00:00:00:00:01 --text "Która jest godzina?"

Pierwsze uruchomienie dla nowego MAC wypisze kod aktywacji – wpisz go w panelu
(http://HOST:8002 -> Urządzenia) i uruchom ponownie. Odpowiedź audio ląduje w logs/xiaozhi_reply.wav.
"""
import argparse
import asyncio
import json
import sys
import tempfile
import time
import urllib.request
import wave
from pathlib import Path

import av
import edge_tts
import websockets

FRAME_MS = 60


def ota(host, mac):
    body = json.dumps({"application": {"version": "1.0.0"}, "board": {"type": "esp32s3"}}).encode()
    req = urllib.request.Request(f"http://{host}:8002/xiaozhi/ota/", data=body,
                                 headers={"Device-Id": mac, "Client-Id": "xiaozhi-test",
                                          "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=10))


async def synth_pcm(text, voice, rate=16000):
    """Edge TTS -> PCM s16 mono 16 kHz (symuluje mowę użytkownika)."""
    with tempfile.TemporaryDirectory() as d:
        mp3 = Path(d) / "in.mp3"
        await edge_tts.Communicate(text, voice).save(str(mp3))
        out = bytearray()
        res = av.AudioResampler(format="s16", layout="mono", rate=rate)
        with av.open(str(mp3)) as c:
            for fr in c.decode(audio=0):
                for r in res.resample(fr):
                    out += bytes(r.planes[0])[: r.samples * 2]
        for r in res.resample(None):
            out += bytes(r.planes[0])[: r.samples * 2]
    return bytes(out)


def opus_frames(pcm, rate):
    enc = av.CodecContext.create("libopus", "w")
    enc.sample_rate, enc.layout, enc.format = rate, "mono", "s16"
    enc.open()
    n = rate * FRAME_MS // 1000
    step = n * 2
    pcm += b"\x00" * (-len(pcm) % step)
    for i in range(0, len(pcm), step):
        fr = av.AudioFrame(format="s16", layout="mono", samples=n)
        fr.sample_rate = rate
        fr.planes[0].update(pcm[i:i + step])
        fr.pts = i // 2
        for p in enc.encode(fr):
            yield bytes(p)


def decode_opus(packets, rate):
    dec = av.CodecContext.create("libopus", "r")
    dec.sample_rate, dec.layout = rate, "mono"
    dec.open()
    out, real_rate = bytearray(), rate
    for pk in packets:
        for fr in dec.decode(av.Packet(pk)):
            real_rate = fr.sample_rate  # libopus zwraca 48 kHz niezależnie od nagłówka
            out += bytes(fr.planes[0])[: fr.samples * 2]
    return bytes(out), real_rate


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="192.168.1.67")
    ap.add_argument("--mac", default="02:00:00:00:00:01")
    ap.add_argument("--text", default="Cześć, powiedz mi coś o sobie.")
    ap.add_argument("--voice", default="pl-PL-MarekNeural")
    ap.add_argument("--out", default="logs/xiaozhi_reply.wav")
    a = ap.parse_args()

    info = ota(a.host, a.mac)
    if "activation" in info:
        print(f"URZĄDZENIE NIEAKTYWNE. Kod aktywacji: {info['activation']['code']}")
        print(f"Wpisz go w panelu http://{a.host}:8002 (Urządzenia) i uruchom skrypt ponownie.")
        return 2
    ws = info["websocket"]
    print("WebSocket:", ws["url"])

    pcm = await synth_pcm(a.text, a.voice)
    print(f"Nagranie testowe: {len(pcm) / 32000:.1f}s  tekst: {a.text!r}")

    headers = {"Authorization": "Bearer " + ws["token"], "Protocol-Version": "1",
               "Device-Id": a.mac, "Client-Id": "xiaozhi-test"}
    async with websockets.connect(ws["url"], additional_headers=headers, open_timeout=10) as w:
        await w.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket",
                                 "audio_params": {"format": "opus", "sample_rate": 16000,
                                                  "channels": 1, "frame_duration": FRAME_MS}}))
        srv = json.loads(await asyncio.wait_for(w.recv(), 10))
        print("hello serwera:", json.dumps(srv, ensure_ascii=False))
        if srv.get("type") != "hello":
            return 1
        down_rate = srv.get("audio_params", {}).get("sample_rate", 24000)
        sid = srv.get("session_id", "")

        await w.send(json.dumps({"session_id": sid, "type": "listen", "state": "start", "mode": "manual"}))
        for pkt in opus_frames(pcm, 16000):
            await w.send(pkt)
            await asyncio.sleep(FRAME_MS / 1000 * 0.5)  # szybciej niż real-time
        await w.send(json.dumps({"session_id": sid, "type": "listen", "state": "stop"}))
        t_stop = time.monotonic()

        audio, first_audio = [], None
        try:
            while True:
                m = await asyncio.wait_for(w.recv(), 20)
                if isinstance(m, bytes):
                    if first_audio is None:
                        first_audio = time.monotonic() - t_stop
                        print(f"  [{first_audio:6.2f}s] pierwszy dźwięk odpowiedzi")
                    audio.append(m)
                    continue
                j = json.loads(m)
                print(f"  [{time.monotonic() - t_stop:6.2f}s]", {k: v for k, v in j.items() if k != "session_id"})
                if j.get("type") == "tts" and j.get("state") == "stop":
                    break
        except asyncio.TimeoutError:
            print("Timeout oczekiwania na odpowiedź")

    if audio:
        Path(a.out).parent.mkdir(exist_ok=True)
        pcm_out, down_rate = decode_opus(audio, down_rate)
        with wave.open(a.out, "wb") as f:
            f.setnchannels(1), f.setsampwidth(2), f.setframerate(down_rate)
            f.writeframes(pcm_out)
        print(f"Zapisano {a.out} ({len(pcm_out) / 2 / down_rate:.1f}s, {down_rate} Hz, "
              f"{len(audio)} ramek = {len(audio) * FRAME_MS / 1000:.1f}s)")
    else:
        print("Brak audio w odpowiedzi.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
