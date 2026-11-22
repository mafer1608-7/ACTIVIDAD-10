"""Grafica de EJEMPLO (datos simulados) del rumbo actual y deseado durante una mision con evasion.
No son mediciones del robot: sirve para ver el formato. La grafica real sale de graficar_csv.py."""
import os
import random

from graficar_csv import dibujar

AQUI = os.path.dirname(os.path.abspath(__file__))
random.seed(3)
dt = 0.1
t = [i * dt for i in range(0, 321)]
act, obj = [], []
h = 3.0
for x in t:
    # fase de la mision: alinear (3-6 s) -> avanzar -> evasion (14-21 s) -> avanzar
    if x < 3:
        objetivo_local = 3.0
    elif x < 14:
        objetivo_local = 90.0
    elif x < 16.5:
        objetivo_local = 180.0       # gira 90 grados respecto al rumbo objetivo
    elif x < 19.5:
        objetivo_local = 180.0       # paso lateral
    else:
        objetivo_local = 90.0        # vuelve al rumbo objetivo
    err = objetivo_local - h
    h += max(-45, min(45, 0.9 * err)) * dt * 1.6 + random.gauss(0, 0.25)
    act.append(h % 360)
    obj.append(90.0 if x >= 3 else 0.0)
dibujar(t, act, obj, os.path.join(AQUI, "fig", "grafica_ejemplo.png"), ejemplo=True)
print("listo")
