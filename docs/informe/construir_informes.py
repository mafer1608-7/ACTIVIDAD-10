"""Genera los informes IEEE de la Entrega 1 y la Entrega 2 sobre la plantilla del curso."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ieee_lib import Informe  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
ROBOTO = os.path.dirname(os.path.dirname(AQUI))
LAB = os.path.dirname(ROBOTO)
PLANTILLA = os.path.join(LAB, "Plantilla IEEE-UMNG.docx")
FIG = os.path.join(AQUI, "fig")
SALIDA = os.path.join(ROBOTO, "informes")
os.makedirs(SALIDA, exist_ok=True)
F = lambda n: os.path.join(FIG, n)  # noqa: E731
CEN = WD_ALIGN_PARAGRAPH.CENTER
IZQ = WD_ALIGN_PARAGRAPH.LEFT

AUTORES = "Peñuela R. María Fernanda (7004788)"

REFS = [
    "J. G. Webster, *Measurement, Instrumentation, and Sensors Handbook*, 2nd ed. Boca Raton, FL, USA: CRC Press, 2014.",
    "J. Fraden, *Handbook of Modern Sensors: Physics, Designs, and Applications*, 5th ed. New York, NY, USA: Springer, 2016.",
    "S. Monk, *Programming ESP32 with Arduino IDE*. New York, NY, USA: McGraw-Hill Education, 2021.",
    "P. Ripka, *Magnetic Sensors and Magnetometers*. Boston, MA, USA: Artech House, 2001.",
    "R. Siegwart, I. R. Nourbakhsh, and D. Scaramuzza, *Introduction to Autonomous Mobile Robots*, 2nd ed. Cambridge, MA, USA: MIT Press, 2011.",
    "K. Ogata, *Modern Control Engineering*, 5th ed. Upper Saddle River, NJ, USA: Prentice Hall, 2010.",
    "InvenSense Inc., “MPU-6000 and MPU-6050 Product Specification,” Rev. 3.4, 2013.",
    "Espressif Systems, “ESP32-S3 Series Datasheet.” [En línea]. Disponible: https://www.espressif.com",
    "STMicroelectronics, “L298: Dual full-bridge driver,” hoja de datos.",
    "Elec Freaks, “HC-SR04 ultrasonic ranging module: user guide.”",
]


# ======================================================================= bloques compartidos
def sec_componentes(R):
    R.h2("Selección de componentes")
    R.p("La Tabla {} resume los componentes y el criterio de selección. Se descartó cualquier kit comercial: el "
        "chasis, los soportes y el mástil son piezas propias; los motores, el driver y los sensores son módulos "
        "discretos de venta común.".format(R.n_tab + 1))
    R.tabla("Componentes seleccionados.", [
        ["Componente", "Función", "Criterio de selección"],
        ["ESP32-S3 DevKitC-1 [8]", "Control, sensado, WiFi", "Doble núcleo, WiFi integrado, PWM (LEDC) e I²C por hardware, bajo costo"],
        ["L298N [9]", "Puente H doble", "Dos canales de 2 A, entradas de dirección y habilitación PWM; su regulador entrega 5 V"],
        ["2 motorreductores TT", "Tracción diferencial", "Par suficiente a 7,4 V, bajo costo, montaje sencillo"],
        ["HC-SR04 [10]", "Distancia frontal", "Rango típico 2–400 cm, interfaz digital TRIG/ECHO"],
        ["MPU6050 / GY-521 [7]", "Acelerómetro y giroscopio", "6 ejes por I²C (0x68), disponible en la tarjeta GY-521"],
        ["GY-273 (QMC5883L)", "Magnetómetro (previsto)", "3 ejes por I²C (0x0D); **no se pudo integrar** (ver Resultados)"],
        ["2×18650 (7,4 V)", "Alimentación", "Corriente suficiente para los motores; recargables"],
    ], [2.6, 2.3, 4.0], size=7.5)


def sec_mecanico(R, placas=True):
    R.h2("Diseño mecánico propio")
    R.p("El chasis es circular, de Ø180 mm, con dos placas paralelas de 3 mm separadas 40 mm por separadores M3 de "
        "latón (no magnéticos). Las ruedas de Ø65 mm van sobre soportes de motor impresos, con una distancia entre "
        "ruedas de 150 mm. El diseño prevé un apoyo trasero (patín impreso o rueda loca), que **no se montó** en el prototipo evaluado. Un mástil de 80 mm eleva el módulo de "
        "orientación para alejarlo de los motores [4]. El modelo es paramétrico (CadQuery, Python) y se exporta a "
        "STEP (compatible con SolidWorks), DXF (contorno de las placas) y STL (impresión 3D). Las piezas se "
        "fabricaron por impresión 3D. " + (
        "La Fig. {} muestra el ensamble y la Fig. {} el plano de las placas.".format(R.n_fig + 1, R.n_fig + 2) if placas
        else "La Fig. {} muestra el ensamble.".format(R.n_fig + 1)))
    R.figura(F("col_cad_iso.png"), 8.4, "Modelo CAD del ensamble (vista isométrica): placas, soportes de motor, "
             "ruedas, mástil de 80 mm y soporte del sensor ultrasónico.")
    if placas:
        R.figura(F("col_cad_placas.png"), 7.2, "Planos de las placas inferior y superior (DXF), con el frente en +X.")


def sec_electronico(R, entrega):
    R.h2("Diseño electrónico")
    R.p("La Fig. {} presenta el diagrama de bloques y las Figs. {} y {} el esquema de conexiones tal como se construyó. "
        "Las pilas alimentan el L298N (12 V) a través del interruptor; el regulador del L298N entrega 5 V al ESP32-S3 "
        "y al HC-SR04, y el MPU6050 se alimenta con los 3,3 V del ESP32-S3. Se retiraron los puentes ENA y ENB del "
        "L298N para controlar la velocidad por PWM (1 kHz, 8 bits). Todas las tierras se unen en un punto común.".format(
            R.n_fig + 1, R.n_fig + 2, R.n_fig + 3))
    R.figura(F("col_bloques.png"), 8.4, "Diagrama de bloques del sistema embebido. El magnetómetro figura en línea "
             "discontinua porque no se instaló.")
    R.figura(F("col_esq_motores.png"), 8.4, "Esquema de conexiones: ESP32-S3, driver L298N, motores y alimentación.")
    R.figura(F("col_esq_sensores.png"), 8.4, "Esquema de conexiones: HC-SR04 con divisor de tensión en ECHO y MPU6050 en el bus I²C.")
    R.p("El pin ECHO del HC-SR04 entrega 5 V y los GPIO del ESP32-S3 admiten 3,3 V, por lo que se usó un divisor de "
        "1 kΩ y 2 kΩ: V = 5·2/(1+2) = 3,33 V. El bus I²C (SDA = GPIO8, SCL = GPIO9) se comparte entre los módulos de "
        "orientación. La Tabla {} lista la asignación de pines.".format(R.n_tab + 1))
    R.tabla("Asignación de pines del ESP32-S3.", [
        ["Señal", "GPIO", "Señal", "GPIO"],
        ["ENA (PWM motor izq.)", "4", "TRIG (HC-SR04)", "17"],
        ["IN1 / IN2", "5 / 6", "ECHO (con divisor)", "18"],
        ["ENB (PWM motor der.)", "7", "SDA (I²C)", "8"],
        ["IN3 / IN4", "15 / 16", "SCL (I²C)", "9"],
    ], [3.0, 1.2, 3.2, 1.2], size=8, alinear=[IZQ, CEN, IZQ, CEN])


def sec_orientacion(R, completa=False):
    R.h2("Estimación de la orientación polar")
    R.p("La dirección del robot se expresa como un ángulo θ en grados, de 0° a 360°, medido en sentido horario desde "
        "el norte de referencia (coordenada polar). Con un magnetómetro calibrado, el rumbo sería [4]:")
    R.ecuacion("θ_{m} = atan2(B_{y} − o_{y}, B_{x} − o_{x}) + δ", 1)
    R.p("donde o_{x} y o_{y} son los desplazamientos de hierro duro obtenidos al girar el robot sobre sí mismo y δ es la "
        "declinación magnética local. El firmware incluye el controlador del QMC5883L/HMC5883L y la calibración por "
        "giro de 20 s, pero **no se pudo usar por falta de un magnetómetro operativo**: el escáner I²C no detectó "
        "ningún dispositivo con el GY-273 conectado.")
    R.p("Como alternativa se estimó el rumbo integrando la velocidad angular del giroscopio del MPU6050 [7], con el "
        "cero fijado manualmente (botón «fijar 0°») cuando el robot apunta al norte indicado por la brújula de un celular:")
    R.ecuacion("θ_{k} = (θ_{k−1} + s·(ω_{z} − ω_{0})·Δt) mod 360°", 2)
    R.p("con s = ±1 según el montaje del sensor y ω_{0} el sesgo medido al arrancar con el robot quieto. Si el MPU6050 "
        "no responde, el firmware integra la orden a los motores (Δθ = κ·(u_{I} − u_{D})·Δt, con κ = 1,5 °/s por 1 % de "
        "diferencia entre ruedas). En ambos casos **el rumbo es una estimación**: un sesgo residual de, por ejemplo, 0,1 °/s "
        "acumula 6° por minuto, y el cero depende de la exactitud con que se alineó el robot.")


def sec_software(R, entrega):
    R.h2("Firmware, comunicación inalámbrica y aplicación")
    R.p("Se eligió WiFi en modo punto de acceso: el ESP32-S3 crea la red «ROBOT_MOVIL» y sirve una página web en "
        "http://192.168.4.1, por lo que cualquier PC o celular con navegador funciona como aplicación, sin instalar "
        "nada. No se usó ESP-NOW (requiere un segundo ESP32) ni Bluetooth (requiere emparejar y una aplicación nativa). "
        "La comunicación es bidireccional: la página envía órdenes con peticiones HTTP y, cada 100 ms, consulta "
        "`/ctrl`, cuya respuesta es un JSON con el estado completo (rumbo, distancia, velocidades, modo, eventos y datos "
        "inerciales).")
    if entrega == 1:
        R.p("En modo manual se controla el robot con las teclas W, A, S, D o con botones; si la página deja de enviar "
            "órdenes durante 600 ms, los motores se detienen, y el robot no avanza si el HC-SR04 mide menos de 15 cm. "
            "La aplicación muestra el rumbo en una brújula polar y los valores de los sensores.")
    else:
        R.p("La aplicación permite elegir el modo (manual o autónomo), escribir el rumbo deseado o tocarlo sobre la "
            "brújula, la distancia y la velocidad, y muestra de forma continua el rumbo **actual** y el **deseado** "
            "(aguja y marca sobre la misma brújula, con el error en grados), la fase de la misión, el progreso en "
            "centímetros, los sensores, la bitácora de eventos y una gráfica de los últimos 30 s. Los datos se "
            "descargan como CSV cada 0,1 s para el análisis.")


# ======================================================================= ENTREGA 1
def entrega1():
    R = Informe(PLANTILLA)
    R.portada(
        "ROBOT MÓVIL DE COORDENADAS POLARES BASADO EN ESP32-S3: DISEÑO, SENSADO Y COMUNICACIÓN INALÁMBRICA (ENTREGA 1)",
        AUTORES,
        "Resumen—Se presenta la primera etapa de un robot móvil de diseño propio, sin kits comerciales, basado en el "
        "ESP32-S3. Se desarrolló un chasis en CAD paramétrico, fabricado por impresión 3D, y una electrónica con driver "
        "L298N, dos motorreductores, un sensor ultrasónico HC-SR04 y una unidad inercial MPU6050. El microcontrolador "
        "crea una red WiFi propia y sirve una aplicación web desde la que se controla el robot en modo manual y se "
        "visualiza su dirección polar en una brújula. El magnetómetro previsto no pudo integrarse, por lo que la "
        "orientación se estimó integrando el giroscopio desde un cero fijado manualmente; el informe analiza el "
        "efecto de esta limitación sobre la exactitud del rumbo y propone las mejoras necesarias.",
        "robot móvil, ESP32-S3, orientación polar, MPU6050, HC-SR04, WiFi, CAD.")

    R.h1("Introducción")
    R.p("Un robot móvil necesita conocer hacia dónde apunta para navegar. En robots de bajo costo, esa información "
        "proviene de sensores inerciales y magnéticos [1], [2]: el magnetómetro entrega una referencia absoluta "
        "respecto al campo terrestre, mientras que el giroscopio mide el cambio de orientación sin referencia "
        "absoluta [4]. La cinemática diferencial, con dos ruedas motrices independientes, permite girar sobre el "
        "propio eje y es la base de muchos robots de laboratorio [5]. El ESP32-S3 integra WiFi y periféricos "
        "suficientes para sensar, controlar los motores y servir una interfaz remota con un solo chip [3], [8].")
    R.p("Este informe documenta la primera entrega del proyecto: el diseño mecánico y electrónico propio del robot, "
        "la lectura de sensores de movimiento y de proximidad, el cálculo de la dirección polar, y su transmisión a "
        "una aplicación mediante WiFi. Se trabajó de forma incremental, verificando cada subsistema por separado.")
    R.p("Se declara desde el principio una limitación: **el magnetómetro no estuvo operativo**, de modo que la "
        "orientación respecto al norte magnético no se midió y se reemplazó por una estimación inercial. Las secciones "
        "siguientes describen el diseño, los resultados obtenidos y las consecuencias de esa limitación.")

    R.h1("Métodos y Materiales")
    R.h2("Requerimientos del sistema")
    R.tabla("Requerimientos funcionales y no funcionales.", [
        ["Id.", "Requerimiento"],
        ["RF1", "Controlar el movimiento del robot en modo manual desde un PC o celular."],
        ["RF2", "Calcular y mostrar la dirección polar del robot respecto a un norte de referencia."],
        ["RF3", "Medir la distancia a obstáculos frontales y detener el avance manual a menos de 15 cm."],
        ["RF4", "Comunicar el robot con la aplicación de forma inalámbrica y en tiempo real."],
        ["RNF1", "Diseño mecánico y electrónico propio, sin kits comerciales."],
        ["RNF2", "Alimentación autónoma con baterías; diámetro del chasis de 180 mm."],
    ], [1.2, 7.7], size=8)
    sec_componentes(R)
    sec_mecanico(R)
    sec_electronico(R, 1)
    sec_orientacion(R)
    sec_software(R, 1)
    R.h2("Protocolo de pruebas")
    R.p("Cada subsistema se probó antes de integrarlo: (i) motores con la página web desde el PC; (ii) HC-SR04, "
        "acercando la mano y comparando con una distancia conocida; (iii) MPU6050, verificando en reposo ≈ (0, 0, 1) g "
        "y velocidad angular ≈ 0; (iv) orientación, girando el robot hacia 0°, 90°, 180° y 270° con la brújula de un "
        "celular como referencia. Se corrigió el sentido de giro de los motores en el firmware tras observar que "
        "las teclas de giro y avance estaban intercambiadas.")

    R.h1("Resultados")
    R.h2("Cumplimiento de los resultados esperados")
    R.tabla("Estado de los resultados esperados de la Entrega 1.", [
        ["Resultado esperado", "Estado", "Evidencia"],
        ["Requerimientos del sistema", "Cumple", "Tabla 1"],
        ["Selección de componentes", "Cumple", "Tabla 2"],
        ["Diseño electrónico", "Cumple", "Figs. 3 a 5, Tabla 3"],
        ["Diseño mecánico propio (CAD)", "Cumple", "Figs. 1 y 2; STEP, DXF y STL"],
        ["Diagrama de bloques", "Cumple", "Fig. 3"],
        ["Datos inerciales", "Cumple", "MPU6050 leído en la app"],
        ["Datos magnéticos", "**No cumple**", "Magnetómetro no detectado"],
        ["Orientación polar", "**Parcial**", "Estimada con giroscopio; cero manual"],
        ["Comunicación inalámbrica", "Cumple", "WiFi AP + HTTP, 100 ms"],
        ["Visualización en la aplicación", "Cumple", "Brújula polar y sensores"],
    ], [3.8, 1.7, 3.4], size=8)
    R.h2("Mediciones")
    R.p("Con el robot en reposo y ligeramente inclinado, el acelerómetro marcó (−0,14; −0,23; 0,90) g; el módulo de la "
        "aceleración es ≈ 0,94 g, coherente con la gravedad. El HC-SR04 entregó lecturas estables (por ejemplo, 42,6 y "
"53,9 cm). La Tabla 5 resume los valores aproximados de orientación: al ordenar giros a ángulos conocidos y "
        "medir con la brújula de un celular, los errores fueron de 0° a 6°.")
    R.tabla("Rumbo ordenado frente a rumbo real medido con el celular (valores aproximados).", [
        ["Ordenado", "Real (celular)", "Error"],
        ["0°", "3°", "+3°"],
        ["90°", "90°", "0°"],
        ["180°", "186°", "+6°"],
        ["270°", "276°", "+6°"],
    ], [2.6, 2.6, 2.6], size=8, alinear=[CEN, CEN, CEN])
    R.h2("Análisis de resultados")
    R.p("**Orientación.** Sin magnetómetro no existe una referencia absoluta: el rumbo mostrado es una integral que "
        "arranca en el cero fijado a mano, por lo que hereda dos errores. El primero es el error de alineación inicial: "
        "la brújula de un celular es poco exacta y sensible a metales cercanos. El segundo es la deriva del giroscopio, "
        "que crece con el tiempo. En las pruebas, el rumbo mostrado por la aplicación no coincidió bien con el del "
        "celular al girar el robot a ángulos conocidos.")
    R.p("**Problemas encontrados y causas.**")
    R.lista([
        "*Magnetómetro sin respuesta.* El escáner I²C no encontró ningún dispositivo con el GY-273 conectado, ni "
        "intercambiando SDA y SCL ni probando otros pines. Se atribuye a un módulo defectuoso o a un contacto "
        "deficiente; no se pudo reemplazar a tiempo.",
        "*Sentido de giro invertido.* El motor derecho estaba cableado con polaridad inversa y, después, los canales "
        "izquierdo y derecho estaban cruzados. Se corrigió en el firmware (INVERTIR_DER e INTERCAMBIAR_LADOS).",
        "*Bus I²C.* El MPU6050 no se detectó hasta corregir el contacto de SDA y SCL; la lectura de SDA/SCL en alto "
        "no demuestra continuidad, y para detectar el fallo se usó una prueba con resistencia de pull-down.",
        "*Alimentación.* Con las pilas descargadas, los motores pierden fuerza y el giro cambia, lo que afecta el "
        "comportamiento del robot y la calibración.",
        "*Apoyo trasero no montado.* El prototipo se evaluó sin el patín o la rueda loca prevista en el diseño, lo "
        "que probablemente afectó la estabilidad del chasis y la repetibilidad de los giros (hipótesis, no medida).",
    ])
    R.p("**Mejoras propuestas.** Instalar y calibrar un magnetómetro (QMC5883L o HMC5883L) en el mástil, con "
        "tornillería no magnética; fusionarlo con el giroscopio mediante un filtro complementario para corregir la "
        "deriva; añadir un sensor de ángulo de giro por encoders; y medir y registrar la latencia de la comunicación.")

    R.h1("Respuestas a las preguntas de discusión")
    pregs = [
        "**Criterios de selección.** El ESP32-S3 integra WiFi, doble núcleo, PWM e I²C por hardware y tiene bajo costo; "
        "el HC-SR04 es barato y de interfaz digital simple; el MPU6050 y el QMC5883L comparten el bus I²C.",
        "**Influencia del diseño mecánico.** El mástil de 80 mm y los separadores de latón buscan alejar el sensor de los "
        "motores y de piezas ferromagnéticas, y la placa plana mantiene vertical el eje Z del giroscopio.",
        "**Calibración del magnetómetro.** El firmware la implementa (giro de 20 s; mínimos y máximos por eje dan los "
        "desplazamientos y la escala), pero **no se aplicó** porque no hubo sensor operativo.",
        "**Fuentes de error.** Sesgo y deriva del giroscopio, error del cero manual y, con magnetómetro, hierro duro y "
        "blando, inclinación y declinación local. Se evidenciaron como diferencias entre el rumbo de la app y el del celular.",
        "**Medio inalámbrico.** WiFi AP no requiere infraestructura ni aplicación nativa y permite varias pantallas; "
        "limita el alcance y la latencia (consulta cada 100 ms). ESP-NOW tendría menos latencia pero exige otro ESP32.",
        "**Sincronización.** El lazo principal lee los sensores y el servidor responde con el último estado, con una marca "
        "de tiempo en cada paquete.",
        "**Interferencias electromagnéticas.** Los motores DC y los cables de potencia perturban el magnetómetro; "
        "se mitigan con el mástil y con cables trenzados. No se midió por falta del sensor.",
        "**Aporte del diseño electrónico.** Se separó la potencia (batería → L298N) de la lógica, se usó un divisor en "
        "ECHO y se unieron las tierras. Una batería baja degrada el funcionamiento, como se observó.",
        "**Validación experimental.** Comparando el rumbo mostrado con el de la brújula de un celular a 0°, 90°, 180° y "
        "270° (Tabla 5). El resultado mostró que la estimación no era suficientemente exacta.",
        "**Mejoras de precisión.** Magnetómetro calibrado, fusión con el giroscopio, filtrado de las lecturas y "
        "calibración de la declinación.",
        "**Limitaciones para navegación autónoma.** Sin referencia absoluta el rumbo deriva, la distancia se estima "
        "por tiempo y solo hay un sensor frontal de obstáculos.",
        "**Diseño propio.** El chasis, los soportes y el mástil se modelaron en CAD paramétrico y se imprimieron; se "
        "entregan los archivos STEP, DXF y STL y el script que los genera.",
    ]
    for i, t in enumerate(pregs, 1):
        R.p(f"{i}. {t}", size=9.5)

    R.h1("Conclusiones")
    R.lista([
        "Se diseñó y construyó un robot móvil propio, con CAD paramétrico, electrónica documentada y firmware que "
        "integra motores, sensor de proximidad e IMU, comunicado por WiFi con una aplicación web.",
        "El control manual y la medición de distancia funcionaron correctamente; la dirección polar se visualiza en la "
        "aplicación, pero se obtuvo por estimación inercial y no con magnetómetro.",
        "Esa limitación impide garantizar el cero respecto al norte y hace derivar el rumbo; es la mejora prioritaria "
        "para la siguiente entrega, junto con la calibración del magnetómetro y su fusión con el giroscopio.",
        "Verificar cada módulo por separado (escáner I²C, pruebas de motores y de sensores) permitió aislar fallos "
        "de cableado y de polaridad con rapidez.",
    ], size=10)
    R.referencias(REFS)
    R.guardar(os.path.join(SALIDA, "Informe_Entrega1_IEEE.docx"))


# ======================================================================= ENTREGA 2
def entrega2():
    R = Informe(PLANTILLA)
    R.portada(
        "NAVEGACIÓN POR RUMBO Y EVASIÓN DE OBSTÁCULOS EN UN ROBOT MÓVIL DE COORDENADAS POLARES CON ESP32-S3 (ENTREGA 2)",
        AUTORES,
        "Resumen—Se presenta la segunda etapa de un robot móvil de diseño propio basado en ESP32-S3: un modo de "
        "navegación autónoma que recorre una distancia dada manteniendo un rumbo, en grados respecto al norte "
        "configurado, y evade obstáculos con un sensor ultrasónico retomando después el rumbo objetivo. La aplicación "
        "web muestra de forma continua el rumbo actual y el deseado y se comunica de forma bidireccional por WiFi. "
        "El magnetómetro no estuvo disponible, por lo que el rumbo se estimó con el giroscopio del MPU6050 desde un "
        "cero fijado manualmente. El robot avanzó las distancias pedidas y esquivó los obstáculos en 15 de 20 "
        "intentos, pero no giró con exactitud a los ángulos pedidos y no ubicó bien el cero; el informe analiza las causas.",
        "navegación autónoma, evasión de obstáculos, control de rumbo, ESP32-S3, MPU6050, WiFi.")

    R.h1("Introducción")
    R.p("La navegación autónoma de un robot de tracción diferencial requiere un lazo de control que compare la "
        "orientación deseada con la medida y corrija la diferencia de velocidad entre ruedas [5], [6]. Además, la "
        "presencia de obstáculos obliga a combinar el seguimiento de una dirección con maniobras reactivas basadas "
        "en sensores de proximidad [5]. Un control proporcional sobre el error angular es una solución simple y "
        "robusta para robots de laboratorio [6].")
    R.p("Esta entrega parte del robot descrito en la Entrega 1 (mecánica, electrónica, WiFi y aplicación) y añade: "
        "el modo autónomo con rumbo y distancia configurables a distancia, la evasión de obstáculos con retorno al "
        "rumbo objetivo, y una aplicación que muestra la dirección polar actual y la deseada de forma continua y "
        "registra los eventos y los datos para su análisis.")
    R.p("**El magnetómetro no estuvo operativo**, así que el rumbo es una estimación inercial con cero manual. Esto "
        "condiciona la exactitud de los giros y se analiza en la sección de resultados.")

    R.h1("Métodos y Materiales")
    R.h2("Plataforma")
    R.p("Se mantiene la plataforma de la Entrega 1. La Fig. 1 muestra el diseño CAD, la Fig. 2 el diagrama de bloques "
        "y las Figs. 3 y 4 el esquema de conexiones; el diseño mecánico (chasis circular de Ø180 mm, ruedas de Ø65 mm, "
        "distancia entre ruedas de 150 mm y mástil de 80 mm) se detalla en el informe anterior.")
    sec_mecanico(R, placas=False)
    sec_electronico(R, 2)
    sec_orientacion(R)
    R.h2("Algoritmo de navegación")
    R.p("Las órdenes llegan por la aplicación (rumbo θ_{d}, distancia d y velocidad v). El error angular se calcula en "
        "el intervalo [−180°, 180°) para girar siempre por el lado más corto:")
    R.ecuacion("e = ((θ_{d} − θ + 540°) mod 360°) − 180°", 3)
    R.p("La misión es una máquina de estados (Fig. {}). En ALINEAR el robot gira en el sitio con una orden proporcional "
        "saturada entre 28 % y 55 % (en valor absoluto):".format(R.n_fig + 1))
    R.ecuacion("u_{I} = −u_{D} = sat(K_{g}·e)", 4)
    R.p("hasta que |e| < 6° durante 0,4 s. En AVANZAR se mantiene el rumbo con una corrección proporcional entre ruedas, "
        "saturada a ±30 %:")
    R.ecuacion("c = sat(K_{r}·e);   u_{I} = v + c;   u_{D} = v − c", 5)
    R.p("y si |e| supera 40° el robot se detiene y vuelve a girar en el sitio. La distancia recorrida se calcula por "
        "tiempo (no se instalaron encoders): el avance se acumula solo cuando ambas ruedas van hacia adelante, a una "
        "velocidad en cm/s calibrada con una prueba de 3 s medida con cinta. Solo cuenta el avance sobre el rumbo "
        "objetivo; los pasos laterales de la evasión no se suman.")
    R.figura(F("col_flujo.png"), 8.4, "Diagrama de estados de la misión autónoma, con la evasión de obstáculos.")
    R.h2("Evasión de obstáculos y retorno al rumbo")
    R.p("Si el HC-SR04 mide 25 cm o menos en dos lecturas consecutivas, el robot se detiene (EV_GIRO) y gira 90° respecto "
        "al rumbo objetivo; avanza 35 cm de lado (EV_LADO); vuelve a girar al rumbo objetivo (EV_VOLVER) y espera "
        "0,35 s para comprobar si el obstáculo sigue (EV_REVISAR). Si sigue, da otro paso lateral; si el lado está "
        "bloqueado, alterna el lado; se permiten hasta 6 intentos. Si está libre, retoma AVANZAR. Al terminar, el robot conserva el rumbo configurado pero queda "
        "desplazado lateralmente respecto a la línea original. La Tabla {} reúne los parámetros del controlador.".format(R.n_tab + 1))
    R.tabla("Parámetros del algoritmo (firmware).", [
        ["Parámetro", "Valor"],
        ["K_{g} (giro en el sitio)", "0,7 % por grado"],
        ["Orden de giro mín. / máx.", "28 % / 55 %"],
        ["Tolerancia de alineación", "6°"],
        ["K_{r} (mantener rumbo)", "0,9 % por grado"],
        ["Corrección máxima c", "30 %"],
        ["Error de realineación", "40°"],
        ["Distancia de evasión", "25 cm"],
        ["Paso lateral / intentos", "35 cm / 6"],
        ["PWM: frecuencia, resolución, mínimo", "1 kHz, 8 bits, 110/255"],
    ], [5.2, 3.7], size=8, alinear=[IZQ, CEN])
    sec_software(R, 2)
    R.h2("Protocolo experimental")
    R.p("Las pruebas se hicieron sobre piso plano. (1) Modo manual: recorrido con las teclas. (2) Misión recta: rumbo "
        "y distancia configurados desde la aplicación, observando el avance y el rumbo final. (3) Evasión: una caja "
        "colocada sobre la ruta. (4) Giro al rumbo: orden «solo girar» a ángulos conocidos, midiendo el ángulo real "
        "con la brújula de un celular. Los datos se registraron en el CSV de la aplicación.")

    R.h1("Resultados")
    R.h2("Cumplimiento de los resultados esperados")
    R.tabla("Estado de los resultados esperados de la Entrega 2.", [
        ["Resultado esperado", "Estado", "Observación"],
        ["Navegación manual", "Cumple", "Teclas desde la app"],
        ["Navegación autónoma (rumbo + distancia)", "**Parcial**", "Distancia correcta; rumbo impreciso"],
        ["Configuración remota del rumbo", "Cumple", "Número o clic en la brújula"],
        ["Detección y evasión de obstáculos", "**Parcial**", "Exitosa en 15 de 20 intentos"],
        ["Retorno al rumbo tras evadir", "**Parcial**", "Depende de la estimación del rumbo"],
        ["Visualización de rumbo actual y deseado", "Cumple", "Brújula y gráfica"],
        ["Comunicación bidireccional", "Cumple", "WiFi AP, HTTP cada 100 ms"],
        ["Control de velocidad y giro", "**Parcial**", "Giros imprecisos a ángulos pedidos"],
        ["Uso del magnetómetro", "**No cumple**", "No se instaló"],
    ], [4.2, 1.7, 3.0], size=8)
    R.h2("Resultados experimentales")
    R.p("**Distancia.** El robot recorrió correctamente la distancia solicitada. En una misión de 100 cm avanzó "
        "aproximadamente 102 cm, un error de +2 cm (Tabla {}; valor aproximado registrado durante las pruebas).".format(R.n_tab + 1))
    R.tabla("Distancia recorrida en misión recta (valores aproximados).", [
        ["Pedida (cm)", "Medida (cm)", "Error (cm)"],
        ["100", "102", "+2"],
    ], [2.6, 2.6, 2.6], size=8, alinear=[CEN, CEN, CEN])
    R.p("**Evasión.** En 15 de 20 intentos (75 %) el robot detectó la caja, la esquivó y siguió avanzando; en los 5 "
        "restantes no completó la maniobra.")
    R.p("**Rumbo.** La Tabla {} resume los valores aproximados registrados al ordenar giros a ángulos conocidos y "
        "medir con la brújula de un celular: los errores fueron de 0° a 6°. Aun así, el robot **no se detenía de forma "
        "consistente en el ángulo pedido** y el cero de referencia no coincidía con el norte indicado por el "
        "celular.".format(R.n_tab + 1))
    R.tabla("Rumbo ordenado frente a rumbo real medido con el celular (valores aproximados).", [
        ["Ordenado", "Real (celular)", "Error"],
        ["0°", "3°", "+3°"],
        ["90°", "90°", "0°"],
        ["180°", "186°", "+6°"],
        ["270°", "276°", "+6°"],
    ], [2.6, 2.6, 2.6], size=8, alinear=[CEN, CEN, CEN])
    R.h2("Análisis de resultados")
    R.p("La distancia funcionó y la evasión tuvo éxito en 15 de 20 intentos porque no dependen de la exactitud del rumbo absoluto: la distancia se "
        "calcula por tiempo con una velocidad calibrada y la evasión se basa en el sensor ultrasónico. En cambio, "
        "los fallos de giro y del cero tienen una causa común: **el rumbo es una estimación sin referencia absoluta**.")
    R.lista([
        "*Cero mal ubicado.* El norte lo fija el operario al pulsar «fijar 0°» con ayuda de la brújula de un celular, "
        "de exactitud limitada y sensible a metales; cualquier error se transfiere a todo el rumbo posterior.",
        "*Error acumulativo.* La integral del giroscopio acumula el sesgo residual (p. ej., 0,1 °/s equivale a 6° por "
        "minuto); sin magnetómetro no hay corrección.",
        "*Giros imprecisos.* Si falla el giroscopio, el firmware estima el giro con una constante κ que supone "
        "una velocidad angular fija por cada 1 % de diferencia entre ruedas. En la práctica depende de la tensión de "
        "la batería, de la fricción del piso y de la zona muerta del PWM, por lo que el ángulo real difiere.",
        "*Ganancias no ajustadas.* K_{g} y K_{r} se definieron de forma teórica; faltó un ajuste con mediciones reales de "
        "sobreimpulso y tiempo de asentamiento [6].",
        "*Alimentación.* Con las pilas descargadas, la velocidad y el par cambian, lo que altera giros y distancia.",
        "*Apoyo trasero no montado.* El prototipo se evaluó sin el patín o la rueda loca prevista en el diseño; "
        "es probable que esto haya afectado la estabilidad y el deslizamiento del chasis durante los giros, y con ello "
        "la repetibilidad del ángulo real y el retorno al rumbo tras evadir (hipótesis, no medida).",
        "*Fallos de evasión.* Los 5 intentos no exitosos pueden relacionarse con "
        "la dependencia del retorno al rumbo respecto al rumbo estimado y con un único sensor frontal (hipótesis).",
    ])
    R.p("**Mejoras propuestas.** Instalar y calibrar un magnetómetro en el mástil y fusionarlo con el giroscopio "
        "(filtro complementario) para obtener un cero real y eliminar la deriva; añadir encoders para medir distancia "
        "y velocidad de las ruedas; ajustar K_{g} y K_{r} (o pasar a un PID) con las mediciones de la Tabla 5; y "
        "añadir más sensores de proximidad (laterales o un sensor orientable) para entornos con varios obstáculos.")

    R.h1("Respuestas a las preguntas de discusión")
    pregs = [
        "**Dirección deseada.** Es un ángulo θ_{d} en grados, de 0° a 360°, en sentido horario desde el norte de referencia, "
        "introducido en la app. Se compara con el rumbo actual mediante e = ((θ_{d} − θ + 540°) mod 360°) − 180°.",
        "**Manual y autónomo.** En manual el operador cierra el lazo con las teclas y el robot se detiene si pierde la "
        "comunicación 600 ms; en autónomo el robot alinea, avanza con control proporcional y evade solo.",
        "**Precisión del magnetómetro.** No se usó. Su ausencia impuso un rumbo estimado, cuya exactitud depende del "
        "giroscopio y del cero manual.",
        "**Estrategia de evasión.** Detenerse, girar 90° respecto al rumbo objetivo, avanzar 35 cm de lado, volver al rumbo "
        "y comprobar. Desplaza lateralmente el robot respecto a la línea original.",
        "**Retomar la dirección.** El estado EV_VOLVER gira de nuevo al rumbo objetivo y EV_REVISAR confirma 0,35 s que "
        "el camino está libre. La precisión del retorno es la del rumbo estimado.",
        "**Latencia.** La página consulta el estado cada 100 ms, por lo que la visualización se actualiza con un retardo "
        "de ese orden más el de la red; la latencia no se midió con instrumentos. El paro por inactividad ocurre a los 600 ms.",
        "**Velocidad y giro.** El PWM mínimo (110/255) vence la fricción de los motores; el giro en el sitio usa 28–55 % "
        "proporcional al error; el avance usa 35–90 % (60 % por defecto) con una corrección máxima de 30 %.",
        "**Validación de la distancia.** Con una prueba de 3 s se calibró el avance en cm/s y se verificó con una cinta "
        "métrica en una misión de 100 cm, donde avanzó aproximadamente 102 cm (Tabla 4).",
        "**Información en la app.** Rumbo actual, deseado y error, modo y fase, progreso, distancia, datos inerciales, "
        "bitácora de eventos y gráfica; permite entender el estado y diagnosticar fallos.",
        "**Limitaciones del algoritmo.** Rumbo estimado con deriva, distancia por tiempo, un solo sensor frontal y "
        "desplazamiento lateral tras evadir.",
        "**Robustez con varios obstáculos.** Más sensores (laterales o un sensor orientable), un mapa local y un "
        "controlador PID con encoders.",
        "**Calidad mecánica.** La rigidez, la distancia entre ruedas y el apoyo trasero determinan el deslizamiento y "
        "la repetibilidad de los giros. En el prototipo no se montó el apoyo trasero, lo que probablemente empeoró la "
        "estabilidad; las piezas impresas y la tracción irregular también afectan el ángulo real.",
        "**Escalabilidad con ESP32.** Odometría con encoders, uso de los dos núcleos, varios robots por ESP-NOW y "
        "fusión de sensores.",
        "**Aprendizajes.** Verificar cada sensor por separado, calibrar antes de controlar, registrar datos para el "
        "análisis y documentar el diseño; y que un sensor de referencia absoluta es crítico.",
    ]
    for i, t in enumerate(pregs, 1):
        R.p(f"{i}. {t}", size=9.5)

    R.h1("Conclusiones")
    R.lista([
        "Se implementaron los modos manual y autónomo, con configuración remota del rumbo y la distancia, evasión de "
        "obstáculos y una aplicación bidireccional que muestra el rumbo actual y el deseado.",
        "El robot avanzó las distancias pedidas y esquivó los obstáculos en 15 de 20 intentos (75 %), pero no giró "
        "con exactitud a los ángulos pedidos ni ubicó bien el cero, porque no se contó con magnetómetro y el rumbo fue una estimación.",
        "La integración del magnetómetro y su fusión con el giroscopio es la mejora principal; sin una referencia "
        "absoluta, el seguimiento de una dirección respecto al norte no es confiable.",
        "El diseño mecánico y electrónico propio, documentado con CAD y esquemas, permitió depurar fallos y sentar "
        "las bases para escalar el sistema.",
    ], size=10)
    R.referencias(REFS)
    R.guardar(os.path.join(SALIDA, "Informe_Entrega2_IEEE.docx"))


if __name__ == "__main__":
    entrega1()
    entrega2()
    print("Informes en", SALIDA, os.listdir(SALIDA))








