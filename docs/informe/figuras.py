"""Figuras 'tal como se construyo' para los informes IEEE (esquematico, bloques, flujo, CAD)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
ROBOTO = os.path.dirname(os.path.dirname(AQUI))
SAL = os.path.join(AQUI, "fig")
os.makedirs(SAL, exist_ok=True)

C = dict(bat="#c0392b", v5="#e67e22", v33="#b7950b", gnd="#2c3e50", i2c="#2471a3",
         dig="#17a589", mot="#8e44ad", ln="#2c3e50")


def caja(ax, x, y, w, h, txt, fc="#eaf2f8", ec=C["ln"], fs=8, bold=False, ls="-", r=0.02):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.005,rounding_size={r}",
                                fc=fc, ec=ec, lw=1.2, ls=ls))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def flecha(ax, p, q, color=C["ln"], ls="-", lw=1.4, both=False):
    st = "<|-|>" if both else "-|>"
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=st, color=color, lw=lw, ls=ls,
                                                     shrinkA=0, shrinkB=0, mutation_scale=9))


def lienzo(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


# ------------------------------------------------------------------ 1) bloques
def bloques():
    fig, ax = lienzo(9.2, 5.8)
    # alimentacion (columna izquierda)
    caja(ax, 0.02, 0.72, 0.17, 0.20, "Baterías\n2×18650\n7,4 V", fc="#fdedec", bold=True)
    caja(ax, 0.02, 0.40, 0.17, 0.18, "Interruptor\ngeneral", fc="#fdedec")
    caja(ax, 0.02, 0.06, 0.17, 0.20, "Regulador 5 V\n(del L298N)", fc="#fdebd0")
    flecha(ax, (0.105, 0.72), (0.105, 0.58), C["bat"], lw=2)
    flecha(ax, (0.105, 0.40), (0.105, 0.26), C["bat"], lw=2)
    # sensores
    caja(ax, 0.30, 0.82, 0.22, 0.14, "HC-SR04\ndistancia frontal", fc="#e8f6f3")
    caja(ax, 0.55, 0.82, 0.20, 0.14, "MPU6050\ngiroscopio y\nacelerómetro", fc="#e8f6f3")
    caja(ax, 0.79, 0.82, 0.19, 0.14, "Magnetómetro\nGY-273\n(no instalado)", fc="#f2f3f4", ec="#7f8c8d", ls="--", fs=7.5)
    # ESP32
    caja(ax, 0.30, 0.46, 0.34, 0.28, "ESP32-S3 DevKitC-1\n\n• Lectura de sensores\n• Estimación del rumbo\n• Control PWM de motores\n• Servidor web (WiFi AP)", fc="#d6eaf8")
    # actuacion
    caja(ax, 0.72, 0.46, 0.14, 0.28, "Driver\nL298N\n2 puentes H", fc="#f4ecf7", bold=True)
    caja(ax, 0.90, 0.58, 0.09, 0.14, "Motor\nizq.", fc="#f4ecf7", fs=7.5)
    caja(ax, 0.90, 0.40, 0.09, 0.14, "Motor\nder.", fc="#f4ecf7", fs=7.5)
    # aplicacion
    caja(ax, 0.30, 0.06, 0.34, 0.18, "Aplicación web (PC / celular)\nmodo manual y autónomo\nrumbo actual y deseado", fc="#fef9e7", bold=True)

    flecha(ax, (0.41, 0.82), (0.41, 0.74), C["dig"], both=True)
    ax.text(0.425, 0.775, "TRIG / ECHO", fontsize=6.8, color=C["dig"], ha="left")
    flecha(ax, (0.65, 0.82), (0.58, 0.74), C["i2c"], both=True)
    ax.text(0.655, 0.775, "I²C", fontsize=6.8, color=C["i2c"], ha="left")
    flecha(ax, (0.885, 0.82), (0.64, 0.74), "#95a5a6", ls="--")
    ax.text(0.80, 0.755, "sin conexión", fontsize=6.3, color="#7f8c8d", ha="center", rotation=-12)
    flecha(ax, (0.64, 0.60), (0.72, 0.60), C["mot"], lw=2)
    ax.text(0.68, 0.62, "PWM\n+ DIR", fontsize=6, color=C["mot"], ha="center", va="bottom")
    flecha(ax, (0.86, 0.65), (0.90, 0.65), C["mot"], lw=2)
    flecha(ax, (0.86, 0.50), (0.90, 0.47), C["mot"], lw=2)
    flecha(ax, (0.47, 0.24), (0.47, 0.46), "#7f8c8d", ls="--", both=True)
    ax.text(0.455, 0.33, "WiFi (AP)\nHTTP cada 100 ms", fontsize=6.5, color="#7f8c8d", ha="right")
    # potencia: 12 V por debajo del ESP32 hasta el driver
    ax.plot([0.19, 0.19, 0.79, 0.79], [0.49, 0.36, 0.36, 0.46], color=C["bat"], lw=2)
    flecha(ax, (0.79, 0.41), (0.79, 0.46), C["bat"], lw=2)
    ax.text(0.62, 0.375, "12 V (VBAT)", fontsize=6.8, color=C["bat"], ha="left")
    flecha(ax, (0.19, 0.16), (0.30, 0.50), C["v5"], lw=2)
    ax.text(0.215, 0.14, "5 V", fontsize=6.8, color=C["v5"], ha="left")
    ax.text(0.02, 0.005, "Rojo: potencia (batería)   Naranja: 5 V   Verde: señales digitales   Azul: bus I²C   "
                         "Violeta: motores   Gris: inalámbrico / no instalado", fontsize=6.6, color="#555")
    fig.savefig(os.path.join(SAL, "fig_bloques.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ 2) esquematico
def esquematico():
    fig, ax = plt.subplots(figsize=(9.4, 6.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 72)
    ax.axis("off")

    def hilo(pts, color, lw=1.7):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round")

    def etiqueta_pin(x, y, txt, lado, fs=7, color="black"):
        ax.plot([x], [y], "o", ms=3, color=C["ln"])
        ax.text(x + (1.0 if lado == "d" else -1.0), y, txt, ha="left" if lado == "d" else "right",
                va="center", fontsize=fs, color=color)

    def tag(x, y, txt, color, dx=0.0, dy=-3.2, sentido="abajo"):
        """etiqueta de red con un trazo corto"""
        ax.plot([x, x + dx], [y, y + dy], color=color, lw=1.7)
        ax.text(x + dx, y + dy + (-0.4 if dy < 0 else 0.4), txt, ha="center", va="top" if dy < 0 else "bottom",
                fontsize=6.6, fontweight="bold", color=color)

    def modulo(x, y, w, h, titulo, ec=C["ln"], ls="-", fc="#f4f6f7"):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.4, ls=ls))
        ax.text(x + w / 2, y + h + 0.8, titulo, ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # ---------------- ESP32-S3
    ax.add_patch(Rectangle((38, 18), 18, 44, fc="#1c2833", ec="black", lw=2))
    ax.text(47, 60.6, "ESP32-S3\nDevKitC-1", ha="center", va="top", color="white", fontsize=9, fontweight="bold")
    izq = [("GPIO4", 52), ("GPIO5", 48), ("GPIO6", 44), ("GPIO7", 40), ("GPIO15", 36), ("GPIO16", 32)]
    for n, y in izq:
        ax.plot([38], [y], "s", ms=3.5, color="#f1c40f")
        ax.text(39.2, y, n, ha="left", va="center", fontsize=7, color="white")
    der = [("GPIO8", 52), ("GPIO9", 48), ("GPIO17", 36), ("GPIO18", 32)]
    for n, y in der:
        ax.plot([56], [y], "s", ms=3.5, color="#f1c40f")
        ax.text(54.8, y, n, ha="right", va="center", fontsize=7, color="white")
    for n, x, col in (("5V", 43, C["v5"]), ("3V3", 47, C["v33"]), ("GND", 51, C["gnd"])):
        ax.plot([x], [18], "s", ms=3.5, color="#f1c40f")
        ax.text(x, 19.0, n, ha="center", va="bottom", fontsize=7, color="white")
        tag(x, 18, {"5V": "+5V", "3V3": "+3V3", "GND": "GND"}[n], col, dy=-3.4)
    # ---------------- L298N
    modulo(10, 14, 16, 46, "Driver L298N")
    pines_der = [("ENA", 52), ("IN1", 48), ("IN2", 44), ("ENB", 40), ("IN3", 36), ("IN4", 32)]
    for (n, y), (_, y2) in zip(pines_der, izq):
        etiqueta_pin(26, y, n, "i")
        hilo([(26, y), (38, y)], C["mot"])
    for n, y in (("OUT1", 55), ("OUT2", 51), ("OUT3", 41), ("OUT4", 37)):
        etiqueta_pin(10, y, n, "d")
    for (yc, t, ya, yb) in ((53, "Motor\nizq.", 55, 51), (39, "Motor\nder.", 41, 37)):
        ax.add_patch(Circle((3.4, yc), 3.0, fc="#f9e79f", ec=C["ln"], lw=1.3))
        ax.text(3.4, yc, t, ha="center", va="center", fontsize=5.8)
        hilo([(6.4, yc + 1.1), (8, yc + 1.1), (8, ya), (10, ya)], "#555", lw=1.2)
        hilo([(6.4, yc - 1.1), (8, yc - 1.1), (8, yb), (10, yb)], "#555", lw=1.2)
    for x, n, col in ((13, "12V", C["bat"]), (18, "5V", C["v5"]), (23, "GND", C["gnd"])):
        ax.plot([x], [14], "o", ms=3, color=C["ln"])
        ax.text(x, 15, n, ha="center", va="bottom", fontsize=7)
        tag(x, 14, {"12V": "VBAT", "5V": "+5V", "GND": "GND"}[n], col, dy=-3.4)

    # ---------------- bateria e interruptor
    ax.add_patch(Rectangle((2, 1.5), 12, 5.2, fc="#fdedec", ec=C["ln"], lw=1.3))
    ax.text(8, 4.1, "2×18650\n7,4 V", ha="center", va="center", fontsize=7)
    ax.add_patch(Rectangle((19, 1.5), 12, 5.2, fc="#fdedec", ec=C["ln"], lw=1.3))
    ax.text(25, 4.1, "Interruptor", ha="center", va="center", fontsize=7)
    hilo([(14, 5.2), (19, 5.2)], C["bat"], lw=2)
    hilo([(31, 5.2), (34, 5.2)], C["bat"], lw=2)
    ax.text(34.5, 5.2, "VBAT", ha="left", va="center", fontsize=6.6, fontweight="bold", color=C["bat"])
    hilo([(8, 1.5), (8, 0.2)], C["gnd"], lw=2)
    ax.text(8, 0.0, "GND", ha="center", va="top", fontsize=6.6, fontweight="bold", color=C["gnd"])
    ax.text(2, 8.0, "Alimentación", fontsize=7.5, style="italic", color="#555")

    # ---------------- MPU6050
    modulo(76, 44, 20, 16, "GY-521 (MPU6050, 0x68)")
    for n, y in (("VCC", 57), ("SDA", 52), ("SCL", 48), ("GND", 45)):
        etiqueta_pin(76, y, n, "d")
    hilo([(56, 52), (76, 52)], C["i2c"], lw=2)
    hilo([(56, 48), (76, 48)], C["i2c"], lw=2)
    ax.text(66, 53, "SDA", fontsize=6.6, color=C["i2c"], ha="center")
    ax.text(66, 49, "SCL", fontsize=6.6, color=C["i2c"], ha="center")
    ax.plot([76, 72], [57, 57], color=C["v33"], lw=1.7); ax.text(71.5, 57, "+3V3", ha="right", va="center", fontsize=6.6, fontweight="bold", color=C["v33"])
    ax.plot([76, 72], [45, 45], color=C["gnd"], lw=1.7); ax.text(71.5, 45, "GND", ha="right", va="center", fontsize=6.6, fontweight="bold", color=C["gnd"])

    # magnetometro (no instalado)
    ax.add_patch(Rectangle((76, 64), 20, 6, fc="#f2f3f4", ec="#7f8c8d", lw=1.2, ls="--"))
    ax.text(86, 67, "GY-273 (magnetómetro)\nNO instalado", ha="center", va="center", fontsize=6.6, color="#7f8c8d")

    # ---------------- HC-SR04
    modulo(76, 20, 20, 16, "HC-SR04 (5 V)")
    for n, y in (("VCC", 33), ("TRIG", 30), ("ECHO", 26), ("GND", 23)):
        etiqueta_pin(76, y, n, "d")
    ax.plot([76, 72], [33, 33], color=C["v5"], lw=1.7); ax.text(71.5, 33, "+5V", ha="right", va="center", fontsize=6.6, fontweight="bold", color=C["v5"])
    ax.plot([76, 72], [23, 23], color=C["gnd"], lw=1.7); ax.text(71.5, 23, "GND", ha="right", va="center", fontsize=6.6, fontweight="bold", color=C["gnd"])
    hilo([(56, 36), (66, 36), (66, 30), (76, 30)], C["dig"], lw=2)
    ax.text(61, 37, "TRIG", fontsize=6.6, color=C["dig"], ha="center")
    # divisor de tension del ECHO
    hilo([(56, 32), (62, 32), (62, 26)], C["dig"], lw=2)
    ax.text(57.5, 33, "ECHO", fontsize=6.6, color=C["dig"], ha="left")
    ax.add_patch(Rectangle((64.5, 25), 5.5, 2.0, fc="white", ec=C["ln"], lw=1.2))
    hilo([(62, 26), (64.5, 26)], C["dig"], lw=2)
    hilo([(70, 26), (76, 26)], C["dig"], lw=2)
    ax.text(67.2, 28.0, "1 kΩ", fontsize=6.6, ha="center")
    ax.plot([62], [26], "o", ms=3.5, color="black")
    hilo([(62, 26), (62, 24.3)], C["dig"], lw=2)
    ax.add_patch(Rectangle((60.9, 21.3), 2.2, 3.0, fc="white", ec=C["ln"], lw=1.2))
    ax.text(63.6, 22.8, "2 kΩ", fontsize=6.6, ha="left", va="center")
    ax.plot([62, 62], [21.3, 19.6], color=C["gnd"], lw=1.7)
    ax.text(62, 19.2, "GND", ha="center", va="top", fontsize=6.6, fontweight="bold", color=C["gnd"])
    ax.text(79, 17.2, "Divisor 5 V → 3,3 V en ECHO", fontsize=6.6, color=C["dig"], ha="left")

    ax.text(1, 70, "Todos los GND y los 5 V se unen en un punto común.", fontsize=6.8, color="#555", ha="left")
    fig.savefig(os.path.join(SAL, "fig_esquematico.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ 3) flujo de navegacion
def flujo():
    fig, ax = lienzo(9.0, 5.6)
    cw, ch = 0.21, 0.14
    cols = [0.01, 0.27, 0.53, 0.79]

    def est(i, y, txt, fc="#eaf2f8", w=cw, h=ch):
        caja(ax, cols[i], y, w, h, txt, fc=fc, fs=7.6)

    est(0, 0.80, "INICIO\nrumbo, distancia y\nvelocidad desde la app", fc="#fef9e7")
    est(1, 0.80, "ALINEAR\ngirar en el sitio hasta\n|error| < 6°")
    est(2, 0.80, "AVANZAR\nmantener el rumbo\n(control proporcional)")
    est(3, 0.80, "META\nparar y reportar", fc="#e8f8f5")
    est(2, 0.47, "¿obstáculo a\n≤ 25 cm?\n(2 lecturas seguidas)", fc="#fdedec")
    est(1, 0.47, "EV_GIRO\ngirar 90° respecto\nal rumbo objetivo", fc="#fdedec")
    est(0, 0.47, "EV_LADO\navanzar 35 cm\nde lado", fc="#fdedec")
    est(0, 0.14, "EV_VOLVER\ngirar de nuevo al\nrumbo objetivo", fc="#fdedec")
    est(1, 0.14, "EV_REVISAR\n¿sigue el obstáculo?", fc="#fdedec")
    caja(ax, cols[2], 0.14, cw, ch, "volver a AVANZAR\n(rumbo recuperado)", fc="#eaf2f8", fs=7.6)

    flecha(ax, (cols[0] + cw, 0.87), (cols[1], 0.87))
    flecha(ax, (cols[1] + cw, 0.87), (cols[2], 0.87))
    flecha(ax, (cols[2] + cw, 0.87), (cols[3], 0.87))
    ax.text((cols[2] + cw + cols[3]) / 2, 0.905, "avance\n≥ d", fontsize=6.3, ha="center", va="bottom")
    flecha(ax, (cols[2] + 0.06, 0.80), (cols[2] + 0.06, 0.61))
    flecha(ax, (cols[2] + 0.15, 0.61), (cols[2] + 0.15, 0.80))
    ax.text(cols[2] + 0.16, 0.70, "no", fontsize=6.5, ha="left")
    flecha(ax, (cols[2], 0.54), (cols[1] + cw, 0.54))
    ax.text((cols[2] + cols[1] + cw) / 2, 0.555, "sí", fontsize=6.5, ha="center")
    flecha(ax, (cols[1], 0.54), (cols[0] + cw, 0.54))
    flecha(ax, (cols[0] + 0.105, 0.47), (cols[0] + 0.105, 0.28))
    flecha(ax, (cols[0] + cw, 0.21), (cols[1], 0.21))
    flecha(ax, (cols[1] + cw, 0.21), (cols[2], 0.21))
    ax.text((cols[1] + cw + cols[2]) / 2, 0.225, "libre", fontsize=6.5, ha="center")
    # si sigue el obstaculo: vuelve a EV_GIRO
    ax.plot([cols[1] + 0.105, cols[1] + 0.105], [0.28, 0.47], color=C["ln"], lw=1.4, ls="--")
    ax.annotate("", xy=(cols[1] + 0.105, 0.47), xytext=(cols[1] + 0.105, 0.30),
                arrowprops=dict(arrowstyle="-|>", color=C["ln"], lw=1.4, ls="--", shrinkA=0, shrinkB=0, mutation_scale=9))
    ax.text(cols[1] + 0.115, 0.37, "sigue", fontsize=6.5, ha="left")
    ax.text(0.01, 0.05, "Si el lado de evasión está bloqueado se alterna de lado (máximo 6 intentos). "
                        "Los pasos laterales no se cuentan en la distancia recorrida.", fontsize=6.6, color="#555")
    fig.savefig(os.path.join(SAL, "fig_flujo.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ 4) CAD (reutiliza las vistas ya generadas)
def cad():
    im = Image.open(os.path.join(ROBOTO, "cad", "vista_ensamble.png")).convert("RGB")
    w, h = im.size
    lienzo_ = Image.new("RGB", (w, h + 70), "white")
    lienzo_.paste(im, (0, 70))
    lienzo_.save(os.path.join(SAL, "fig_cad_ensamble.png"))
    Image.open(os.path.join(ROBOTO, "cad", "vista_placas_dxf.png")).convert("RGB").save(os.path.join(SAL, "fig_cad_placas.png"))


if __name__ == "__main__":
    bloques()
    esquematico()
    flujo()
    cad()
    print("figuras en", SAL, os.listdir(SAL))



