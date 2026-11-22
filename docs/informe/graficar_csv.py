"""Grafica el rumbo actual y el deseado a partir del CSV descargado de la aplicacion (registro_robot.csv).

Uso:  python graficar_csv.py registro_robot.csv [t_inicio] [t_fin]
Genera grafica_rumbo.png (ancho de una columna IEEE) junto al CSV. Usa SOLO los datos del archivo.
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AZUL, NARANJA, PAPEL = "#1d3f73", "#d4501b", "#faf7ec"


def leer(ruta):
    t, act, obj = [], [], []
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            try:
                t.append(float(fila["t_s"]))
                act.append(float(fila["rumbo_deg"]))
                obj.append(float(fila["objetivo_deg"]))
            except (ValueError, KeyError):
                continue
    return t, act, obj


def dibujar(t, act, obj, salida, ejemplo=False):
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor(PAPEL)
    ax.plot(t, obj, color=NARANJA, lw=1.3, ls="--", label="deseado")
    ax.plot(t, act, color=AZUL, lw=1.4, label="actual")
    ax.set_ylim(0, 360)
    ax.set_yticks([0, 90, 180, 270, 360])
    ax.set_xlabel("tiempo (s)", fontsize=7)
    ax.set_ylabel("rumbo (°)", fontsize=7)
    ax.tick_params(labelsize=6.5)
    ax.grid(color="#cfc9b4", lw=0.5)
    ax.legend(fontsize=6.5, loc="upper right", frameon=True, facecolor=PAPEL, edgecolor="#999")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    if ejemplo:
        ax.text(0.5, 0.06, "EJEMPLO ILUSTRATIVO · datos simulados", transform=ax.transAxes, ha="center",
                fontsize=6.5, color="#b03a2e", fontweight="bold")
    fig.tight_layout(pad=0.4)
    fig.savefig(salida, dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ruta = sys.argv[1]
    t, act, obj = leer(ruta)
    if not t:
        sys.exit("No se encontraron datos en el CSV.")
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else t[0]
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else t[-1]
    sel = [(a, b, c) for a, b, c in zip(t, act, obj) if t0 <= a <= t1]
    tt, aa, oo = zip(*sel)
    tt = [x - tt[0] for x in tt]
    salida = os.path.join(os.path.dirname(os.path.abspath(ruta)), "grafica_rumbo.png")
    dibujar(tt, aa, oo, salida)
    print("Grafica guardada en", salida, "con", len(tt), "muestras")

