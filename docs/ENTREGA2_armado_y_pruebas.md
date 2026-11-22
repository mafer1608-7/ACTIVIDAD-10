# Robot móvil – Armado final y pruebas (Entregas 1 y 2)

Programa: `firmware/robot_completo/` (`robot_completo.ino` + `pagina_web.h`, en la misma carpeta).
Placa en Arduino IDE: **ESP32S3 Dev Module**. Conexiones: `docs/diagrama_conexiones_s3.png`.

## 1. Conexiones completas (todo apagado y sin batería)

| Módulo | Pin del módulo | ESP32-S3 |
|---|---|---|
| **L298N** | ENA (sin jumper) | GPIO 4 |
| | IN1 / IN2 | GPIO 5 / GPIO 6 |
| | ENB (sin jumper) | GPIO 7 |
| | IN3 / IN4 | GPIO 15 / GPIO 16 |
| | 5V (borne azul) | 5V |
| | GND (borne azul del medio) | GND |
| **HC-SR04** | VCC / GND | 5V / GND |
| | TRIG | GPIO 17 |
| | ECHO | 1 kΩ → GPIO 18, y desde GPIO 18 una de 2 kΩ a GND |
| **GY-273** (magnetómetro) | VCC / GND | **3V3** / GND |
| | SDA / SCL | GPIO 8 / GPIO 9 |
| **GY-521** (MPU6050, opcional) | VCC / GND | 3V3 / GND |
| | SDA / SCL | GPIO 8 / GPIO 9 (el mismo bus) |
| **H206 ×2** (encoders, opcionales) | VCC / GND | 3V3 / GND |
| | D0 izquierdo / derecho | GPIO 10 / GPIO 11 |

Los sensores I²C comparten los mismos 2 cables (SDA y SCL): se conectan en paralelo.
Los motores siguen en OUT1-OUT2 (izquierdo) y OUT3-OUT4 (derecho).

## 2. Orden de armado: un sensor a la vez
Después de cada etapa, abran la página y comprueben el resultado antes de seguir.

| Etapa | Qué conectar | Qué debe verse en la página (192.168.4.1) |
|---|---|---|
| 1 | Cargar `robot_completo`; solo motores | "Conectado"; ▲ ▼ ◀ ▶ funcionan como antes |
| 2 | HC-SR04 | "Distancia frontal" cambia al acercar la mano; a menos de 15 cm el robot no avanza en manual |
| 3 | GY-273 (módulo suelto, sobre la mesa) | "Magnetómetro: QMC5883L" y los valores de campo cambian al girar el módulo |
| 4 | GY-521 (si lo tienen) | "Acelerómetro" muestra ≈ 0 / 0 / 1 g con el robot quieto; "Giroscopio" ≈ 0 |
| 5 | H206 (si los tienen) | "RPM" sube al mover las ruedas |
| 6 | Pasar el GY-273 (y el GY-521) al mástil | Se repite la etapa 3 y 4 |

Los cables del mástil: **SDA con GND trenzados, SCL con 3V3 trenzados**, lejos de los cables de los motores.
Tornillos del mástil en **nylon**, nunca de acero. La flecha X del módulo apunta al frente.

Si no conectan el MPU6050 o los H206, el programa funciona igual: usa solo el magnetómetro y mide la
distancia por tiempo.

## 3. Calibración (se hace una vez, y cada vez que se mueva algo de sitio)
1. Robot en el piso, con espacio libre, **lejos de metales, del PC y del celular**.
2. Botón **"1. Calibrar brújula"**: el robot gira solo 20 s en el sitio.
   - El programa detecta solo el sentido del magnetómetro y del giroscopio.
   - Si el robot gira a la **izquierda**, los motores están cruzados: intercambien OUT1-OUT2 con OUT3-OUT4.
3. Pongan el robot mirando al **norte** (con la brújula del celular) y pulsen **"2. fijar 0°"**.
4. Verifiquen con la mano: giren el robot a la derecha. El **rumbo debe subir**. Si baja, pulsen **"Invertir sentido"**.
5. Apunten el robot al este, sur y oeste (con el celular) y comprueben ≈ 90°, 180° y 270°.

**Distancia (si no tienen encoders):** botón **"Prueba de distancia"**, el robot avanza 3 s. Midan con cinta
cuántos cm recorrió, escríbanlo y pulsen **Guardar**. Con encoders, ese mismo botón corrige el factor.

## 4. Modo autónomo
1. Elijan el **rumbo** (número o tocando la brújula), la **distancia** y la velocidad.
2. **▶ Iniciar misión**. Fases: *Alineando* → *Avanzando* → (si hay obstáculo) *Evasión* → *Avanzando* → meta.
3. Mover el robot con los botones o pulsar **■** cancela la misión en cualquier momento.

**Evasión de obstáculos:** a menos de 25 cm, el robot se detiene, gira 90° y avanza 35 cm de lado.
Luego **vuelve a girar al rumbo objetivo** y revisa si ya está libre. Si no, repite hasta 6 veces.
La distancia se cuenta **sobre el rumbo objetivo**: los pasos laterales no suman.
Al terminar, el robot sigue en el rumbo configurado, pero desplazado hacia un lado de la línea original.

## 5. Pruebas para el informe (grábenlas y descarguen el CSV)
El botón **"Descargar CSV"** guarda rumbo, objetivo, error, distancia, velocidades y sensores inerciales cada 0,1 s.

| # | Prueba | Cómo | Dato a anotar |
|---|---|---|---|
| 1 | Modo manual | Recorrer un cuadrado de 1 m con las teclas | Video |
| 2 | Lectura de sensores | Captura de pantalla con todos los sensores | Imagen |
| 3 | Precisión de la brújula | Apuntar a 0°, 45°, 90°… 315° con el celular de referencia, 3 veces | Tabla: rumbo real vs rumbo del robot, error medio |
| 4 | Seguimiento de rumbo | Misión a 90°, 200 cm, 5 veces | Tabla: rumbo final y desviación; gráfica del CSV (rumbo vs deseado) |
| 5 | Distancia | Misión de 100 cm, 5 veces, medir con cinta | Tabla: cm reales, error medio y desviación |
| 6 | Evasión | Caja de 30 × 30 cm en la ruta, 5 veces | Éxito/fallo, rumbo final, eventos de la app |
| 7 | Latencia | Pulsar ■ y medir con el video el tiempo hasta que frena | Tiempo en ms (video a 30 fps) |
| 8 | Alcance WiFi | Alejarse con el PC hasta perder conexión | Metros |
| 9 | Giro a rumbo | "Solo girar al rumbo" a 0°, 90°, 180°, 270° | Error final |

Con esto se contestan las preguntas 1 a 12 de la sección 15 de la guía.

## 6. Ajustes (sección CONFIGURACION del `.ino`)

| Constante | Cuándo cambiarla |
|---|---|
| `INVERTIR_IZQ`, `INVERTIR_DER` | Un motor gira al revés |
| `PWM_MIN` | Los motores zumban sin arrancar a velocidad baja (probar 130) |
| `KP_GIRO`, `GIRO_MIN`, `GIRO_MAX` | El giro en el sitio se pasa del rumbo o oscila: bajar `KP_GIRO` o `GIRO_MAX` |
| `KP_RUMBO` | Avanza en zigzag: bajarlo. Se desvía sin corregir: subirlo |
| `TOL_GIRO` | Tolerancia del giro (grados) |
| `DIST_EVASION_CM` | Distancia a la que empieza a evadir |
| `PASO_LATERAL_CM` | Si el obstáculo es más ancho que el paso lateral |
| `DECLINACION` | Bogotá ≈ −8° |

## 7. Problemas comunes

| Problema | Causa probable |
|---|---|
| "No encontrado" en el magnetómetro | SDA/SCL cruzados o VCC mal; probar 3V3 |
| El rumbo salta o no cambia al girar | Metal o motores cerca del magnetómetro; subirlo al mástil; recalibrar |
| La misión "Abortada: no logra alinearse" | Calibración mala o sentido invertido (ver 3.4) |
| El robot da vueltas sin parar al alinear | Sentido de la brújula invertido: botón "Invertir sentido" |
| La evasión se activa sola | ECHO sin divisor, o un cable suelto: la distancia salta |
| "Sin encoders: distancia por tiempo" | Normal si no hay H206; calibren con la prueba de distancia |
| El ESP32 se reinicia al arrancar los motores | Batería baja o falta el capacitor de 470 µF |
