"""
Robot movil diferencial - chasis hibrido (placas de corte laser + soportes impresos 3D)
Modelo parametrico en CadQuery. Genera:
  STEP/  -> piezas y ensamble (abrir en SolidWorks: Archivo > Abrir > *.step)
  DXF/   -> placas para corte laser (acrilico 3 mm)
  STL/   -> piezas para impresion 3D (PETG o PLA)

Sistema de coordenadas (mm): origen en el suelo bajo el eje de las ruedas,
+X = frente del robot, +Y = izquierda, +Z = arriba.

IMPORTANTE: las medidas del motor TT, rueda loca y modulos son valores tipicos.
Midan sus piezas reales con calibrador y ajusten la seccion PARAMETROS.
"""
import math
import os
import cadquery as cq

# ============================== PARAMETROS ==============================
R_CHASIS = 90.0        # radio de las placas (diametro 180 mm)
T_PLACA = 3.0          # espesor acrilico

# Rueda (rueda tipica para motor TT)
D_RUEDA = 65.0
W_RUEDA = 26.0
Y_RUEDA = 75.0         # distancia del centro del robot al centro de la rueda

# Motor TT amarillo (doble eje)
M_LARGO = 70.0         # largo total (caja + motor)
M_ALTO = 22.5
M_ANCHO = 18.8         # en direccion del eje
M_EJE_DESDE_PUNTA = 11.5   # del extremo de la caja reductora al eje
M_AGUJEROS_X = (-12.0, -29.5)  # posicion X de los 2 agujeros pasantes (eje en X=0)
GAP_MOTOR_RUEDA = 3.0

T_SOPORTE = 3.0        # espesor de la base del soporte de motor
T_PARED = 4.0          # espesor de la pared del soporte de motor

# Altura del eje = radio de la rueda
Z_EJE = D_RUEDA / 2
Z_PLACA_INF = Z_EJE - M_ALTO / 2 - T_SOPORTE - T_PLACA   # cara inferior placa inferior
Z_PLACA_INF_TOP = Z_PLACA_INF + T_PLACA

L_SEPARADOR = 40.0     # separadores M3 de laton (no magneticos) entre placas
Z_PLACA_SUP = Z_PLACA_INF_TOP + L_SEPARADOR
Z_PLACA_SUP_TOP = Z_PLACA_SUP + T_PLACA

# Rueda loca (bola metalica). Ajustar a la comprada.
X_RUEDA_LOCA = -70.0
H_RUEDA_LOCA = 12.0          # altura de la rueda loca (suelo -> cara de montaje)
SEP_AGUJEROS_LOCA = 24.0     # separacion de sus 2 agujeros (en X)
USAR_PATIN = True            # True: patin impreso en lugar de rueda loca comprada

# Mastil del magnetometro / IMU
H_MASTIL = 80.0

M3 = 3.4               # agujero pasante M3
D_SEPARADORES = [(67.5, 39.0), (67.5, -39.0), (-67.5, 39.0), (-67.5, -39.0)]

OUT = os.path.dirname(os.path.abspath(__file__))


# ============================== AYUDANTES ==============================
def caja(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cil_z(x, y, z0, h, d):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))


def cil_y(x, z, y0, h, d):
    return cq.Workplane("XY").add(
        cq.Solid.makeCylinder(d / 2, h, cq.Vector(x, y0, z), cq.Vector(0, 1, 0)))


def cil_x(y, z, x0, h, d):
    return cq.Workplane("XY").add(
        cq.Solid.makeCylinder(d / 2, h, cq.Vector(x0, y, z), cq.Vector(1, 0, 0)))


def ranura_z(x, y, z0, h, largo, d, ang=0):
    """Ranura (agujero alargado) vertical, largo total incluyendo radios."""
    return (cq.Workplane("XY").slot2D(largo, d, ang).extrude(h)
            .translate((x, y, z0)))


def agujeros(solido, pts, d, z0, h):
    for (x, y) in pts:
        solido = solido.cut(cil_z(x, y, z0 - 1, h + 2, d))
    return solido


def espejo_y(pts):
    return pts + [(x, -y) for (x, y) in pts]


# ======================= POSICIONES DERIVADAS =======================
Y_MOTOR_EXT = Y_RUEDA - W_RUEDA / 2 - GAP_MOTOR_RUEDA      # cara exterior del motor
Y_MOTOR_INT = Y_MOTOR_EXT - M_ANCHO                         # cara interior del motor
Y_PARED_INT = Y_MOTOR_INT - T_PARED
X_MOTOR_FRENTE = M_EJE_DESDE_PUNTA
X_MOTOR_ATRAS = M_EJE_DESDE_PUNTA - M_LARGO

# agujeros M3 del soporte de motor (lado izquierdo, Y+)
SOP_X0, SOP_X1 = -45.0, 18.0
AGUJ_SOPORTE = [(15.0, Y_PARED_INT + 6.0), (15.0, Y_MOTOR_EXT - 5.0),
                (-40.0, Y_PARED_INT - 4.0), (-20.0, Y_PARED_INT - 4.0)]

# Bateria 2x18650 (portapilas)
BAT = dict(x=-15.0, y=0.0, l=77.0, w=41.0, h=21.0)

# Sensor ultrasonico frontal HC-SR04
X_US_PARED = 78.0
Z_US = Z_PLACA_INF_TOP + 3.0 + 15.0


# ============================== PIEZAS ==============================
def ranuras_ruedas(p):
    for s in (1, -1):
        y0 = Y_RUEDA - W_RUEDA / 2 - 2.0
        p = p.cut(caja(-36, 36, min(s * y0, s * 100), max(s * y0, s * 100), -1, T_PLACA + 1))
    return p


def placa_inferior():
    p = ranuras_ruedas(cil_z(0, 0, 0, T_PLACA, 2 * R_CHASIS))
    pts = []
    pts += D_SEPARADORES
    pts += espejo_y(AGUJ_SOPORTE)
    # soporte sensor frontal
    pts += [(72.0, 18.0), (72.0, -18.0)]
    # rueda loca
    pts += [(X_RUEDA_LOCA + SEP_AGUJEROS_LOCA / 2, 0), (X_RUEDA_LOCA - SEP_AGUJEROS_LOCA / 2, 0)]
    # sensor de ranura H206 (encoder optico) junto al eje interior
    pts += espejo_y([(16.0, Y_PARED_INT - 6.0)])
    p = agujeros(p, pts, M3, 0, T_PLACA)
    # paso de cables
    p = p.cut(cil_z(40, 0, -1, T_PLACA + 2, 18))
    p = p.cut(cil_z(-62, 50, -1, T_PLACA + 2, 10)).cut(cil_z(-62, -50, -1, T_PLACA + 2, 10))
    # ranuras para amarre (bridas) del portapilas
    for x in (BAT["x"] - 28, BAT["x"] + 28):
        for y in (BAT["w"] / 2 + 3.5, -(BAT["w"] / 2 + 3.5)):
            p = p.cut(caja(x - 2, x + 2, y - 1.5, y + 1.5, -1, T_PLACA + 1))
    return p


def placa_superior():
    # las ruedas (D65) sobresalen por encima de la placa superior -> mismas ranuras
    p = ranuras_ruedas(cil_z(0, 0, 0, T_PLACA, 2 * R_CHASIS))
    pts_fijos = list(D_SEPARADORES)
    pts_mastil = [(10, 10), (10, -10), (-10, 10), (-10, -10)]
    pasacables = [(40, 0, 20), (-55, 28, 15), (-55, -28, 15)]
    interruptor = (-74.0, 0.0, 13.0, 19.5)   # interruptor basculante (KCD1)
    p = agujeros(p, pts_fijos + pts_mastil, M3, 0, T_PLACA)
    for (x, y, d) in pasacables:
        p = p.cut(cil_z(x, y, -1, T_PLACA + 2, d))
    xi, yi, ai, bi = interruptor
    p = p.cut(caja(xi - ai / 2, xi + ai / 2, yi - bi / 2, yi + bi / 2, -1, T_PLACA + 1))

    # rejilla de agujeros M3 cada 10 mm para montar ESP32, driver, regulador...
    rejilla = []
    for i in range(-8, 9):
        for j in range(-8, 9):
            x, y = 10.0 * i, 10.0 * j
            if math.hypot(x, y) > R_CHASIS - 9:
                continue
            if abs(x) < 20 and abs(y) < 20:
                continue
            if abs(x) < 42 and abs(y) > 54:      # borde de las ranuras de rueda
                continue
            if x > 66 and abs(y) < 9:            # flecha de frente
                continue
            if any(math.hypot(x - a, y - b) < 8 for (a, b) in pts_fijos):
                continue
            if any(math.hypot(x - a, y - b) < d / 2 + 5 for (a, b, d) in pasacables):
                continue
            if abs(x - xi) < ai / 2 + 5 and abs(y - yi) < bi / 2 + 5:
                continue
            rejilla.append((x, y))
    p = agujeros(p, rejilla, 3.2, 0, T_PLACA)
    # marca de frente (flecha pasante pequena)
    flecha = (cq.Workplane("XY").polyline([(80, 0), (72, 5), (72, -5)]).close()
              .extrude(T_PLACA + 2).translate((0, 0, -1)))
    return p.cut(flecha)


def soporte_motor_izq():
    """Soporte en L para motor TT (lado izquierdo, +Y). Coordenadas globales."""
    z0 = Z_PLACA_INF_TOP
    base = caja(SOP_X0, SOP_X1, Y_PARED_INT - 8.0, Y_MOTOR_EXT, z0, z0 + T_SOPORTE)
    # despeje para el disco del encoder en el eje interior
    base = base.cut(caja(-15, SOP_X1 + 1, Y_PARED_INT - 9.0, Y_PARED_INT, z0 - 1, z0 + T_SOPORTE + 1))
    pared = caja(SOP_X0, 8.0, Y_PARED_INT, Y_MOTOR_INT, z0, z0 + T_SOPORTE + M_ALTO)
    s = base.union(pared)
    # agujero para el eje interior (encoder) y ranuras para los tornillos del motor
    s = s.cut(cil_y(0, Z_EJE, Y_PARED_INT - 1, T_PARED + 2, 10.0))
    for xa in M_AGUJEROS_X:
        s = s.cut(cq.Workplane("XZ").slot2D(5.0, M3, 0).extrude(-(T_PARED + 2))
                  .translate((xa, Y_PARED_INT - 1, Z_EJE)))
    # nervio de refuerzo
    nervio = (cq.Workplane("YZ").polyline([(Y_PARED_INT - 8.0, 0), (Y_PARED_INT, 0),
                                           (Y_PARED_INT, 14.0)]).close()
              .extrude(4.0).translate((SOP_X0, 0, z0 + T_SOPORTE)))
    s = s.union(nervio)
    s = agujeros(s, AGUJ_SOPORTE, M3, z0, T_SOPORTE)
    return s


def soporte_ultrasonico():
    z0 = Z_PLACA_INF_TOP
    base = caja(66, X_US_PARED + 3, -25, 25, z0, z0 + 3)
    pared = caja(X_US_PARED, X_US_PARED + 3, -25, 25, z0, z0 + 33)
    s = base.union(pared)
    for y in (13.0, -13.0):
        s = s.cut(cil_x(y, Z_US, X_US_PARED - 1, 5, 16.6))
    # agujeros M2 alternativos para un VL53L0X sobre los transductores
    for y in (-10.0, 10.0):
        s = s.cut(cil_x(y, z0 + 28.5, X_US_PARED - 1, 5, 2.4))
    s = agujeros(s, [(72.0, 18.0), (72.0, -18.0)], M3, z0, 3)
    return s


def separador_rueda_loca():
    h = Z_PLACA_INF - H_RUEDA_LOCA
    if h < 1.0:
        return None
    s = caja(X_RUEDA_LOCA - 17, X_RUEDA_LOCA + 17, -12, 12, H_RUEDA_LOCA, Z_PLACA_INF)
    return agujeros(s, [(X_RUEDA_LOCA + SEP_AGUJEROS_LOCA / 2, 0),
                        (X_RUEDA_LOCA - SEP_AGUJEROS_LOCA / 2, 0)], M3, H_RUEDA_LOCA, h)


def patin_trasero():
    """Patin deslizante impreso que reemplaza la rueda loca (mismos 2 agujeros).
    Punta semiesferica que toca el suelo; para piso liso (baldosa, madera, MDF)."""
    r = 8.0
    z_brida = Z_PLACA_INF - 4.0
    brida = caja(X_RUEDA_LOCA - 17, X_RUEDA_LOCA + 17, -11, 11, z_brida, Z_PLACA_INF)
    cuerpo = cil_z(X_RUEDA_LOCA, 0, r, z_brida - r + 0.01, 2 * r)
    punta = cq.Workplane("XY").sphere(r).translate((X_RUEDA_LOCA, 0, r))
    s = brida.union(cuerpo).union(punta)
    s = s.cut(caja(X_RUEDA_LOCA - 20, X_RUEDA_LOCA + 20, -15, 15, Z_PLACA_INF, Z_PLACA_INF + 5))
    return agujeros(s, [(X_RUEDA_LOCA + SEP_AGUJEROS_LOCA / 2, 0),
                        (X_RUEDA_LOCA - SEP_AGUJEROS_LOCA / 2, 0)], M3, z_brida, 4.0)


def mastil_magnetometro():
    z0 = Z_PLACA_SUP_TOP
    base = caja(-15, 15, -15, 15, z0, z0 + 4)
    tubo = cil_z(0, 0, z0, H_MASTIL, 16)
    top = caja(-16, 16, -13, 13, z0 + H_MASTIL, z0 + H_MASTIL + 3)
    s = base.union(tubo).union(top)
    s = s.cut(cil_z(0, 0, z0 - 1, H_MASTIL + 5, 9))        # cables por dentro
    s = s.cut(caja(-20, -3, -4, 4, z0 + 4, z0 + 14))        # salida de cables
    s = agujeros(s, [(10, 10), (10, -10), (-10, 10), (-10, -10)], M3, z0, 4)
    # ranuras M2.5 para fijar BNO055 / MPU6050+QMC5883L (ajustables)
    zt = z0 + H_MASTIL
    for y in (9.0, -9.0):
        s = s.cut(ranura_z(0, y, zt - 1, 5, 20, 2.7))
    # flecha grabada que indica el frente (+X) para alinear el eje X del sensor
    flecha = (cq.Workplane("XY").polyline([(15, 0), (9, 3.5), (9, -3.5)]).close()
              .extrude(1).translate((0, 0, zt + 2.4)))
    return s.cut(flecha)


# ======================= COMPONENTES DE REFERENCIA =======================
def motor_tt(lado):
    y_int = Y_MOTOR_INT
    z0 = Z_EJE - M_ALTO / 2
    caja_red = caja(X_MOTOR_FRENTE - 45, X_MOTOR_FRENTE, y_int, y_int + M_ANCHO, z0, z0 + M_ALTO)
    motor = cil_x((y_int + M_ANCHO / 2), Z_EJE, X_MOTOR_ATRAS, 26, 18)
    eje = cil_y(0, Z_EJE, y_int - 9, M_ANCHO + 18, 5.4)
    m = caja_red.union(motor).union(eje)
    return m if lado > 0 else m.mirror("XZ")


def rueda(lado):
    r = cil_y(0, Z_EJE, Y_RUEDA - W_RUEDA / 2, W_RUEDA, D_RUEDA)
    return r if lado > 0 else r.mirror("XZ")


def disco_encoder(lado):
    d = cil_y(0, Z_EJE, Y_PARED_INT - 5.0, 1.5, 25)
    return d if lado > 0 else d.mirror("XZ")


def componentes():
    zi, zs = Z_PLACA_INF_TOP, Z_PLACA_SUP_TOP
    c = {}
    c["motor_izq"] = (motor_tt(1), (0.95, 0.8, 0.1))
    c["motor_der"] = (motor_tt(-1), (0.95, 0.8, 0.1))
    c["rueda_izq"] = (rueda(1), (0.2, 0.2, 0.2))
    c["rueda_der"] = (rueda(-1), (0.2, 0.2, 0.2))
    c["encoder_izq"] = (disco_encoder(1), (0.05, 0.05, 0.05))
    c["encoder_der"] = (disco_encoder(-1), (0.05, 0.05, 0.05))
    c["portapilas_2x18650"] = (caja(BAT["x"] - BAT["l"] / 2, BAT["x"] + BAT["l"] / 2,
                                    -BAT["w"] / 2, BAT["w"] / 2, zi, zi + BAT["h"]), (0.3, 0.3, 0.3))
    if not USAR_PATIN:
        c["rueda_loca"] = (cq.Workplane("XY").sphere(H_RUEDA_LOCA / 2)
                           .translate((X_RUEDA_LOCA, 0, H_RUEDA_LOCA / 2)), (0.75, 0.75, 0.75))
    c["hc_sr04"] = (caja(X_US_PARED - 1.6, X_US_PARED, -22.5, 22.5, Z_US - 10, Z_US + 10)
                    .union(cil_x(13, Z_US, X_US_PARED, 12, 16))
                    .union(cil_x(-13, Z_US, X_US_PARED, 12, 16)), (0.1, 0.3, 0.8))
    c["esp32_devkit"] = (caja(2.5, 57.5, -54, -26, zs + 5, zs + 6.6), (0.05, 0.05, 0.05))
    c["tb6612fng"] = (caja(25, 45, 30, 50, zs + 5, zs + 6.6), (0.8, 0.1, 0.1))
    c["regulador_buck"] = (caja(-46.5, -3.5, 34.5, 55.5, zs + 5, zs + 6.6), (0.1, 0.3, 0.8))
    c["imu_bno055"] = (caja(-13, 13, -10, 10, zs + H_MASTIL + 3 + 4, zs + H_MASTIL + 3 + 5.6),
                       (0.5, 0.2, 0.6))
    for i, (x, y) in enumerate(D_SEPARADORES):
        c[f"separador_laton_{i + 1}"] = (cil_z(x, y, zi, L_SEPARADOR, 5.5), (0.85, 0.65, 0.15))
    return c


# ============================== EXPORTACION ==============================
def a_origen(wp):
    bb = wp.val().BoundingBox()
    return wp.translate((-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def main():
    for d in ("STEP", "DXF", "STL"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)

    pinf, psup = placa_inferior(), placa_superior()
    impresas = {
        "soporte_motor_izq": soporte_motor_izq(),
        "soporte_motor_der": soporte_motor_izq().mirror("XZ"),
        "soporte_ultrasonico": soporte_ultrasonico(),
        "mastil_magnetometro": mastil_magnetometro(),
    }
    sep = separador_rueda_loca()
    if sep is not None:
        impresas["separador_rueda_loca"] = sep
    if USAR_PATIN:
        impresas.pop("separador_rueda_loca", None)
        impresas["patin_trasero"] = patin_trasero()

    # placas: STEP + DXF (vista superior para corte laser)
    for nombre, p in (("placa_inferior", pinf), ("placa_superior", psup)):
        cq.exporters.export(p, os.path.join(OUT, "STEP", nombre + ".step"))
        cq.exporters.export(p.section(T_PLACA / 2), os.path.join(OUT, "DXF", nombre + ".dxf"))

    # piezas impresas: STEP + STL (llevadas al origen)
    for nombre, s in impresas.items():
        cq.exporters.export(a_origen(s), os.path.join(OUT, "STEP", nombre + ".step"))
        if nombre == "patin_trasero":   # imprimir con la brida sobre la cama y la punta arriba
            s = s.rotate((0, 0, 0), (1, 0, 0), 180)
        cq.exporters.export(a_origen(s), os.path.join(OUT, "STL", nombre + ".stl"),
                            tolerance=0.05, angularTolerance=0.1)

    # ensamble completo
    asm = cq.Assembly(name="robot_movil")
    asm.add(pinf.translate((0, 0, Z_PLACA_INF)), name="placa_inferior",
            color=cq.Color(0.75, 0.9, 1.0, 0.6))
    asm.add(psup.translate((0, 0, Z_PLACA_SUP)), name="placa_superior",
            color=cq.Color(0.75, 0.9, 1.0, 0.6))
    for nombre, s in impresas.items():
        asm.add(s, name=nombre, color=cq.Color(1.0, 0.5, 0.0))
    for nombre, (s, col) in componentes().items():
        asm.add(s, name=nombre, color=cq.Color(*col))
    asm.export(os.path.join(OUT, "STEP", "ensamble_robot.step"))

    print(f"Altura eje: {Z_EJE:.2f} mm | Despeje placa inferior: {Z_PLACA_INF:.2f} mm")
    print(f"Placa superior a z={Z_PLACA_SUP:.2f} mm | Sensor IMU a z~{Z_PLACA_SUP_TOP + H_MASTIL + 8:.1f} mm")
    print(f"Distancia entre ruedas (centro a centro): {2 * Y_RUEDA:.1f} mm")
    return asm


if __name__ == "__main__":
    main()
