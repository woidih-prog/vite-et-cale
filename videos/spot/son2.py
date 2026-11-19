#!/usr/bin/env python3
"""Bande-son du spot vacances (29,5 s), composée ici de zéro et calée sur les instants de spot2.html.
Pad, basse, pulsation à 120 bpm, tics des compteurs, souffles des transitions, cloche du résultat."""
import wave, numpy as np
SR = 44100; T = 29.5; N = int(SR * T)
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

def ioc(p): return 4*p**3 if p < .5 else 1 - (-2*p + 2)**3 / 2
def quand(m):                     # instant où la ligne de l'année atteint le mois m (même courbe que l'image)
    for k in range(2000):
        p = k / 1999
        if ioc(p) * 12 >= m: return 16.6 + p * 3.6
    return 20.2
D = [50, 54, 57, 62, 66]; Bm = [47, 50, 54, 59, 62]; G = [43, 50, 55, 59, 62]; A = [45, 52, 57, 61, 64]
# 0-3,4 s : le soleil se lève, nappe majeure et trois notes pour les trois lignes
pose(nappe([38, 45, 50, 54, 57], 3.6, 0.12), 0.0); pose(souffle(2.2), 0.5, 0.5)
for k, m in enumerate([74, 78, 81]): pose(piano(m, 2.0), 0.25 + k * 0.14, 1.3)
# 3,4-15,5 s : la pulsation, chaleureuse
pose(souffle(0.6, False), 3.0, 0.8)
for b in range(6):
    t0 = 3.5 + b * 2; notes = [D, Bm, G, A][b % 4]
    pose(nappe(notes, 2.2, 0.10), t0); pose(basse(notes[0] - 12, 1.0), t0); pose(basse(notes[0] - 12, 0.6), t0 + 1.0)
    for k, m in enumerate([notes[-1] + 12, notes[-2] + 12, notes[-3] + 12]): pose(piano(m), t0 + 0.5 + k * 0.5, 0.8, pan=(-0.3 if k % 2 else 0.3))
for k in range(24):
    tt = 3.5 + k * 0.5; pose(kick(0.5), tt)
    if tt >= 7.5: pose(hat(), tt + 0.25, 0.8, pan=0.2)
for k in range(30): pose(tic(2600), 3.5 + 0.8 * (1 - (1 - k / 30) ** 2), 0.18)
pose(bande(rng.standard_normal(at(0.22)), 2000, 9000) * env(at(0.22), 0.002, 0.05) * 0.5, 4.6, pan=-0.3)
for k in range(15): pose(tic(3000), 4.8 + 0.7 * (1 - (1 - k / 15) ** 2), 0.18)
pose(kick(1.0), 5.7); pose(cloche(83, 1.8), 5.7, 0.3); pose(cloche(90, 1.5), 5.85, 0.15)
pose(souffle(0.7, False), 7.1, 0.8); pose(cloche(86, 1.0), 8.9, 0.15)
pose(souffle(0.6, False), 11.2, 0.8); pose(kick(0.9), 11.5)
for tt in (13.27, 14.42): pose(souffle(0.45, False), tt - 0.3, 0.5); pose(cloche(81, 0.8), tt, 0.1)
# 15,8-21,3 s : l'année défile, une note par mois qui monte
pose(souffle(0.6), 15.3, 0.8); pose(nappe(D + [69], 5.4, 0.10), 15.9)
gamme = [62, 64, 66, 67, 69, 71, 73, 74, 76, 78, 79, 81]
for m in range(12): pose(piano(gamme[m] + 12, 1.2), quand(m + 0.5), 0.9, pan=-0.4 + m * 0.07)
for m in (2, 6, 11.3): pose(cloche(86, 1.6), quand(m), 0.2)
pose(kick(0.9), 20.2); pose(cloche(90, 2.4), 20.2, 0.25)
# 21,3-25,5 s : coucher de soleil, la mer, l'avion
pose(nappe([38, 50, 57, 62, 66, 69, 74], 4.6, 0.16), 21.3); pose(basse(38, 3.0), 21.3)
n = at(4.2); mer = bande(rng.standard_normal(n), 200, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / SR / 2.1)) * 0.05; pose(mer, 21.3)
n = at(3.4); x = bande(rng.standard_normal(n), 500, 3500) * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.12
i0 = at(22.0); k = np.linspace(-0.8, 0.8, n); mix[i0:i0+n, 0] += x * (1 - np.maximum(0, k)); mix[i0:i0+n, 1] += x * (1 + np.minimum(0, k))
for k2, m in enumerate([74, 78, 83]): pose(piano(m, 2.2), 22.2 + k2 * 0.42, 1.2)
# 25,3-29,5 s : signature
pose(kick(1.1), 25.3); pose(nappe([50, 57, 62, 66, 69, 74, 78], 4.2, 0.15), 25.3); pose(basse(38, 3.0), 25.3)
for k2, m in enumerate([74, 78, 81, 86]): pose(piano(m, 2.0), 25.9 + k2 * 0.12, 1.2)
for k2, m in enumerate([86, 90, 93, 98]): pose(cloche(m, 1.5), 28.2 + k2 * 0.09, 0.08, pan=(-0.3 + k2 * 0.2))

# fondu final, normalisation
f = np.ones(N); f[at(28.6):] = np.linspace(1, 0, N - at(28.6)); mix *= f[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open("son2.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
print("ok", round(T, 1))
