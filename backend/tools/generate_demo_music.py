#!/usr/bin/env python3
"""
Генератор демо-музыки для Music Hub.

Все 9 композиций синтезируются кодом с нуля (оригинальные мелодии, без сэмплов),
поэтому авторских прав на них нет — они отдаются как CC0 / общественное достояние.
Готовые файлы уже лежат в backend/demo_music, этот скрипт нужен только если вы
захотите их пересоздать или изменить. Требуется: numpy и ffmpeg (для mp3).

    python tools/generate_demo_music.py
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT_DIR = Path(__file__).resolve().parents[1] / "demo_music"
rng = np.random.default_rng(2026)


# ---------- базовые кирпичики ----------
def midi(n): return 440.0 * 2.0 ** ((n - 69) / 12.0)
def time(d): return np.arange(int(d * SR)) / SR

def osc(kind, f, d):
    """Осцилляторы. saw/square/pulse строятся аддитивно и ограничены по полосе (до 10 кГц),
    чтобы не было алиасинга — иначе на электронных треках слышен резкий «песок»."""
    t = time(d)
    th = 2 * np.pi * f * t
    if kind == "sine": return np.sin(th)
    if kind == "tri": return 2 / np.pi * np.arcsin(np.sin(th))
    kmax = max(1, int(10000 / f))
    out = np.zeros_like(t)
    if kind == "saw":
        for k in range(1, kmax + 1): out += np.sin(k * th) / k
        return out * 2 / np.pi
    if kind == "square":
        for k in range(1, kmax + 1, 2): out += np.sin(k * th) / k
        return out * 4 / np.pi
    if kind == "pulse":  # скважность 25%
        dty = 0.25
        for k in range(1, kmax + 1):
            a = 2 * np.sin(2 * np.pi * k * dty) / (k * np.pi)
            b = 2 * (1 - np.cos(2 * np.pi * k * dty)) / (k * np.pi)
            out += a * np.cos(k * th) + b * np.sin(k * th)
        return out
    raise ValueError(kind)

def band_noise(n):
    """Шум в полосе примерно 3–11 кГц: звучит как тарелка/хэт, но без резкого «шипения» выше."""
    w = rng.standard_normal(n)
    return (lowpass(w, 2) - lowpass(w, 10)) * 1.6

def perc(d, tau, attack=0.004):
    """Быстрая атака и экспоненциальное затухание."""
    t = time(d); e = np.exp(-t / tau)
    a = max(1, int(attack * SR)); e[:a] *= np.linspace(0, 1, a)
    r = min(len(e), int(0.01 * SR)); e[-r:] *= np.linspace(1, 0, r)
    return e

def swell(d, attack, release):
    n = int(d * SR); e = np.ones(n)
    a = min(n, max(1, int(attack * SR))); r = min(n, max(1, int(release * SR)))
    e[:a] *= np.linspace(0, 1, a); e[-r:] *= np.linspace(1, 0, r)
    return e

def lowpass(x, k):
    return x if k <= 1 else np.convolve(x, np.ones(k) / k, mode="same")

def put(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i < 0 or i >= len(buf): return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain

def echo(x, delay=0.35, fb=0.4, mix=0.3, taps=6):
    out = x.copy()
    for i in range(1, taps + 1):
        d = int(delay * SR * i)
        if d >= len(x): break
        out[d:] += x[:-d] * mix * (fb ** (i - 1))
    return out

def ducking(length, beat, depth=0.65):
    """Имитация sidechain: звук проседает на каждом ударе бочки."""
    tt = np.arange(length) / SR
    return 1 - depth * np.exp(-(tt % beat) * 9)


# ---------- инструменты ----------
def piano(m, d):
    f = midi(m); t = time(d); sig = np.zeros_like(t)
    stretch = 1 + max(0, m - 60) / 48
    for k in range(1, 9):
        if f * k > 9000: break
        sig += (1 / k ** 1.25) * np.sin(2 * np.pi * f * k * t * (1 + 0.0003 * k * k)) * np.exp(-t * (0.8 + 0.7 * k) * stretch)
    return sig * swell(d, 0.003, min(0.15, d / 3))

def rhodes(m, d):
    f = midi(m); t = time(d)
    sig = (np.sin(2 * np.pi * f * t)
           + 0.45 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
           + 0.12 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 14))
    return sig * np.exp(-t * 1.6) * swell(d, 0.004, 0.12)

def bell(m, d):
    f = midi(m); t = time(d)
    sig = (np.sin(2 * np.pi * f * t)
           + 0.5 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 2.5)
           + 0.25 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 5))
    return sig * np.exp(-t * 0.9) * swell(d, 0.003, 0.2)

def sub_bass(m, d):
    f = midi(m); t = time(d)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)) * np.exp(-t * 3) * swell(d, 0.005, 0.05)

def kick(d=0.3):
    t = time(d); f = 48 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)

def snare(d=0.22):
    t = time(d); n = band_noise(len(t))
    return (0.7 * n * np.exp(-t * 20) + 0.5 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28)) * 0.6

def clap(d=0.25):
    t = time(d); n = band_noise(len(t))
    return n * (np.exp(-t * 22) + 0.6 * np.exp(-np.clip(t - 0.012, 0, None) * 22)) * 0.5

def hat(d=0.08, tau=0.02):
    t = time(d); n = band_noise(len(t))
    return n * np.exp(-t / tau) * 0.35

def finish(buf, total):
    x = buf[: int((total + 3) * SR)].copy()
    x = x / np.max(np.abs(x)) * 0.89
    fi, fo = int(0.2 * SR), int(2.5 * SR)
    x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo)
    return x


# ---------- композиции ----------
def slow_tide():
    chords = [[45, 57, 60, 64, 67, 71], [41, 53, 57, 60, 64], [36, 55, 59, 64, 67], [43, 50, 55, 59, 62, 64]]
    seg = 11.0; total = len(chords) * seg
    buf = np.zeros(int((total + 6) * SR))
    for i, ch in enumerate(chords):
        d = seg + 3
        for m in ch:
            f = midi(m)
            voice = (osc("sine", f - 0.35, d) + osc("sine", f, d) + osc("sine", f + 0.35, d)) / 3
            put(buf, voice * swell(d, 3, 3), i * seg, 0.5 / len(ch) * 2)
    pent = [69, 72, 74, 76, 79, 81]
    for t in np.arange(2, total, 3.4):
        put(buf, bell(int(rng.choice(pent)), 4.0), t + rng.uniform(-0.6, 0.6), 0.16)
    return finish(echo(buf, 0.45, 0.5, 0.35), total)

def glass_hours():
    chords = [[38, 50, 53, 57, 62], [34, 46, 50, 53, 58], [41, 48, 53, 57, 60], [36, 48, 52, 55, 60]]
    seg = 11.0; total = len(chords) * seg
    buf = np.zeros(int((total + 6) * SR))
    for i, ch in enumerate(chords):
        d = seg + 3
        for m in ch:
            put(buf, osc("tri", midi(m), d) * swell(d, 3, 3), i * seg, 0.16)
        arp = ch[1:]; seq = arp + arp[-2:0:-1]
        k = 0
        while k * 0.95 < seg:
            put(buf, bell(seq[k % len(seq)] + 12, 3.5), i * seg + k * 0.95, 0.2)
            k += 1
    return finish(echo(buf, 0.5, 0.45, 0.3), total)

def lofi(bpm, chords, roots, bars, melody_scale, seed, swing=0.14):
    lr = np.random.default_rng(seed)
    beat = 60 / bpm; step = beat / 2; bar = beat * 4; total = bars * bar
    buf = np.zeros(int((total + 4) * SR))
    for b in range(bars):
        c, r, t0 = chords[b % len(chords)], roots[b % len(roots)], b * bar
        for hit, dur in ((0, 1.8), (2.5, 1.2)):
            for j, m in enumerate(c):
                put(buf, rhodes(m, dur * beat + 0.3), t0 + hit * beat + j * 0.018, 0.17)
            put(buf, sub_bass(r, 1.2 * beat), t0 + hit * beat, 0.34)
        for s in range(8):
            ts = t0 + s * step + (swing * step if s % 2 else 0)
            if s in (0, 5): put(buf, kick(), ts, 0.9)
            if s in (2, 6): put(buf, snare(), ts, 0.7)
            if lr.random() > 0.12: put(buf, hat(), ts, 0.5 if s % 2 == 0 else 0.3)
            if b >= 2 and lr.random() < 0.33:
                m = int(lr.choice(melody_scale))
                put(buf, osc("tri", midi(m), 0.8) * perc(0.8, 0.45), ts, 0.1)
    music = lowpass(buf, 7)
    crackle = (lr.random(len(buf)) < 0.00025) * lr.standard_normal(len(buf)) * 0.25
    music += lowpass(crackle, 3) * 0.6
    return finish(music, total)

def rainy_window():
    return lofi(75, [[48, 55, 59, 64], [45, 52, 55, 60], [50, 57, 60, 65], [55, 59, 62, 65]],
                [36, 33, 38, 31], 12, [72, 74, 76, 79, 81, 84], seed=11)

def coffee_break():
    return lofi(82, [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]],
                [41, 40, 38, 36], 14, [72, 76, 77, 79, 83, 84], seed=23)

def evening_prelude():
    beat = 60 / 88; bar = 4 * beat; bars = 16
    chords = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 52, 55, 60, 64], [43, 50, 55, 59, 62]]
    melody = {0: [(0, 76, 2), (2, 72, 2)], 1: [(0, 77, 2), (2, 72, 2)], 2: [(0, 79, 2), (2, 76, 2)], 3: [(0, 74, 2), (2, 71, 2)]}
    arp = [0, 2, 3, 4, 3, 2, 3, 2]
    total = bars * bar; buf = np.zeros(int((total + 5) * SR))
    for b in range(bars):
        ch = chords[b % 4]
        for s, idx in enumerate(arp):
            put(buf, piano(ch[idx], 2.2 if s == 0 else 1.4), b * bar + s * beat / 2, 0.18 if s % 4 == 0 else 0.15)
        if b >= 4:
            for bt, m, nb in melody[b % 4]:
                put(buf, piano(m, nb * beat + 0.8), b * bar + bt * beat, 0.3)
    return finish(echo(buf, 0.32, 0.35, 0.18), total)

def lighthouse_waltz():
    beat = 60 / 126; bar = 3 * beat
    prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]),
            (48, [60, 64, 67]), (43, [59, 62, 67]), (41, [57, 60, 65]), (48, [60, 64, 67])]
    melody = [[(0, 76, 1), (1, 79, 1), (2, 76, 1)], [(0, 74, 1), (1, 71, 1), (2, 74, 1)],
              [(0, 72, 1), (1, 76, 1), (2, 72, 1)], [(0, 69, 1), (1, 72, 1), (2, 77, 1)],
              [(0, 79, 1), (1, 76, 1), (2, 72, 1)], [(0, 71, 1), (1, 74, 1), (2, 79, 1)],
              [(0, 77, 1), (1, 76, 1), (2, 74, 1)], [(0, 72, 3)]]
    bars = 24; total = bars * bar; buf = np.zeros(int((total + 5) * SR))
    for b in range(bars):
        root, chord = prog[b % 8]
        put(buf, piano(root, 1.6), b * bar, 0.34)
        for k in (1, 2):
            for m in chord: put(buf, piano(m, 0.9), b * bar + k * beat, 0.13)
        if b >= 2:
            for bt, m, nb in melody[b % 8]: put(buf, piano(m, nb * beat + 0.5), b * bar + bt * beat, 0.28)
    return finish(echo(buf, 0.3, 0.35, 0.18), total)

def night_highway():
    beat = 60 / 108; bar = 4 * beat; bars = 16
    chords = [[57, 60, 64], [53, 57, 60], [60, 64, 67], [55, 59, 62]]; roots = [45, 41, 48, 43]
    total = bars * bar; n = int((total + 4) * SR)
    pad, bass, arp, drums = (np.zeros(n) for _ in range(4))
    for b in range(bars):
        ch, r, t0 = chords[b % 4], roots[b % 4], b * bar
        for m in ch:
            f = midi(m); d = bar + 0.3
            put(pad, lowpass((osc("saw", f * 0.995, d) + osc("saw", f * 1.005, d)) / 2, 24) * swell(d, 0.25, 0.4), t0, 0.12)
        for k in range(8):
            put(bass, lowpass(osc("saw", midi(r), 0.28), 14) * perc(0.28, 0.22), t0 + k * beat / 2, 0.5)
        if b >= 2:
            tones = [m + 12 for m in ch] + [ch[0] + 24]
            for s in range(16):
                put(arp, lowpass(osc("pulse", midi(tones[[0, 1, 2, 3, 2, 1, 2, 3][s % 8]]), 0.18), 3) * perc(0.18, 0.09), t0 + s * beat / 4, 0.11)
        for k in range(4):
            put(drums, kick(), t0 + k * beat, 0.9)
            put(drums, hat(0.08, 0.03), t0 + (k + 0.5) * beat, 0.5)
            if b >= 2 and k in (1, 3): put(drums, clap(), t0 + k * beat, 0.5)
    duck = ducking(n, beat)
    return finish((pad + bass) * duck + arp * (0.6 + 0.4 * duck) + drums, total)

def pulse_128():
    beat = 60 / 128; bar = 4 * beat; bars = 20
    chords = [[62, 65, 69], [58, 62, 65], [57, 60, 65], [60, 64, 67]]; roots = [50, 46, 53, 48]
    total = bars * bar; n = int((total + 4) * SR)
    pad, bass, stabs, drums = (np.zeros(n) for _ in range(4))
    for b in range(bars):
        ch, r, t0 = chords[b % 4], roots[b % 4], b * bar
        for k in range(4):
            put(drums, kick(), t0 + k * beat, 0.9)
            if b >= 2: put(drums, hat(0.12, 0.05), t0 + (k + 0.5) * beat, 0.5)
            if b >= 4 and k in (1, 3): put(drums, clap(), t0 + k * beat, 0.5)
            if b >= 4: put(bass, lowpass(osc("saw", midi(r), 0.2), 12) * perc(0.2, 0.18), t0 + (k + 0.5) * beat, 0.5)
        if b >= 8:
            for s in (2, 5, 10, 13):
                for m in ch:
                    put(stabs, lowpass(osc("saw", midi(m), 0.3), 10) * perc(0.3, 0.13), t0 + s * beat / 4, 0.1)
        if b >= 12:
            for m in ch:
                d = bar + 0.3
                put(pad, lowpass(osc("saw", midi(m), d), 24) * swell(d, 0.3, 0.4), t0, 0.06)
    duck = ducking(n, beat)
    return finish((bass + pad) * duck + stabs * (0.5 + 0.5 * duck) + drums, total)

def level_one():
    beat = 60 / 140; bar = 4 * beat; bars = 24
    chords = [[72, 76, 79, 84], [69, 72, 76, 81], [65, 69, 72, 77], [67, 71, 74, 79]]; roots = [48, 45, 41, 43]
    total = bars * bar; buf = np.zeros(int((total + 3) * SR))
    for b in range(bars):
        ch, r, t0 = chords[b % 4], roots[b % 4], b * bar
        for s in range(8):
            ts = t0 + s * beat / 2
            put(buf, osc("pulse", midi(ch[[0, 1, 2, 3, 2, 1, 2, 1][s]]), 0.2) * perc(0.2, 0.12), ts, 0.16)
            put(buf, osc("tri", midi(r + (12 if s % 2 else 0)), 0.22) * perc(0.22, 0.2), ts, 0.3)
            put(buf, hat(0.05, 0.015), ts, 0.4)
        for k in range(4):
            if k in (0, 2): put(buf, kick(0.18), t0 + k * beat, 0.7)
            else: put(buf, snare(0.15), t0 + k * beat, 0.6)
            if b >= 8: put(buf, osc("square", midi(ch[2] - 12), 0.25) * perc(0.25, 0.15), t0 + k * beat, 0.07)
    return finish(buf, total)


# ---------- каталог и экспорт ----------
CATALOG = [
    ("slow_tide", slow_tide, "Slow Tide", "Lumen Fields", "Still Water", "ambient", "ambient, спокойное, медитация"),
    ("glass_hours", glass_hours, "Glass Hours", "Lumen Fields", "Still Water", "ambient", "ambient, ночь, спокойное"),
    ("rainy_window", rainy_window, "Rainy Window", "Pixel Rain", "Study Tapes", "lo-fi", "lo-fi, хип-хоп, для учёбы"),
    ("coffee_break", coffee_break, "Coffee Break", "Pixel Rain", "Study Tapes", "lo-fi", "lo-fi, для учёбы, спокойное"),
    ("evening_prelude", evening_prelude, "Evening Prelude", "Quiet Harbor", "Harbor Lights", "classical", "классика, фортепиано, спокойное"),
    ("lighthouse_waltz", lighthouse_waltz, "Lighthouse Waltz", "Quiet Harbor", "Harbor Lights", "classical", "классика, фортепиано, вальс"),
    ("night_highway", night_highway, "Night Highway", "Neon Drift", "After Dark", "electronic", "электроника, synthwave, для дороги"),
    ("pulse_128", pulse_128, "Pulse 128", "Neon Drift", "After Dark", "electronic", "электроника, танцевальная, для спорта"),
    ("level_one", level_one, "Level One", "Bit Garden", "8-Bit Meadow", "chiptune", "chiptune, игры, бодрое"),
]

def save(slug, x, title, artist, album, genre):
    wav_path, mp3_path = OUT_DIR / f"{slug}.wav", OUT_DIR / f"{slug}.mp3"
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", "128k",
           "-metadata", f"title={title}", "-metadata", f"artist={artist}", "-metadata", f"album={album}",
           "-metadata", f"genre={genre}", "-metadata", "comment=CC0 - public domain, generated for Music Hub",
           str(mp3_path)]
    try:
        ok = subprocess.run(cmd).returncode == 0
    except FileNotFoundError:
        ok = False
    if ok:
        wav_path.unlink(); return mp3_path.name
    print(f"  ffmpeg недоступен — оставлен {wav_path.name}")
    return wav_path.name

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = []
    for slug, builder, title, artist, album, genre, tags in CATALOG:
        print(f"Генерирую {artist} — {title}")
        fname = save(slug, builder(), title, artist, album, genre)
        catalog.append({"file": fname, "title": title, "artist": artist, "album": album, "tags": tags})
    (OUT_DIR / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "LICENSE.txt").write_text(
        "Все файлы в этой папке созданы скриптом tools/generate_demo_music.py и переданы в общественное достояние (CC0 1.0).\n"
        "Их можно свободно использовать, изменять и распространять без указания авторства.\n", encoding="utf-8")
    print("Готово:", OUT_DIR)

if __name__ == "__main__":
    main()
