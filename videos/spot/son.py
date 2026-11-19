#!/usr/bin/env python3
"""Bande-son du spot (26,5 s), composée ici de zéro et calée sur les instants de spot.html.
Pad, basse, pulsation à 120 bpm, tics des compteurs, souffles des transitions, cloche du résultat."""
import wave, numpy as np
SR = 44100; T = 26.5; N = int(SR * T)
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

# 0-3 s : tension. Nappe grave, compteur qui tique en ralentissant, coupure rouge.
pose(nappe([38, 45, 50], 3.2, 0.10), 0.0)
v_prec = -1
for k in range(0, 300):
    tt = 0.3 + k * 0.005; p = min(1, (tt - 0.3) / 1.4); v = int(6140 * (1 - (1 - p) ** 4) / 40)
    if v != v_prec and tt < 1.7: pose(tic(2600), tt, 0.25); v_prec = v
pose(kick(0.9), 1.70); pose(bande(rng.standard_normal(at(0.25)), 2000, 9000) * env(at(0.25), 0.002, 0.06) * 0.6, 1.90, pan=0.3)
pose(souffle(0.9), 2.1, 0.8)

# 3-14 s : la pulsation démarre sur l'impact du 30 €.
pose(kick(1.2), 3.0); pose(cloche(81, 1.2), 3.25, 0.18); pose(cloche(84, 1.2), 3.45, 0.14)
accords = [([50, 57, 62, 66, 69], 38), ([47, 54, 59, 62, 66], 35), ([43, 50, 55, 59, 62], 31), ([45, 52, 57, 61, 64], 33)]
for b in range(6):                      # mesures de 2 s, de 3 à 15 s
    t0 = 3.0 + b * 2; notes, bas = accords[b % 4]
    pose(nappe(notes, 2.2, 0.11), t0)
    pose(basse(bas, 1.0), t0); pose(basse(bas, 0.6), t0 + 1.0)
    for k, m in enumerate([notes[-1] + 12, notes[-2] + 12, notes[-3] + 12]):
        if t0 >= 5: pose(piano(m), t0 + 0.5 + k * 0.5, 1.0, pan=(-0.3 if k % 2 else 0.3))
for k in range(int((13.5 - 3.0) / 0.5) + 1):
    tt = 3.0 + k * 0.5
    pose(kick(0.55), tt)
    if tt >= 5.0: pose(hat(), tt + 0.25, 0.9, pan=0.2)
pose(souffle(0.7, False), 4.6, 0.9); pose(kick(0.9), 5.0)
pose(souffle(0.6, False), 8.7, 0.8); pose(kick(0.9), 9.0)
for i in range(10):                     # chaque produit qui tombe dans le panier
    tt = 9.35 + i * 0.38 + 1.3; pose(cloche(76 + (i % 4) * 2, 0.5), tt, 0.10, pan=(-0.4 if i % 2 else 0.4))
pose(souffle(0.6), 13.4, 1.0)

# 14-17,5 s : le résultat. Silence relatif, compteur, cloche, puis l'accord majeur.
for k in range(60):
    tt = 14.2 + k * 0.016
    p = min(1, (tt - 14.2) / 0.95)
    if p < 1 and k % (1 + k // 12) == 0: pose(tic(3200), tt, 0.2)
pose(cloche(86, 3.0), 15.15, 0.35); pose(cloche(79, 3.0), 15.15, 0.25); pose(kick(1.0), 15.15)
pose(nappe([50, 57, 62, 66, 69, 74], 2.4, 0.13), 15.15)
for i in range(3): pose(tic(1800), 15.5 + i * 0.17, 0.3)

# 17,5-22 s : les plats, un glissé par assiette.
pose(souffle(0.6, False), 17.2, 0.9); pose(kick(0.9), 17.6)
for b in range(2):
    t0 = 17.6 + b * 2.2; notes, bas = accords[(b + 2) % 4]
    pose(nappe(notes, 2.4, 0.11), t0); pose(basse(bas, 1.0), t0)
for k in range(9): pose(kick(0.5), 17.6 + k * 0.5); pose(hat(), 17.85 + k * 0.5, 0.8)
for k in range(1, 4): pose(souffle(0.45, False), 18.2 + k * 0.9 - 0.4, 0.55)

# 22-26,5 s : signature. Impact, accord qui s'ouvre, scintillement sur l'adresse.
pose(kick(1.2), 22.0); pose(nappe([50, 57, 62, 66, 69, 74, 78], 4.5, 0.15), 22.0); pose(basse(38, 3.0), 22.0)
for i, m in enumerate([74, 78, 81, 86]): pose(piano(m, 2.0), 22.6 + i * 0.12, 1.2)
for i, m in enumerate([86, 90, 93, 98]): pose(cloche(m, 1.5), 25.1 + i * 0.09, 0.08, pan=(-0.3 + i * 0.2))

# fondu final, normalisation
f = np.ones(N); f[at(25.6):] = np.linspace(1, 0, N - at(25.6)); mix *= f[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open("son.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype("<i2").tobytes())
print("ok", round(T, 1))
