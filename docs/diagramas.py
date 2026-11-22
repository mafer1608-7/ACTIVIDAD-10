"""
Genera el diagrama de bloques y el diagrama de conexiones del robot movil.
Salida: diagrama_bloques.png/.svg y diagrama_conexiones.png/.svg (en esta carpeta).
Uso: python diagramas.py   (requiere matplotlib)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

OUT = os.path.dirname(os.path.abspath(__file__))

C_VBAT = "#c0392b"   # potencia bateria
C_5V = "#e67e22"
C_3V3 = "#d4ac0d"
C_GND = "#2c3e50"
C_PWM = "#8e44ad"    # control motores
C_I2C = "#1f77b4"
C_SIG = "#16a085"    # senales digitales
C_RF = "#7f8c8d"

COL_BLOQUE = {
    "energia": "#fdecea", "control": "#e8f4fd", "sensor": "#eafaf1",
    "actuador": "#f4ecf7", "app": "#fef9e7",
}


def bloque(ax, x, y, w, h, texto, tipo, fs=9, negrita_1=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                fc=COL_BLOQUE[tipo], ec="#34495e", lw=1.3))
    lineas = texto.split("\n")
    if negrita_1:
        ax.text(x + w / 2, y + h / 2 + (len(lineas) - 1) * 1.6, lineas[0], ha="center",
                va="center", fontsize=fs + 1, weight="bold")
        if len(lineas) > 1:
            ax.text(x + w / 2, y + h / 2 - 1.6, "\n".join(lineas[1:]), ha="center",
                    va="center", fontsize=fs - 0.5, linespacing=1.3)
    else:
        ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs)


def flecha(ax, pts, color, etiqueta=None, pos=0.5, doble=False, punteada=False, lw=2.0,
           desp=(0, 1.8)):
    ls = (0, (4, 3)) if punteada else "-"
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=lw, ls=ls, solid_capstyle="round")
    estilo = "<|-|>" if doble else "-|>"
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle=estilo, color=color, lw=lw, ls=ls,
                                mutation_scale=14, shrinkA=0, shrinkB=0))
    if doble and len(pts) > 2:
        ax.annotate("", xy=pts[0], xytext=pts[1],
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                    mutation_scale=14, shrinkA=0, shrinkB=0))
    if etiqueta:
        # etiqueta sobre el segmento mas largo
        seg = max(zip(pts[:-1], pts[1:]), key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
        x = seg[0][0] + (seg[1][0] - seg[0][0]) * pos + desp[0]
        y = seg[0][1] + (seg[1][1] - seg[0][1]) * pos + desp[1]
        ax.text(x, y, etiqueta, fontsize=8, color=color, ha="center", va="center",
                weight="bold", bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.9))


# ============================ DIAGRAMA DE BLOQUES ============================
def diagrama_bloques():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 160); ax.set_ylim(-8, 102); ax.axis("off")
    ax.text(80, 99, "Diagrama de bloques – Robot móvil diferencial (diseño propio)",
            ha="center", fontsize=15, weight="bold")

    # Energia
    bloque(ax, 4, 76, 30, 13, "Baterías 2×18650\nLi-ion, 7.4 V nominal\n(8.4 V cargada)", "energia")
    bloque(ax, 4, 56, 30, 12, "BMS 2S\nprotección sobrecarga,\nsobredescarga, corto", "energia")
    bloque(ax, 4, 36, 30, 12, "Fusible 3 A +\ninterruptor general", "energia")
    bloque(ax, 4, 12, 30, 14, "Regulador 5 V\ndel L298N (jumper 5V)\nLM2596 opcional", "energia")
    flecha(ax, [(19, 76), (19, 68.5)], C_VBAT)
    flecha(ax, [(19, 56), (19, 48.5)], C_VBAT)
    flecha(ax, [(19, 36), (19, 26.5)], C_VBAT, "VBAT 7.4 V", desp=(9, 0))

    # Control
    bloque(ax, 58, 36, 42, 28, "ESP32 DevKit V1\nMicrocontrolador doble núcleo 240 MHz\n"
           "WiFi 802.11 b/g/n + Bluetooth\n\n• Lectura de sensores (I²C, GPIO)\n"
           "• Fusión → rumbo respecto al norte\n• PWM de motores / odometría\n"
           "• Servidor web + WebSocket", "control", fs=9)

    # Sensores
    bloque(ax, 50, 78, 32, 14, "IMU + magnetómetro\nBNO055  (o MPU6050 +\nQMC5883L) – en mástil", "sensor")
    bloque(ax, 88, 78, 26, 14, "Proximidad\nHC-SR04 (frente)\nVL53L0X opcional", "sensor")
    bloque(ax, 76, 6, 30, 13, "Encoders ópticos\n2× H206 + disco\n20 ranuras", "sensor")
    bloque(ax, 38, 44, 14, 9, "Divisor\nV_bat", "energia", fs=8)

    # Actuadores
    bloque(ax, 118, 40, 34, 16, "Driver L298N\n2 puentes H, 2 A/canal\nPWM 1 kHz", "actuador")
    bloque(ax, 114, 10, 19, 13, "Motor TT\nizquierdo\n1:48", "actuador")
    bloque(ax, 137, 10, 19, 13, "Motor TT\nderecho\n1:48", "actuador")

    # App
    bloque(ax, 122, 74, 34, 18, "Aplicación (celular / PC)\nPágina web servida por el ESP32\n"
           "• Joystick modo manual\n• Brújula: rumbo vs. norte\n• Distancia y batería", "app")

    # Conexiones de potencia
    flecha(ax, [(34, 40), (54, 40), (54, 30), (135, 30), (135, 39.5)], C_VBAT, "VBAT → VM", pos=0.7)
    flecha(ax, [(34, 19), (64, 19), (64, 35.5)], C_5V, "+5 V → VIN", pos=0.35)
    flecha(ax, [(34, 44.5), (37.5, 48.5)], C_VBAT)
    flecha(ax, [(52.5, 48.5), (57.5, 48.5)], C_SIG, "ADC", desp=(0, 2.4))

    # Datos
    flecha(ax, [(70, 64.5), (66, 77.5)], C_I2C, "I²C", doble=True, desp=(-4, 0))
    flecha(ax, [(92, 64.5), (98, 77.5)], C_SIG, "TRIG / ECHO", doble=True, desp=(-9, 0))
    flecha(ax, [(91, 19.5), (91, 35.5)], C_SIG, "pulsos", desp=(5, 0))
    flecha(ax, [(100.5, 50), (117.5, 50)], C_PWM, "PWM + DIR", desp=(0, 2.4))
    flecha(ax, [(128, 39.5), (124, 23.5)], C_PWM)
    flecha(ax, [(142, 39.5), (146, 23.5)], C_PWM)
    flecha(ax, [(114, 14), (106.5, 13)], C_RF, punteada=True, lw=1.5)
    ax.text(110, 9.5, "acople\nmecánico", fontsize=7, color=C_RF, ha="center")

    # Inalambrico
    flecha(ax, [(100.5, 60), (121.5, 79)], C_RF, "WiFi (AP)\nWebSocket", doble=True,
           punteada=True, desp=(4, 1))

    # Leyenda
    items = [(C_VBAT, "Potencia batería (7.4 V)"), (C_5V, "Alimentación 5 V"),
             (C_I2C, "Bus I²C"), (C_SIG, "Señales digitales / analógicas"),
             (C_PWM, "Control de motores"), (C_RF, "Inalámbrico / mecánico")]
    for i, (c, t) in enumerate(items):
        x = 4 + (i % 3) * 36
        y = -2 - (i // 3) * 3.4
        ax.plot([x, x + 5], [y, y], color=c, lw=3)
        ax.text(x + 6.5, y, t, va="center", fontsize=8.5)
    ax.text(4, -1.5, "", fontsize=1)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"diagrama_bloques.{ext}"), dpi=150, bbox_inches="tight")
    plt.close(fig)


# =========================== DIAGRAMA DE CONEXIONES ===========================
ESP_IZQ = ["EN", "VP/36", "VN/39", "D34", "D35", "D32", "D33", "D25", "D26", "D27",
           "D14", "D12", "D13", "GND", "VIN"]
ESP_DER = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "TX2", "RX2",
           "D4", "D2", "D15", "GND", "3V3"]
Y0, DY = 95, 5          # y del primer pin y separacion
XE0, XE1 = 82, 100      # bordes del ESP32


def y_pin(lista, nombre):
    return Y0 - DY * lista.index(nombre)


def etiqueta_red(ax, x, y, red, lado="izq", largo=5):
    col = {"+3V3": C_3V3, "+5V": C_5V, "VBAT": C_VBAT, "GND": C_GND}[red]
    x2 = x - largo if lado == "izq" else x + largo
    ax.plot([x, x2], [y, y], color=col, lw=1.8)
    ax.text(x2 + (-0.6 if lado == "izq" else 0.6), y, red, ha="right" if lado == "izq" else "left",
            va="center", fontsize=7.5, color="white", weight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc=col, ec="none"))


def modulo(ax, x, y0, y1, w, titulo, sub="", abajo=False):
    ax.add_patch(Rectangle((x, y0), w, y1 - y0, fc="#f7f9fb", ec="#34495e", lw=1.4))
    ax.text(x + w / 2, (y0 - 1.5) if abajo else (y1 + 1.5), titulo, ha="center",
            va="top" if abajo else "bottom", fontsize=9.5, weight="bold")
    if sub:
        ax.text(x + w / 2, (y0 + y1) / 2, sub, ha="center", va="center", fontsize=7.5,
                color="#555", linespacing=1.3)


def pin(ax, x, y, nombre, lado):
    ax.plot(x, y, "o", ms=3.5, color="#34495e")
    ax.text(x + (1 if lado == "der" else -1), y, nombre, fontsize=7.5,
            ha="left" if lado == "der" else "right", va="center")


def resistencia(ax, xc, yc, valor, vertical=False):
    w, h = (2.2, 6) if vertical else (6, 2.2)
    ax.add_patch(Rectangle((xc - w / 2, yc - h / 2), w, h, fc="white", ec="#34495e", lw=1.3, zorder=3))
    ax.text(xc + (2 if vertical else 0), yc + (0 if vertical else 2.4), valor, fontsize=7.5,
            ha="left" if vertical else "center", va="center")


def cable(ax, pts, color):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=1.8, solid_capstyle="round", zorder=2)


REN_S3 = {"D25": "GPIO4", "D26": "GPIO5", "D27": "GPIO6", "D14": "GPIO7", "D33": "GPIO15",
          "D32": "GPIO16", "D19": "GPIO17", "D18": "GPIO18", "D21": "GPIO8", "D22": "GPIO9",
          "D34": "GPIO10", "D35": "GPIO11", "VP/36": "GPIO1", "VIN": "5V", "GND": "GND", "3V3": "3V3"}


def diagrama_conexiones(s3=False):
    def lab(n):
        return REN_S3.get(n, "") if s3 else n

    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_xlim(-2, 182); ax.set_ylim(-8, 112); ax.axis("off")
    ax.text(90, 109, ("Diagrama de conexiones – ESP32-S3 DevKitC-1" if s3 else "Diagrama de conexiones – ESP32 DevKit V1 (30 pines)"),
            ha="center", fontsize=15, weight="bold")

    # ESP32
    ax.add_patch(Rectangle((XE0, 20), XE1 - XE0, 80, fc="#1b2631", ec="black", lw=1.5))
    ax.text((XE0 + XE1) / 2, 85 if s3 else 60, ("ESP32-S3\nDevKitC-1" if s3 else "ESP32\nDevKit V1\n\nWROOM-32"), color="white", ha="center",
            va="center", fontsize=10, weight="bold")
    ax.add_patch(Rectangle((87, 15.5), 8, 4.5, fc="#bdc3c7", ec="black"))
    ax.text(91, 13.5, "USB", ha="center", fontsize=7.5)
    for i, n in enumerate(ESP_IZQ):
        y = Y0 - DY * i
        ax.plot(XE0, y, "s", ms=4, color="#f1c40f")
        ax.text(XE0 + 1.2, y, lab(n), color="white", fontsize=7, va="center")
    for i, n in enumerate(ESP_DER):
        y = Y0 - DY * i
        ax.plot(XE1, y, "s", ms=4, color="#f1c40f")
        ax.text(XE1 - 1.2, y, lab(n), color="white", fontsize=7, va="center", ha="right")

    # --- L298N (alineado con los pines del ESP32) ---
    tb = [("IN4", "D32"), ("IN3", "D33"), ("ENA", "D25"), ("IN1", "D26"),
          ("IN2", "D27"), ("ENB", "D14")]
    xt0, xt1 = 38, 56
    modulo(ax, xt0, 32, 72, xt1 - xt0, "L298N", "", abajo=True)
    for n, p in tb:
        y = y_pin(ESP_IZQ, p)
        pin(ax, xt1, y, n, "izq")
        cable(ax, [(xt1, y), (XE0, y)], C_PWM)
    izq = [("12V", 70, "VBAT"), ("5V", 65, "+5V"), ("GND", 60, "GND")]
    for n, y, red in izq:
        pin(ax, xt0, y, n, "der")
        etiqueta_red(ax, xt0, y, red, "izq", 4)
    salidas = [("OUT1", 52), ("OUT2", 47), ("OUT3", 41), ("OUT4", 36)]
    for n, y in salidas:
        pin(ax, xt0, y, n, "der")
    # motores
    for (nombre, ya, yb, ym) in (("Motor\nizq.", 52, 47, 49.5), ("Motor\nder.", 41, 36, 38.5)):
        circ = plt.Circle((14, ym), 4.2, fc="#f9e79f", ec="#34495e", lw=1.3)
        ax.add_patch(circ)
        ax.text(14, ym, nombre, ha="center", va="center", fontsize=7)
        cable(ax, [(xt0, ya), (24, ya), (24, ym + 1.5), (18.2, ym + 1.5)], "#555")
        cable(ax, [(xt0, yb), (22, yb), (22, ym - 1.5), (18.2, ym - 1.5)], "#555")
    ax.text(30, 76, "Quitar jumpers ENA y ENB\n470 µF / 16 V entre 12V y GND", fontsize=7.5, ha="center", color=C_VBAT)

    # --- Encoders H206 ---
    modulo(ax, 50, 74.5, 83, 8, "H206 ×2 (opcional)" if s3 else "H206 ×2")
    for n, p in (("D0 izq", "D34"), ("D0 der", "D35")):
        y = y_pin(ESP_IZQ, p)
        pin(ax, 58, y, n, "izq")
        cable(ax, [(58, y), (XE0, y)], C_SIG)
    etiqueta_red(ax, 50, 81, "+3V3", "izq", 3)
    etiqueta_red(ax, 50, 76.5, "GND", "izq", 3)

    # --- Divisor de bateria -> VP/36 ---
    yv = y_pin(ESP_IZQ, "VP/36")
    etiqueta_red(ax, 50, yv, "VBAT", "izq", 3)
    cable(ax, [(50, yv), (XE0, yv)], C_SIG)
    resistencia(ax, 58, yv, "R1 10 kΩ")
    ax.plot(68, yv, "o", ms=4, color="black")
    cable(ax, [(68, yv), (68, 98)], C_GND)
    resistencia(ax, 68, 95, "R2 3.3 kΩ", vertical=True)
    etiqueta_red(ax, 68, 98, "GND", "der", 0.01)
    ax.text(58, 99, ("Divisor de batería (opcional)\nV_ADC = VBAT × 0.248" if s3 else "V_ADC = VBAT × 0.248\n(8.4 V → 2.08 V)"), fontsize=7, ha="center")

    # --- Alimentacion ESP32 ---
    etiqueta_red(ax, XE0, y_pin(ESP_IZQ, "GND"), "GND", "izq", 8)
    etiqueta_red(ax, XE0, y_pin(ESP_IZQ, "VIN"), "+5V", "izq", 8)
    etiqueta_red(ax, XE1, y_pin(ESP_DER, "GND"), "GND", "der", 8)
    etiqueta_red(ax, XE1, y_pin(ESP_DER, "3V3"), "+3V3", "der", 8)
    ax.text(XE1 + 13, y_pin(ESP_DER, "3V3") - 3.5, "salida 3.3 V del regulador\ninterno (sensores)",
            fontsize=7, color="#555")

    # --- IMU (I2C) ---
    xi = 126
    modulo(ax, xi, 72, 98, 26, "IMU + magnetómetro",
           ("GY-273 QMC5883L (0x0D)\n+\nGY-521 MPU6050 (0x68)\n(opcional)" if s3 else "BNO055 (0x28)\n— o —\nMPU6050 (0x68)\n+ QMC5883L (0x0D)"))
    for n, p in (("SCL", "D22"), ("SDA", "D21")):
        y = y_pin(ESP_DER, p)
        pin(ax, xi, y, n, "der")
        cable(ax, [(XE1, y), (xi, y)], C_I2C)
    ax.plot(112, 90, "o", ms=4, color=C_I2C); ax.plot(116, 75, "o", ms=4, color=C_I2C)
    cable(ax, [(112, 90), (112, 103), (160, 103), (160, 87)], C_I2C)
    cable(ax, [(116, 75), (116, 69.5), (162, 69.5), (162, 82)], C_I2C)
    ax.text(136, 104.5, "mismo bus I²C (cable por dentro del mástil)", fontsize=7, ha="center",
            color=C_I2C)
    ax.add_patch(Rectangle((157, 80), 12, 9, fc="#f7f9fb", ec="#34495e", lw=1.2, ls="--"))
    ax.text(163, 84.5, "VL53L0X\n(0x29)\nopcional", fontsize=7, ha="center", va="center")
    etiqueta_red(ax, xi + 26, 94, "+3V3", "der", 3)
    etiqueta_red(ax, xi + 26, 76, "GND", "der", 3)

    # --- HC-SR04 ---
    xh = 140
    modulo(ax, xh, 52, 66, 22, "HC-SR04 (5 V)")
    yt, ye = y_pin(ESP_DER, "D19"), y_pin(ESP_DER, "D18")
    cable(ax, [(XE1, yt), (106, yt), (106, 63), (xh, 63)], C_SIG)
    # ECHO entrega 5 V: divisor R3/R4 antes del ESP32
    cable(ax, [(XE1, ye), (110, ye), (110, 58)], C_SIG)
    ax.plot(118, 58, "o", ms=4, color="black")
    cable(ax, [(110, 58), (xh, 58)], C_SIG)
    resistencia(ax, 130, 58, "R3 1 kΩ")
    cable(ax, [(118, 58), (118, 49)], C_GND)
    resistencia(ax, 118, 53, "R4 2 kΩ", vertical=True)
    etiqueta_red(ax, 118, 49, "GND", "der", 0.01)
    pin(ax, xh, 63, "TRIG", "der")
    pin(ax, xh, 58, "ECHO", "der")
    etiqueta_red(ax, xh + 22, 63, "+5V", "der", 3)
    etiqueta_red(ax, xh + 22, 56, "GND", "der", 3)
    ax.text(123, 48.5, "divisor 5 V → 3.3 V en ECHO", fontsize=7, ha="left", color=C_SIG)

    # --- LED ---
    if not s3:
        ax.text(XE1 + 3, y_pin(ESP_DER, "D2"), "D2: LED integrado (estado WiFi)", fontsize=7.5,
                va="center", color="#555")

    # --- Cadena de potencia ---
    ax.text(4, 8, "Alimentación", fontsize=10, weight="bold")
    cadena = ["2× 18650\n7.4 V", "BMS 2S", "Fusible\n3 A", "Interruptor", "VBAT"]
    x = 4
    for i, t in enumerate(cadena):
        col = C_VBAT if t == "VBAT" else "#fdecea"
        ax.add_patch(FancyBboxPatch((x, -4), 13, 8, boxstyle="round,pad=0.3", fc=col, ec="#34495e"))
        ax.text(x + 6.5, 0, t, ha="center", va="center", fontsize=8,
                color="white" if t == "VBAT" else "black", weight="bold" if t == "VBAT" else None)
        if i < len(cadena) - 1:
            ax.annotate("", xy=(x + 16.5, 0), xytext=(x + 13.6, 0),
                        arrowprops=dict(arrowstyle="-|>", color=C_VBAT, lw=1.8))
        x += 17
    ax.annotate("", xy=(x + 3.5, 0), xytext=(x - 3.4, 0),
                arrowprops=dict(arrowstyle="-|>", color=C_VBAT, lw=1.8))
    ax.add_patch(FancyBboxPatch((x + 4, -4), 20, 8, boxstyle="round,pad=0.3", fc="#fdecea", ec="#34495e"))
    ax.text(x + 14, 0, "Regulador 5 V\ndel L298N", ha="center", va="center", fontsize=8)
    ax.annotate("", xy=(x + 30.5, 0), xytext=(x + 24.4, 0),
                arrowprops=dict(arrowstyle="-|>", color=C_5V, lw=1.8))
    ax.add_patch(FancyBboxPatch((x + 31, -4), 10, 8, boxstyle="round,pad=0.3", fc=C_5V, ec="#34495e"))
    ax.text(x + 36, 0, "+5V", ha="center", va="center", fontsize=8, color="white", weight="bold")
    ax.text(x + 45, 0, "Todas las tierras (GND) unidas en un punto común.\n"
            "No alimentar por USB y VIN a la vez sin diodo.", fontsize=7.5, va="center")

    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"diagrama_conexiones{'_s3' if s3 else ''}.{ext}"), dpi=150,
                    bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    diagrama_bloques()
    diagrama_conexiones()
    diagrama_conexiones(s3=True)
    print("listo")
