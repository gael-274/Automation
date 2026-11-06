#!/usr/bin/env python3
"""
NeuroWave - Step 1
A synthetic "brain" that streams EEG-like signals, plus a live terminal
visualiser that draws the waves with keyboard characters.

Run:   python neurowave.py
Stop:  Ctrl+C
Needs: pip install numpy
"""
import argparse
import math
import os
import shutil
import sys
import time

import numpy as np

FS = 256  # samples per second (typical for consumer EEG headsets)
WINDOW_SEC = 2

BANDS = {
    "delta": (1, 4),    # deep sleep
    "theta": (4, 8),    # drowsy, daydreaming
    "alpha": (8, 13),   # relaxed, eyes closed
    "beta":  (13, 30),  # focused, thinking
    "gamma": (30, 45),  # high-level processing
}
BAND_FREQ = {"delta": 2.0, "theta": 6.0, "alpha": 10.0, "beta": 20.0, "gamma": 38.0}

WAVE_CHARS = "_.-~^"  # keyboard "wave signs", low -> high
COLORS = {"delta": "\x1b[35m", "theta": "\x1b[34m", "alpha": "\x1b[32m",
          "beta": "\x1b[33m", "gamma": "\x1b[31m"}
RESET = "\x1b[0m"


class SyntheticBrain:
    """Fake EEG source. Drifts between relaxed and focused every ~30 seconds."""

    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.t = 0
        self.phase = {b: self.rng.uniform(0, 2 * np.pi) for b in BAND_FREQ}

    def read(self, n):
        ts = np.arange(self.t, self.t + n) / FS
        focus = 0.5 + 0.5 * np.sin(2 * np.pi * ts / 30.0)  # 0 relaxed, 1 focused
        amps = {
            "delta": 8.0,
            "theta": 6.0,
            "alpha": 3.0 + 20.0 * (1 - focus),
            "beta": 4.0 + 14.0 * focus,
            "gamma": 2.0 + 3.0 * focus,
        }
        sig = sum(amps[b] * np.sin(2 * np.pi * BAND_FREQ[b] * ts + self.phase[b])
                  for b in BAND_FREQ)
        sig = sig + self.rng.normal(0, 3, n)
        self.t += n
        return sig


# ---------- signal processing ----------

def band_powers(window):
    w = (window - window.mean()) * np.hanning(len(window))
    spec = np.abs(np.fft.rfft(w)) ** 2
    freqs = np.fft.rfftfreq(len(w), 1 / FS)
    raw = {b: spec[(freqs >= lo) & (freqs < hi)].sum() for b, (lo, hi) in BANDS.items()}
    total = sum(raw.values()) or 1.0
    return {b: v / total for b, v in raw.items()}


def band_filter(x, lo, hi):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / FS)
    spec[(freqs < lo) | (freqs >= hi)] = 0
    return np.fft.irfft(spec, len(x))


def mental_state(rel):
    # Simple rule for now. A later step replaces this with a trained model.
    a, b = rel["alpha"], rel["beta"]
    if a > b * 1.2:
        return "RELAXED"
    if b > a * 1.2:
        return "FOCUSED"
    return "NEUTRAL"


# ---------- keyboard-character drawing ----------

def resample(x, n):
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)


def wave_grid(x, width, height):
    """Draw a waveform using / \\ - | characters."""
    y = resample(x, width)
    lim = max(np.abs(y).max(), 1e-9)
    rows = np.clip(((1 - (y / lim + 1) / 2) * (height - 1)).round().astype(int),
                   0, height - 1)
    grid = [[" "] * width for _ in range(height)]
    for i in range(width):
        r = rows[i]
        nxt = rows[i + 1] if i + 1 < width else r
        if abs(nxt - r) > 1:
            for rr in range(min(r, nxt) + 1, max(r, nxt)):
                grid[rr][i] = "|"
        grid[r][i] = "/" if nxt < r else "\\" if nxt > r else "-"
    return ["".join(row) for row in grid]


def band_strip(x, lo, hi, width, scale):
    """One line per band using _ . - ~ ^ as the wave."""
    y = resample(band_filter(x, lo, hi), width)
    idx = ((np.clip(y / scale, -1, 1) + 1) / 2 * (len(WAVE_CHARS) - 1)).round().astype(int)
    return "".join(WAVE_CHARS[i] for i in idx)


def render(buf, t_sec, source_name, color):
    cols, _ = shutil.get_terminal_size((100, 30))
    cols = max(cols, 70)
    c = (lambda b: COLORS[b]) if color else (lambda b: "")
    r = RESET if color else ""

    rel = band_powers(buf)
    state = mental_state(rel)
    lines = [
        f"NEUROWAVE   source: {source_name}   t={t_sec:6.1f}s   state: {state}",
        "=" * (cols - 1),
        f"RAW EEG ({WINDOW_SEC}s window)",
    ]
    lines += wave_grid(buf, cols - 1, 9)
    lines.append("-" * (cols - 1))

    strip_w = cols - 40
    scale = max(np.abs(buf).max() * 0.6, 1e-9)
    for b, (lo, hi) in BANDS.items():
        strip = band_strip(buf, lo, hi, strip_w, scale)
        bar = "#" * int(rel[b] * 20)
        lines.append(f"{c(b)}{b:<6}{lo:>2}-{hi:<2}Hz {strip} {bar:<20}{rel[b]*100:4.0f}%{r}")
    lines.append("")
    lines.append("Ctrl+C to quit")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="NeuroWave brain wave visualiser")
    ap.add_argument("--fps", type=int, default=20)
    ap.add_argument("--frames", type=int, default=0, help="stop after N frames (0 = run forever)")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()

    if os.name == "nt":
        os.system("")  # enables ANSI escape codes in Windows terminals

    brain = SyntheticBrain()
    buf = np.zeros(FS * WINDOW_SEC)
    chunk = max(FS // args.fps, 1)
    sys.stdout.write("\x1b[2J")
    frame = 0
    try:
        while args.frames == 0 or frame < args.frames:
            new = brain.read(chunk)
            buf = np.roll(buf, -chunk)
            buf[-chunk:] = new
            out = render(buf, brain.t / FS, "synthetic", not args.no_color)
            sys.stdout.write("\x1b[H" + out + "\x1b[J")
            sys.stdout.flush()
            frame += 1
            time.sleep(1 / args.fps)
    except KeyboardInterrupt:
        pass
    print("\nBye.")


if __name__ == "__main__":
    main()
