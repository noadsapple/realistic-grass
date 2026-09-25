"""Voice-over + original music for the Realistic Grass social videos.

For each language this script:
  1. synthesizes the 4 voice-over lines with Kokoro-82M (Apache-2.0) through sherpa-onnx,
  2. derives the scene timing of the video from the length of each line (timing-<lang>.json,
     read by render-reel.mjs so the animation follows the voice),
  3. composes an original backing track in code (drums, bass, chords, pluck melody) —
     no samples, no third-party music, so it is free of any copyright,
  4. mixes them (music ducked under the voice) into audio-<lang>.wav.

Requirements:  pip install sherpa-onnx numpy
Model:  kokoro-int8-multi-lang-v1_0 from
  https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-int8-multi-lang-v1_0.tar.bz2
  (set KOKORO_DIR to the extracted folder).
Usage:  KOKORO_DIR=/path/to/kokoro-int8-multi-lang-v1_0 python3 social/make-audio.py en|es
"""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100

# ---------------------------------------------------------------- voice-over script
# One line per scene: hook / van laying turf / benefits / call to action.
SCRIPT = {
    "en": {
        "voice": 3,  # af_heart
        "speed": 1.05,
        "lines": [
            "Tired of mowing, watering, and mud?",
            "Get real-looking artificial grass, installed in Miami at wholesale prices.",
            "Premium quality, no maintenance. Free estimate, and a five-year limited warranty.",
            "Call Realistic Grass now! Seven eight six, three two nine, nine one one seven.",
        ],
    },
    "es": {
        "voice": 28,  # ef_dora
        "speed": 1.08,
        "lines": [
            "¿Cansado de cortar el césped, regar y el lodo?",
            "Grama artificial que parece real, instalada en Miami a precios al por mayor.",
            "Calidad premium, sin mantenimiento. Estimado gratis y garantía limitada de cinco años.",
            "¡Llame ya a Realistic Grass! Siete, ocho, seis. Tres, dos, nueve. Nueve, uno, uno, siete.",
        ],
    },
}


def synthesize(lang):
    import sherpa_onnx

    d = os.environ.get("KOKORO_DIR", "/tmp/tts/kokoro-int8-multi-lang-v1_0").rstrip("/") + "/"
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=d + "model.int8.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt",
                data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
                lexicon=d + "lexicon-us-en.txt" if lang == "en" else "", lang=lang),
            num_threads=4))
    tts = sherpa_onnx.OfflineTts(cfg)
    s = SCRIPT[lang]
    clips = []
    for line in s["lines"]:
        a = tts.generate(line, sid=s["voice"], speed=s["speed"])
        x = np.asarray(a.samples, dtype=np.float32)
        x = resample(x, a.sample_rate, SR)
        clips.append(trim(x))
    return clips


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    n = int(round(len(x) * sr_out / sr_in))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - 800): idx[-1] + 2000] if len(idx) else x


# ---------------------------------------------------------------- scene timing
def timing(clips):
    """Scene boundaries (seconds) so each line plays over its scene."""
    d = [len(c) / SR for c in clips]
    t = {}
    t["v1"] = 0.35                                          # hook line starts
    t["hookEnd"] = max(2.6, t["v1"] + d[0] + 0.25)
    t["vanStart"] = t["hookEnd"] + 0.05
    t["v2"] = t["vanStart"] + 0.25
    t["vanEnd"] = max(t["vanStart"] + 4.4, t["v2"] + d[1] + 0.35)
    t["listStart"] = t["vanEnd"] + 0.2
    t["v3"] = t["listStart"] + 0.15
    t["ctaStart"] = max(t["listStart"] + 3.2, t["v3"] + d[2] + 0.3)
    t["v4"] = t["ctaStart"] + 0.35
    t["duration"] = round(t["v4"] + d[3] + 1.6, 2)          # hold the end card
    return {k: round(v, 3) for k, v in t.items()}


# ---------------------------------------------------------------- music (original, generated)
BPM = 112
BEAT = 60 / BPM
rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env(n, a=0.005, d=0.2, s=0.0, r=0.05):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, np.exp(-(t - a) / max(d, 1e-4)) * (1 - s) + s)
    rel = int(r * SR)
    if rel and n > rel:
        e[-rel:] *= np.linspace(1, 0, rel)
    return e


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):          # one-pole filter (fine for a few seconds of audio)
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def saw(f, n, detune=0.0):
    t = np.arange(n) / SR
    out = 0
    for dt in (-detune, 0, detune):
        ph = (t * f * (1 + dt)) % 1.0
        out = out + (2 * ph - 1)
    return out / 3


def kick(n):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def clap(n):
    t = np.arange(n) / SR
    noise = rng.uniform(-1, 1, n)
    burst = sum(np.exp(-np.clip(t - k * 0.011, 0, None) * 60) * (t >= k * 0.011) for k in range(3))
    return lowpass(noise, 3000) * burst * 1.4


def hat(n, open_=False):
    noise = rng.uniform(-1, 1, n)
    hp = noise - lowpass(noise, 7000)
    return hp * env(n, 0.001, 0.12 if open_ else 0.03)


def music(duration):
    n = int((duration + 0.5) * SR)
    L = np.zeros(n)
    R = np.zeros(n)

    def put(buf, x, t, gain=1.0):
        i = int(t * SR)
        if i >= len(buf):
            return
        x = x[: len(buf) - i]
        buf[i: i + len(x)] += x * gain

    def both(x, t, g=1.0, pan=0.0):
        put(L, x, t, g * (1 - max(0, pan)))
        put(R, x, t, g * (1 + min(0, pan)))

    # C – G – Am – F, one bar (4 beats) each
    prog = [(60, [60, 64, 67]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]
    melody = [72, 76, 79, 76, 74, 71, 74, 79, 72, 76, 81, 79, 77, 76, 74, 72]   # pluck arpeggio, 8ths
    bars = int(duration / (4 * BEAT)) + 2
    k_s, c_s, h_s = kick(int(0.4 * SR)), clap(int(0.3 * SR)), hat(int(0.08 * SR))
    ho = hat(int(0.25 * SR), True)
    for b in range(bars):
        root, chord = prog[b % 4]
        t0 = b * 4 * BEAT
        intro = b == 0                                        # first bar: pads + pluck only
        # pad chord (soft detuned saws, low-passed)
        pn = int(4 * BEAT * SR)
        pad = sum(saw(midi(nn), pn, 0.004) for nn in chord)
        pad = lowpass(pad * env(pn, 0.15, 3.0, 0.6, 0.3), 1400)
        both(pad, t0, 0.10, -0.2)
        both(pad, t0 + 0.012, 0.10, 0.2)
        for beat in range(4):
            tb = t0 + beat * BEAT
            if not intro:
                both(k_s, tb, 0.9)
                if beat in (1, 3):
                    both(c_s, tb, 0.35)
                both(h_s, tb + BEAT / 2, 0.16, 0.3)
                if beat == 3:
                    both(ho, tb + BEAT * 0.75, 0.08, -0.3)
                # bass: root on the off-beat (house-style pump)
                bn = int(BEAT * 0.45 * SR)
                bass = lowpass(saw(midi(root - 24), bn) * env(bn, 0.005, 0.18, 0.3, 0.03), 500)
                bass += 0.6 * np.sin(2 * np.pi * midi(root - 24) * np.arange(bn) / SR) * env(bn, 0.005, 0.2, 0.3, 0.03)
                both(bass, tb + BEAT / 2, 0.42)
            for half in range(2):
                note = melody[(b % 2) * 8 + beat * 2 + half] + (chord[0] - 60 if b % 4 in (1, 3) else 0)
                pn2 = int(0.22 * SR)
                t_ = np.arange(pn2) / SR
                pl = (np.sin(2 * np.pi * midi(note) * t_) + 0.3 * np.sin(4 * np.pi * midi(note) * t_)) * env(pn2, 0.003, 0.12)
                both(pl, tb + half * BEAT / 2, 0.11, 0.35 if half else -0.35)
    st = np.stack([L, R], axis=1)[: int(duration * SR)]
    fade = int(1.2 * SR)
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    st[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    return st / (np.max(np.abs(st)) + 1e-9) * 0.8


# ---------------------------------------------------------------- mix
def mix(lang):
    clips = synthesize(lang)
    tm = timing(clips)
    dur = tm["duration"]
    mus = music(dur)
    n = len(mus)
    vo = np.zeros(n)
    for c, key in zip(clips, ("v1", "v2", "v3", "v4")):
        i = int(tm[key] * SR)
        seg = c[: max(0, n - i)]
        vo[i: i + len(seg)] += seg
    vo = vo / (np.max(np.abs(vo)) + 1e-9) * 0.9
    # duck the music under the voice (smoothed envelope)
    active = np.convolve((np.abs(vo) > 0.02).astype(float), np.ones(int(0.25 * SR)) / (0.25 * SR), mode="same")
    duck = 1 - 0.7 * np.clip(active * 3, 0, 1)
    out = mus * duck[:, None] * 0.55 + vo[:, None]
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.95
    path = os.path.join(HERE, f"audio-{lang}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    json.dump(tm, open(os.path.join(HERE, f"timing-{lang}.json"), "w"), indent=2)
    print(lang, "timing", tm)
    return path


if __name__ == "__main__":
    for lang in sys.argv[1:] or ["en", "es"]:
        mix(lang)
