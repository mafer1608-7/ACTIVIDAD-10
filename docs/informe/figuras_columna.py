"""Figuras de ancho de columna (8,9 cm) para los informes IEEE: se leen sin ampliar."""
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

K = dict(bat="#c0392b", v5="#e67e22", v33="#b7950b", gnd="#2c3e50", i2c="#2471a3",
         dig="#17a589", mot="#8e44ad", ln="#2c3e50")
FS = 6.3


def lienzo(h, w=3.6):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100 * h / w)
    ax.axis("off")
    return fig, ax


def caja(ax, x, y, w, h, txt, fc="#eaf2f8", ec=K["ln"], fs=FS, bold=False, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.6",
                                fc=fc, ec=ec, lw=0.9, ls=ls))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.2)


def flecha(ax, p, q, color=K["ln"], ls="-", lw=1.1, both=False):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<|-|>" if both else "-|>", color=color, lw=lw,
                                                     ls=ls, shrinkA=0, shrinkB=0, mutation_scale=7))


def guardar(fig, nombre):
    fig.savefig(os.path.join(SAL, nombre), dpi=300, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ bloques
def bloques():
    fig, ax = lienzo(3.3)
    ax.set_ylim(0, 92)
    caja(ax, 2, 74, 30, 15, "HC-SR04\ndistancia frontal", "#e8f6f3")
    caja(ax, 35, 74, 30, 15, "MPU6050\ngiroscopio y\nacelerómetro", "#e8f6f3")
    caja(ax, 68, 74, 30, 15, "Magnetómetro\nGY-273\n(no instalado)", "#f2f3f4", ec="#7f8c8d", ls="--", fs=5.6)
    caja(ax, 2, 50, 96, 16, "ESP32-S3 DevKitC-1\nlectura de sensores · estimación del rumbo\nPWM de motores · servidor web WiFi",
         "#d6eaf8", bold=False)
    flecha(ax, (17, 74), (17, 66), K["dig"], both=True)
    ax.text(19, 69.3, "TRIG/ECHO", fontsize=5.2, color=K["dig"])
    flecha(ax, (50, 74), (50, 66), K["i2c"], both=True)
    ax.text(52, 69.3, "I²C", fontsize=5.2, color=K["i2c"])
    flecha(ax, (83, 74), (83, 66), "#95a5a6", ls="--")
    ax.text(85, 69.3, "sin conexión", fontsize=5.0, color="#7f8c8d")
    caja(ax, 2, 24, 44, 18, "Aplicación web\n(PC o celular)\nmanual / autónomo", "#fef9e7", bold=True)
    caja(ax, 54, 24, 44, 18, "Driver L298N\n(regulador de 5 V\nintegrado)", "#f4ecf7", bold=True)
    flecha(ax, (24, 42), (24, 50), "#7f8c8d", ls="--", both=True)
    ax.text(26, 45, "WiFi AP, HTTP 100 ms", fontsize=5.0, color="#7f8c8d")
    flecha(ax, (68, 50), (68, 42), K["mot"], lw=1.4)
    ax.text(70, 46, "PWM + DIR", fontsize=5.2, color=K["mot"], ha="left")
    flecha(ax, (88, 42), (88, 50), K["v5"], lw=1.4)
    ax.text(90, 45.5, "5 V", fontsize=5.2, color=K["v5"])
    caja(ax, 2, 2, 44, 14, "Baterías 2×18650\n7,4 V + interruptor", "#fdedec")
    caja(ax, 54, 2, 44, 14, "Motores TT\nizquierdo y derecho", "#f4ecf7")
    flecha(ax, (46, 9), (54, 31), K["bat"], lw=1.4)
    ax.text(47, 20, "12 V", fontsize=5.2, color=K["bat"], ha="left")
    flecha(ax, (76, 24), (76, 16), K["mot"], lw=1.4)
    guardar(fig, "col_bloques.png")


# ------------------------------------------------------------------ esquema motores
def esq_motores():
    fig, ax = lienzo(3.55)
    ax.set_ylim(0, 98.6)

    def pin(x, y, txt, dentro="d", color="black", fs=5.6):
        ax.plot([x], [y], "o", ms=2.2, color=K["ln"])
        ax.text(x + (1.6 if dentro == "d" else -1.6), y, txt, ha="left" if dentro == "d" else "right", va="center",
                fontsize=fs, color=color)

    def tag(x, y, txt, color, dy=-4.0):
        ax.plot([x, x], [y, y + dy], color=color, lw=1.2)
        ax.text(x, y + dy - 0.6, txt, ha="center", va="top", fontsize=5.4, fontweight="bold", color=color)

    # ESP32
    ax.add_patch(Rectangle((2, 22), 24, 70, fc="#1c2833", ec="black", lw=1.2))
    ax.text(14, 90, "ESP32-S3", ha="center", va="top", color="white", fontsize=6.5, fontweight="bold")
    izq = [("GPIO4", 78), ("GPIO5", 70), ("GPIO6", 62), ("GPIO7", 54), ("GPIO15", 46), ("GPIO16", 38)]
    for n, y in izq:
        ax.plot([26], [y], "s", ms=2.6, color="#f1c40f")
        ax.text(24.6, y, n, ha="right", va="center", fontsize=5.6, color="white")
    for n, x, c in (("5V", 8, K["v5"]), ("GND", 18, K["gnd"])):
        ax.plot([x], [22], "s", ms=2.6, color="#f1c40f")
        ax.text(x, 23.4, n, ha="center", va="bottom", fontsize=5.4, color="white")
        tag(x, 22, "+5V" if n == "5V" else "GND", c)
    # L298N
    ax.add_patch(Rectangle((52, 22), 26, 70, fc="#f4f6f7", ec=K["ln"], lw=1.2))
    ax.text(65, 93, "L298N", ha="center", va="bottom", fontsize=6.5, fontweight="bold")
    for (n, y), (_, y2) in zip([("ENA", 78), ("IN1", 70), ("IN2", 62), ("ENB", 54), ("IN3", 46), ("IN4", 38)], izq):
        pin(52, y, n, "d")
        ax.plot([26, 52], [y, y], color=K["mot"], lw=1.2)
    for x, n, c in ((57, "12V", K["bat"]), (65, "5V", K["v5"]), (73, "GND", K["gnd"])):
        ax.plot([x], [22], "o", ms=2.2, color=K["ln"])
        ax.text(x, 23.4, n, ha="center", va="bottom", fontsize=5.4)
        tag(x, 22, {"12V": "VBAT", "5V": "+5V", "GND": "GND"}[n], c)
    # salidas a motores
    for (yc, t, ya, yb) in ((74, "Motor\nizq.", 78, 70), (46, "Motor\nder.", 54, 38)):
        ax.plot([78], [ya], "o", ms=2.2, color=K["ln"]); ax.plot([78], [yb], "o", ms=2.2, color=K["ln"])
        ax.text(76.6, ya, "OUT" + ("1" if yc == 74 and ya == 78 else "3"), ha="right", va="center", fontsize=5.2)
        ax.text(76.6, yb, "OUT" + ("2" if yc == 74 else "4"), ha="right", va="center", fontsize=5.2)
        ax.add_patch(Circle((92, yc), 6.2, fc="#f9e79f", ec=K["ln"], lw=0.9))
        ax.text(92, yc, t, ha="center", va="center", fontsize=5.0)
        ax.plot([78, 84, 86], [ya, ya, yc + 2], color="#555", lw=1.0)
        ax.plot([78, 84, 86], [yb, yb, yc - 2], color="#555", lw=1.0)
    # bateria
    ax.add_patch(Rectangle((30, 1), 23, 9, fc="#fdedec", ec=K["ln"], lw=0.9))
    ax.text(41.5, 5.5, "2×18650 · 7,4 V", ha="center", va="center", fontsize=5.2)
    ax.add_patch(Rectangle((58, 1), 18, 9, fc="#fdedec", ec=K["ln"], lw=0.9))
    ax.text(67, 5.5, "Interruptor", ha="center", va="center", fontsize=5.2)
    ax.plot([53, 58], [5.5, 5.5], color=K["bat"], lw=1.4)
    ax.plot([76, 80], [5.5, 5.5], color=K["bat"], lw=1.4)
    ax.text(80.8, 5.5, "VBAT", ha="left", va="center", fontsize=5.4, fontweight="bold", color=K["bat"])
    ax.text(2, 5.5, "Alimentación", fontsize=5.4, style="italic", color="#555", va="center")
    guardar(fig, "col_esq_motores.png")


# ------------------------------------------------------------------ esquema sensores
def esq_sensores():
    fig, ax = lienzo(3.55)
    ax.set_ylim(0, 98.6)

    def pin(x, y, txt, fs=5.6):
        ax.plot([x], [y], "o", ms=2.2, color=K["ln"])
        ax.text(x + 1.6, y, txt, ha="left", va="center", fontsize=fs)

    def tag_h(x, y, txt, color):
        ax.plot([x - 6, x], [y, y], color=color, lw=1.2)
        ax.text(x - 6.6, y, txt, ha="right", va="center", fontsize=5.4, fontweight="bold", color=color)

    def tag_v(x, y, txt, color, dy=-4.0):
        ax.plot([x, x], [y, y + dy], color=color, lw=1.2)
        ax.text(x, y + dy - 0.6, txt, ha="center", va="top", fontsize=5.4, fontweight="bold", color=color)

    ax.add_patch(Rectangle((2, 22), 24, 70, fc="#1c2833", ec="black", lw=1.2))
    ax.text(14, 90, "ESP32-S3", ha="center", va="top", color="white", fontsize=6.5, fontweight="bold")
    for n, y in (("GPIO8", 80), ("GPIO9", 72), ("GPIO17", 46), ("GPIO18", 36)):
        ax.plot([26], [y], "s", ms=2.6, color="#f1c40f")
        ax.text(24.6, y, n, ha="right", va="center", fontsize=5.6, color="white")
    for n, x, c in (("5V", 6, K["v5"]), ("3V3", 14, K["v33"]), ("GND", 22, K["gnd"])):
        ax.plot([x], [22], "s", ms=2.6, color="#f1c40f")
        ax.text(x, 23.4, n, ha="center", va="bottom", fontsize=5.2, color="white")
        tag_v(x, 22, "+" + n if n != "GND" else "GND", c)

    # MPU6050
    ax.add_patch(Rectangle((64, 62), 34, 32, fc="#f4f6f7", ec=K["ln"], lw=1.2))
    ax.text(81, 95, "GY-521 (MPU6050)", ha="center", va="bottom", fontsize=6.0, fontweight="bold")
    for n, y in (("VCC", 89), ("SDA", 80), ("SCL", 72), ("GND", 66)):
        pin(64, y, n)
    tag_h(64, 89, "+3V3", K["v33"])
    tag_h(64, 66, "GND", K["gnd"])
    ax.plot([26, 64], [80, 80], color=K["i2c"], lw=1.4)
    ax.plot([26, 64], [72, 72], color=K["i2c"], lw=1.4)
    ax.text(45, 81.2, "SDA", fontsize=5.2, color=K["i2c"], ha="center")
    ax.text(45, 73.2, "SCL", fontsize=5.2, color=K["i2c"], ha="center")

    # HC-SR04 + divisor
    ax.add_patch(Rectangle((64, 14), 34, 38, fc="#f4f6f7", ec=K["ln"], lw=1.2))
    ax.text(81, 53, "HC-SR04 (5 V)", ha="center", va="bottom", fontsize=6.0, fontweight="bold")
    for n, y in (("VCC", 46), ("TRIG", 38), ("ECHO", 30), ("GND", 20)):
        pin(64, y, n)
    tag_h(64, 46, "+5V", K["v5"])
    tag_h(64, 20, "GND", K["gnd"])
    ax.plot([26, 64], [46, 38.0 + 0], color="none")
    ax.plot([26, 40, 40, 64], [46, 46, 38, 38], color=K["dig"], lw=1.4)       # TRIG
    ax.text(33, 47.3, "TRIG", fontsize=5.2, color=K["dig"], ha="center")
    ax.plot([26, 36], [36, 36], color=K["dig"], lw=1.4)                        # ECHO -> divisor
    ax.plot([36, 36, 44], [36, 30, 30], color=K["dig"], lw=1.4)
    ax.add_patch(Rectangle((44, 28.8), 10, 2.4, fc="white", ec=K["ln"], lw=0.9))
    ax.plot([54, 64], [30, 30], color=K["dig"], lw=1.4)
    ax.text(49, 33.0, "1 kΩ", fontsize=5.2, ha="center")
    ax.plot([36], [30], "o", ms=2.4, color="black")
    ax.plot([36, 36], [30, 25.5], color=K["dig"], lw=1.4)
    ax.add_patch(Rectangle((34.9, 19.5), 2.2, 6.0, fc="white", ec=K["ln"], lw=0.9))
    ax.text(38.4, 22.5, "2 kΩ", fontsize=5.2, ha="left", va="center")
    ax.plot([36, 36], [19.5, 16.5], color=K["gnd"], lw=1.2)
    ax.text(36, 15.9, "GND", ha="center", va="top", fontsize=5.4, fontweight="bold", color=K["gnd"])
    ax.text(2, 3.0, "ECHO entrega 5 V: el divisor 1 kΩ / 2 kΩ lo baja a 3,3 V.", fontsize=5.2, color="#555")
    ax.text(2, 0.0, "I²C compartido: SDA = GPIO8, SCL = GPIO9.", fontsize=5.2, color="#555")
    guardar(fig, "col_esq_sensores.png")


# ------------------------------------------------------------------ flujo
def flujo():
    fig, ax = lienzo(4.7)
    ax.set_ylim(0, 130.5)
    W, H = 43, 17
    L, R = 2, 55
    filas = [108, 84, 60, 36, 12]

    def b(x, y, txt, fc="#eaf2f8"):
        caja(ax, x, y, W, H, txt, fc, fs=5.9)

    b(L, filas[0], "INICIO\nrumbo, distancia y\nvelocidad desde la app", "#fef9e7")
    b(R, filas[0], "ALINEAR\ngirar en el sitio hasta\n|error| < 6°")
    b(R, filas[1], "AVANZAR\nmantener el rumbo\n(control proporcional)")
    b(L, filas[1], "META\nparar y reportar", "#e8f8f5")
    b(R, filas[2], "¿obstáculo ≤ 25 cm?\n(2 lecturas seguidas)", "#fdedec")
    b(L, filas[2], "EV_GIRO\ngirar 90° respecto\nal rumbo objetivo", "#fdedec")
    b(L, filas[3], "EV_LADO\navanzar 35 cm\nde lado", "#fdedec")
    b(R, filas[3], "EV_VOLVER\ngirar de nuevo al\nrumbo objetivo", "#fdedec")
    b(R, filas[4], "EV_REVISAR\n¿sigue el obstáculo?\nsí: otro paso (EV_GIRO)", "#fdedec")
    b(L, filas[4], "volver a AVANZAR\n(rumbo recuperado)")
    mid = H / 2
    flecha(ax, (L + W, filas[0] + mid), (R, filas[0] + mid))
    flecha(ax, (R + W / 2, filas[0]), (R + W / 2, filas[1] + H))
    flecha(ax, (R, filas[1] + mid), (L + W, filas[1] + mid))
    ax.text((L + W + R) / 2, filas[1] + mid + 1.6, "avance ≥ d", fontsize=5.2, ha="center")
    flecha(ax, (R + 10, filas[1]), (R + 10, filas[2] + H))
    flecha(ax, (R + W - 10, filas[2] + H), (R + W - 10, filas[1]))
    ax.text(R + W - 8.5, (filas[1] + filas[2] + H) / 2, "no", fontsize=5.2, ha="left", va="center")
    flecha(ax, (R, filas[2] + mid), (L + W, filas[2] + mid))
    ax.text((L + W + R) / 2, filas[2] + mid + 1.6, "sí", fontsize=5.2, ha="center")
    flecha(ax, (L + W / 2, filas[2]), (L + W / 2, filas[3] + H))
    flecha(ax, (L + W, filas[3] + mid), (R, filas[3] + mid))
    flecha(ax, (R + W / 2, filas[3]), (R + W / 2, filas[4] + H))
    flecha(ax, (R, filas[4] + mid), (L + W, filas[4] + mid))
    ax.text((L + W + R) / 2, filas[4] + mid + 1.6, "libre", fontsize=5.2, ha="center")
    ax.text(2, 4.0, "Si el lado de evasión está bloqueado se alterna el lado (máx. 6 intentos).", fontsize=5.0, color="#555")
    ax.text(2, 0.5, "Los pasos laterales no cuentan en la distancia recorrida.", fontsize=5.0, color="#555")
    guardar(fig, "col_flujo.png")


# ------------------------------------------------------------------ CAD
def cad():
    im = Image.open(os.path.join(ROBOTO, "cad", "vista_ensamble.png")).convert("RGB")
    w, h = im.size
    iso = im.crop((60, 40, w // 2 + 20, h - 40))
    lienzo_ = Image.new("RGB", (iso.width, iso.height), "white")
    lienzo_.paste(iso, (0, 0))
    lienzo_.save(os.path.join(SAL, "col_cad_iso.png"))
    Image.open(os.path.join(ROBOTO, "cad", "vista_placas_dxf.png")).convert("RGB").save(os.path.join(SAL, "col_cad_placas.png"))


if __name__ == "__main__":
    bloques()
    esq_motores()
    esq_sensores()
    flujo()
    cad()
    print(sorted(f for f in os.listdir(SAL) if f.startswith("col_")))

