"""Synthesizes the soundtrack (ambient pad + sparse piano + rain) for the video.
Usage: python3 music.py <timeline.json> <out.wav>"""
import json, sys, wave
import numpy as np

tl = json.load(open(sys.argv[1]))
T = tl["total"]; SR = 44100
N = int(T * SR); t = np.arange(N) / SR
start = {s["id"]: s["start"] for s in tl["timeline"]}
rs = np.random.RandomState(7)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def ramp(a, b):  # 0 before a, 1 after b
    return np.clip((t - a) / max(b - a, 1e-6), 0, 1)

# Am - F - C - G (i - VI - III - VII), 8 seconds per chord
CH = [[45, 52, 57, 60, 64], [41, 48, 57, 60, 65], [48, 55, 60, 64, 67], [43, 50, 59, 62, 67]]
BAR = 8.0
pad = np.zeros(N); piano = np.zeros(N); hi = np.zeros(N)
nb = int(np.ceil(T / BAR))
for b in range(nb):
    ch = CH[b % 4]; t0 = b * BAR
    env = np.clip((t - (t0 - 1.5)) / 3.0, 0, 1) * np.clip(((t0 + BAR + 1.5) - t) / 3.0, 0, 1)
    for i, m in enumerate(ch):
        for det in (-0.07, 0.06):
            f = hz(m + det)
            pad += env * (np.sin(2 * np.pi * f * t + rs.rand() * 6) + 0.3 * np.sin(4 * np.pi * f * t)) * (0.5 if i else 0.9)
    for m in ch[2:]:
        hi += env * np.sin(2 * np.pi * hz(m + 12.04) * t + rs.rand() * 6) * (1 + 0.3 * np.sin(2 * np.pi * 0.2 * t))
    # sparse piano: slow arpeggio
    pat = [(0.0, ch[2]), (2.0, ch[4]), (4.0, ch[3] + 12), (6.0, ch[4])]
    if b % 2: pat = [(0.0, ch[3]), (2.0, ch[4] + 12), (3.0, ch[3] + 12), (5.0, ch[2] + 12)]
    for off, m in pat:
        s0 = int((t0 + off) * SR)
        if s0 >= N: continue
        L = min(int(5 * SR), N - s0); tt = np.arange(L) / SR; f = hz(m)
        note = sum(np.sin(2 * np.pi * f * k * tt) * np.exp(-tt * (1.1 + 0.7 * k)) / k ** 1.6 for k in range(1, 6))
        note *= np.clip(tt / 0.008, 0, 1)
        piano[s0:s0 + L] += note * (0.8 + 0.2 * rs.rand())

def reverb(x, secs=3.2, mix=0.5):
    L = int(secs * SR); ir = rs.randn(L) * np.exp(-np.arange(L) / (secs * SR / 5.5))
    n = 1 << int(np.ceil(np.log2(len(x) + L)))
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
    return x * (1 - mix) + wet / np.sqrt((ir ** 2).sum()) * mix * 1.6

def lowpass(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** 4), len(x))

pad = lowpass(pad / np.abs(pad).max(), 1400)
piano = reverb(piano / np.abs(piano).max(), 3.5, 0.45)
hi = reverb(lowpass(hi / np.abs(hi).max(), 3000), 4, 0.6)

# arrangement: quiet start, builds, drops out at "nasanay na tayo", returns fuller at the flag
bus, roof, work, flag, crowd, end = (start[k] for k in ("bus", "rooftop", "workers", "flag", "crowd", "end"))
drop = 1 - ramp(bus + 3.0, bus + 4.2) + ramp(roof - 0.2, roof + 3)
pad_g = (0.25 + 0.3 * ramp(start["queue"], start["flood"])) * drop + 0.3 * ramp(flag - 1, flag + 4)
piano_g = (0.35 * ramp(2, 6) + 0.15 * ramp(start["flood"], start["mansion"])) * (1 - ramp(bus + 3.0, bus + 3.6) + ramp(roof + 0.5, work)) \
          + 0.25 * ramp(flag - 0.5, flag + 2)
hi_g = 0.12 * ramp(start["road"], start["mansion"]) * drop + 0.4 * ramp(flag - 1, crowd)
music = pad * pad_g + piano * piano_g + hi * hi_g
# low drone + slow heartbeat while the music is gone
hb = np.zeros(N)
for k in np.arange(bus + 3.6, roof + 0.5, 1.25):
    for o in (0, 0.28):
        s0 = int((k + o) * SR); L = min(int(0.5 * SR), N - s0); tt = np.arange(L) / SR
        hb[s0:s0 + L] += np.sin(2 * np.pi * 52 * tt * (1 - 0.3 * tt)) * np.exp(-tt * 13) * (1 if o == 0 else 0.6)
music += hb * 0.55 + np.sin(2 * np.pi * 55 * t) * 0.07 * (ramp(bus + 3, bus + 4.5) - ramp(roof, roof + 2))

# rain
noise = rs.randn(N)
X = np.fft.rfft(noise); f = np.fft.rfftfreq(N, 1 / SR)
rain = np.fft.irfft(X * (f / 900) / (1 + (f / 900) ** 2) / (1 + (f / 7000) ** 2), N); rain /= np.abs(rain).max()
def win(a, b, e=0.8): return ramp(a - e, a + e) * (1 - ramp(b - e, b + e))
q, fl, rd = start["queue"], start["flood"], start["road"]
rain_g = 0.10 * win(q, start["payslip"]) + 0.34 * win(fl, rd, 0.4) + 0.08 * win(bus, roof) + 0.12 * win(roof, work)
mix = music + rain * rain_g
mix *= ramp(0, 2.5) * (1 - ramp(T - 3.5, T - 0.2))
mix = np.tanh(mix * 1.5 / np.abs(mix).max() * 1.2) * 0.84
# gentle stereo widening
d = int(0.012 * SR); L = mix; R = np.concatenate([np.zeros(d), mix[:-d]]) * 0.5 + mix * 0.5
st = (np.stack([L, R], 1) * 32767).astype(np.int16)
w = wave.open(sys.argv[2], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes()); w.close()
print("wrote", sys.argv[2], f"{T:.1f}s")
