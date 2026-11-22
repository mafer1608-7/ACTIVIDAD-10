# Firmware del robot – cargar y probar

## 0. Si la placa es un ESP32-S3 (DevKitC-1)

- *Herramientas → Placa → esp32 → **ESP32S3 Dev Module***. El programa elige solo los pines del S3.
- Si el módulo dice **N16R8 / N8R8** (PSRAM octal), poner *PSRAM → OPI PSRAM*; si dice N8 o N8R2, *Disabled / QSPI*.
- La placa tiene 2 puertos USB-C: usar el marcado **UART** (o COM). Si usan el marcado **USB**, activar
  *USB CDC On Boot → Enabled* para ver el monitor serie.
- Para entrar en modo carga: mantener **BOOT**, pulsar **RST**, soltar ambos.

| Función | ESP32-S3 | ESP32 normal |
|---|---|---|
| L298N ENA / IN1 / IN2 | 4 / 5 / 6 | 25 / 26 / 27 |
| L298N ENB / IN3 / IN4 | 7 / 15 / 16 | 14 / 33 / 32 |
| HC-SR04 TRIG / ECHO | 17 / 18 | 19 / 18 |
| Magnetómetro SDA / SCL | 8 / 9 | 21 / 22 |
| Encoders izq. / der. | 10 / 11 | 34 / 35 |
| Divisor de batería | 1 | 36 |

## 1. Cargar el programa (Arduino IDE)

1. Instalar **Arduino IDE 2** (arduino.cc). El core ESP32 3.x ya está instalado en este PC.
2. Abrir `firmware/robot_esp32/robot_esp32.ino` (la pestaña `pagina_web.h` se abre sola).
3. *Herramientas → Placa → esp32 → **ESP32 Dev Module***. Elegir el puerto COM.
4. Subir. Si se queda en `Connecting....`, mantener presionado el botón **BOOT** del ESP32 hasta que empiece a cargar.
5. Abrir el Monitor Serie a **115200**: debe decir `Magnetometro: QMC5883L` (o `NO ENCONTRADO`) y `WiFi: ROBOT_MOVIL`.

No necesita librerías externas: todo viene en el core del ESP32.

## 2. Conectarse a la app

1. En el PC o el celular, conectarse a la red WiFi **ROBOT_MOVIL**, clave **robot1234**.
2. Abrir en el navegador **http://192.168.4.1**
3. Control: botones en pantalla o teclado **W A S D / flechas**; **Espacio** = parar.

Si se pierde la conexión más de 0,6 s, el robot se detiene solo.

## 3. Pruebas por etapas (en este orden)

| # | Prueba | Cómo | Resultado esperado |
|---|---|---|---|
| 1 | ESP32 + WiFi | Solo el ESP32 por USB | La página abre y dice "Conectado" |
| 2 | HC-SR04 | Conectarlo (con divisor en ECHO) | La distancia cambia al acercar la mano |
| 3 | Motores | **Robot levantado**, ruedas al aire, batería conectada | ▲ = las dos ruedas giran hacia adelante |
| 4 | Sentido de motores | Si una rueda gira al revés | Cambiar `INVERTIR_IZQ` / `INVERTIR_DER` a `true` (o invertir los cables en el L298N) |
| 5 | Giro | ▶ en la app | El robot gira a la **derecha** (horario visto desde arriba). Si gira a la izquierda, los motores están cruzados: intercambiar OUT1-2 con OUT3-4 |
| 6 | Magnetómetro | Conectarlo por I²C | La app muestra "QMC5883L" y los valores crudos cambian al moverlo |
| 7 | Calibración | Robot en el piso, lejos de metales → "Calibrar brújula" | Gira 20 s solo y dice "Calibracion guardada" |
| 8 | Sentido del rumbo | Girar el robot a la derecha con la mano | El rumbo **sube**. Si baja, poner `MAG_INVERTIR_Y = true` y volver a cargar |
| 9 | Norte | Orientar el robot al norte con la brújula del celular → "fijar 0°" | Luego, al apuntar al este debe marcar ~90° |
| 10 | Autónomo (base) | Botón "E" | El robot gira solo hasta ~90° y se detiene |
| 11 | Parada por obstáculo | Avanzar hacia una pared | Se detiene a 15 cm (aún puede girar o retroceder) |

**Graben un video de las pruebas 3, 7, 9, 10 y 11**: son la evidencia de las pruebas funcionales del informe.

## 4. Ajustes en el código (sección CONFIGURACION)

| Constante | Para qué |
|---|---|
| `PWM_MIN` | Si los motores zumban pero no arrancan a velocidad baja, subirlo (por ejemplo 130) |
| `INVERTIR_IZQ`, `INVERTIR_DER` | Sentido de cada motor |
| `MAG_INVERTIR_Y` | Si el rumbo va al revés |
| `DECLINACION` | Bogotá ≈ −8° (oeste). Verificar con la calculadora de declinación de NOAA |
| `DIST_PARADA_CM` | Distancia de parada por obstáculo |

## Problemas comunes

- **Rumbo que salta o no cambia:** el magnetómetro está muy cerca de los motores o de tornillos de acero.
  Súbanlo al mástil y usen tornillos de nylon. Recalibren después de mover algo.
- **El ESP32 se reinicia al arrancar los motores:** la batería está baja o falta el capacitor de 470 µF.
- **"NO ENCONTRADO" en el magnetómetro:** revisar SDA→21, SCL→22, VCC→3V3, GND.
- **Distancia siempre "fuera de rango":** ECHO sin divisor o con TRIG y ECHO intercambiados.
