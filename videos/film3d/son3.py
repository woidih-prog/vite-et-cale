#!/usr/bin/env python3
"""Bande-son du spot (26,5 s), composée ici de zéro et calée sur les instants de spot.html.
Pad, basse, pulsation à 120 bpm, tics des compteurs, souffles des transitions, cloche du résultat."""
import wave, numpy as np
SR = 44100; T = 30.0; N = int(SR * T)
mix = np.zeros((N, 2))
rng = np.random.default_rng(7)

def at(s): return int(s * SR)
def pose(son, t, g=1.0, pan=0.0):
    i = at(t); son = son[:max(0, N - i)]
    mix[i:i+len(son), 0] += son * g * (1 - max(0, pan)); mix[i:i+len(son), 1] += son * g * (1 + min(0, pan))
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def bande(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def env(n, a=0.01, r=0.3):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)

def kick(g=1.0):
    n = at(0.45); t = np.arange(n) / SR; f = 45 + 95 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * g
def hat():
    n = at(0.08); return bande(rng.standard_normal(n), 7000, 16000) * env(n, 0.001, 0.02) * 0.5
def tic(f=2400):
    n = at(0.03); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t * 180)
def souffle(d=0.6, montee=True):
    n = at(d); x = bande(rng.standard_normal(n), 300, 6000); t = np.arange(n) / n
    e = np.sin(np.pi * t) ** 2 if not montee else t ** 2.5
    return x * e * 0.35
def cloche(m, d=2.5):
    n = at(d); t = np.arange(n) / SR; f = hz(m)
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.5 + k)) for k, a in [(1, 1), (2.76, .4), (5.4, .2), (8.9, .08)])
    return s * np.minimum(1, t / 0.003)
def nappe(notes, d, g=0.12):
    n = at(d); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for det in (-0.06, 0.06):
            s += np.sin(2 * np.pi * hz(m + det) * t + np.sin(2 * np.pi * 0.3 * t))
    e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.5)
    return bande(s * e, 60, 2400) * g / len(notes)
def basse(m, d):
    n = at(d); t = np.arange(n) / SR; s = np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m) * 2 * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t / 0.9) * 0.35
def piano(m, d=1.6):
    n = at(d); t = np.arange(n) / SR; f = hz(m)
    s = np.sin(2 * np.pi * f * t + 0.8 * np.exp(-6 * t) * np.sin(2 * np.pi * 2 * f * t))
    return s * np.minimum(1, t / 0.008) * np.exp(-t / 0.8) * 0.2

D_ = [50, 54, 57, 62, 66]; Bm = [47, 50, 54, 59, 62]; G_ = [43, 50, 55, 59, 62]; A_ = [45, 52, 57, 61, 64]
# 0-5 s : le caddie, les prix qui montent (ton mineur, tics), le porte-monnaie
pose(nappe([38, 45, 50, 53], 5.2, 0.11), 0.0)
for i in range(6): pose(tic(2200 + i * 120), 0.5 + i * 0.42, 0.35); pose(cloche(72 + i, 0.4), 0.5 + i * 0.42, 0.06)
v_prec = -1
for k in range(560):
    tt = 0.6 + k * 0.005; p = min(1, (tt - 0.6) / 2.8); p = 4*p**3 if p < .5 else 1 - (-2*p + 2)**3 / 2; v = int(61.4 * p)
    if v != v_prec and tt < 3.4: pose(tic(3000), tt, 0.16); v_prec = v
pose(kick(0.8), 3.4); n = at(0.5); pose(bande(rng.standard_normal(n), 300, 2500) * env(n, 0.005, 0.15) * 0.4, 3.3)
for k in range(3): pose(cloche(88 - k * 3, 0.6), 3.9 + k * 0.12, 0.08)
pose(souffle(1.0), 4.0, 0.8)
# 5-16 s : l'appli arrive, la pulsation majeure
pose(kick(1.1), 5.0); pose(cloche(81, 1.5), 5.0, 0.2)
for b in range(6):
    t0 = 5.0 + b * 2; notes = [D_, Bm, G_, A_][b % 4]
    pose(nappe(notes, 2.2, 0.10), t0); pose(basse(notes[0] - 12, 1.0), t0); pose(basse(notes[0] - 12, 0.6), t0 + 1.0)
    for k, m in enumerate([notes[-1] + 12, notes[-2] + 12, notes[-3] + 12]): pose(piano(m), t0 + 0.5 + k * 0.5, 0.8, pan=(-0.3 if k % 2 else 0.3))
for k in range(22):
    tt = 5.0 + k * 0.5; pose(kick(0.5), tt)
    if tt >= 9.0: pose(hat(), tt + 0.25, 0.8, pan=0.2)
pose(souffle(0.6, False), 9.0, 0.7)
for i in range(8): pose(cloche(79 + (i % 4) * 2, 0.5), 9.4 + i * 0.12 + 0.5, 0.07, pan=(-0.5 + i * 0.14))
pose(souffle(0.7), 15.3, 0.8)
# 16-23 s : les assiettes, une note claire par assiette
pose(kick(1.0), 16.0); pose(nappe(D_ + [69], 7.0, 0.11), 16.0)
for i, m in enumerate([74, 76, 78, 79, 81, 83, 86]): pose(piano(m, 1.6), 16.9 + i * 0.33 + 0.15, 1.0, pan=-0.45 + i * 0.15)
for k in range(12): pose(kick(0.4), 17.0 + k * 0.5); pose(hat(), 17.25 + k * 0.5, 0.6)
pose(cloche(86, 2.0), 19.2, 0.22)
# 23-30 s : convergence et signature
pose(souffle(1.6), 22.4, 0.9); pose(kick(1.2), 24.0)
pose(nappe([50, 57, 62, 66, 69, 74, 78], 6.0, 0.15), 24.0); pose(basse(38, 3.0), 24.0)
for k2, m in enumerate([74, 78, 81, 86]): pose(piano(m, 2.0), 25.3 + k2 * 0.12, 1.2)
pose(kick(0.9), 26.4); pose(cloche(86, 2.0), 26.4, 0.2)
for k2, m in enumerate([86, 90, 93, 98]): pose(cloche(m, 1.5), 27.4 + k2 * 0.09, 0.08, pan=(-0.3 + k2 * 0.2))

# fondu final, normalisation
f = np.ones(N); f[at(29.0):] = np.linspace(1, 0, N - at(29.0)); mix *= f[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open("son3.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
print("ok", round(T, 1))
