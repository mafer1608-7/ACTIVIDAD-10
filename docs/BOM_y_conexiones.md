# Lista de materiales y conexiones – Robot móvil (Guía 5)

> Precios **aproximados en pesos colombianos (COP)**, de referencia para Bogotá a finales de 2026.
> Varían ±20 % según la tienda. Confírmenlos en tiendas de electrónica o en MercadoLibre antes de comprar.

## 1. Lista de materiales (BOM)

### Electrónica

| # | Componente | Cant. | Precio unit. | Subtotal | Justificación |
|---|---|---|---|---|---|
| 1 | ESP32 DevKit V1 (WROOM-32, 30 pines) | 1 | 32.000 | 32.000 | WiFi + BT integrados, 2 núcleos, ADC, PWM por hardware |
| 2 | Driver L298N | 1 | 15.000 | 15.000 | Fácil de conseguir, 2 A/canal; trae regulador de 5 V que alimenta el ESP32 (cae ~2 V en los motores) |
| 3 | Motorreductor TT 1:48 **doble eje** | 2 | 8.000 | 16.000 | Doble eje: un lado para la rueda y el otro para el disco del encoder |
| 4 | Rueda 65 mm para motor TT | 2 | 5.000 | 10.000 | Compatible con el eje TT |
| 5 | Rueda loca de bola metálica | 1 | 8.000 | 8.000 | Tercer punto de apoyo, sin fricción direccional |
| 6 | Sensor de ranura H206 + disco de 20 ranuras | 2 | 6.000 | 12.000 | Odometría, base del modo autónomo |
| 7a | MPU6050 (GY-521), acelerómetro + giroscopio | 1 | 12.000 | 12.000 | Opción económica |
| 7b | QMC5883L (GY-273), magnetómetro | 1 | 14.000 | 14.000 | Opción económica, rumbo respecto al norte |
| 8 | Sensor ultrasónico HC-SR04 | 1 | 7.000 | 7.000 | Proximidad frontal (2–400 cm) |
| 9 | Batería 18650 Li-ion (**real**, ≥2000 mAh) | 2 | 20.000 | 40.000 | 7,4 V; mucho mejor que pilas de 9 V |
| 10 | Portapilas 2×18650 | 1 | 4.000 | 4.000 | |
| 11 | BMS 2S (protección Li-ion) | 1 | 10.000 | 10.000 | Protege contra sobredescarga y corto |
| 12 | Cargador externo para 18650 (doble) | 1 | 25.000 | 25.000 | Omitir si ya tienen uno |
| 13 | Regulador buck LM2596 (opcional) | 0 | 10.000 | 0 | No hace falta: se usa la salida de 5 V del L298N |
| 14 | Interruptor basculante KCD1 | 1 | 2.000 | 2.000 | Va en el hueco de la placa superior |
| 15 | Portafusible + fusible 3 A | 1 | 4.000 | 4.000 | Protección ante cortos |
| 16 | Resistencias (10 k, 3,3 k, 1 k, 2 k) + capacitores (470 µF/16 V, 100 nF) | 1 kit | 4.000 | 4.000 | Divisores y filtrado |
| 17 | Placa perforada 7×9 cm + espadines hembra + borneras | 1 | 12.000 | 12.000 | El ESP32 y los módulos van en zócalo, no soldados |
| 18 | Cables Dupont + cable calibre 22 + termoencogible | 1 | 12.000 | 12.000 | |

### Mecánica

| # | Componente | Cant. | Precio | Subtotal | Notas |
|---|---|---|---|---|---|
| 19 | Corte láser de 2 placas en acrílico de 3 mm (Ø180 mm) | 1 | 30.000 | 30.000 | Archivos en `cad/DXF/` |
| 20 | Impresión 3D (~120 g de PETG/PLA) | 1 | 50.000 | 50.000 | Unos 10.000 si tienen impresora propia |
| 21 | 4 separadores de **latón** M3×40 + tornillería M3 + tornillos de nylon | 1 | 20.000 | 20.000 | Latón y nylon no afectan al magnetómetro |

### Totales

| Opción | IMU | Total aprox. |
|---|---|---|
| **Económica** (recomendada si el presupuesto es justo) | MPU6050 + QMC5883L (items 7a + 7b) | **≈ $339.000** |
| **Rápida de integrar** | BNO055 (≈ $110.000) en lugar de 7a + 7b | **≈ $423.000** |
| Extra opcional | VL53L0X (≈ $18.000), 1 motor TT de repuesto (≈ $8.000) | +$26.000 |

**Recomendación:** compren 1 motor TT y 1 H206 de repuesto. Si se daña uno durante las pruebas, no pierden días.

### ¿BNO055 o MPU6050 + QMC5883L?
- **BNO055**: entrega el rumbo ya fusionado y autocalibrado por I²C. Lo hacen funcionar en 1 tarde. Es más caro.
- **MPU6050 + QMC5883L**: ustedes calibran el magnetómetro (*hard/soft iron*) y programan la fusión
  (filtro complementario o Madgwick). Toma más tiempo, pero da más contenido técnico para el informe.
- ⚠️ Muchos módulos "HMC5883L" en realidad traen el chip **QMC5883L**, que usa otra dirección (0x0D) y otra librería.
  Revisen el chip con lupa.

## 2. Asignación de pines del ESP32

| Pin ESP32 | Conecta a | Tipo | Nota |
|---|---|---|---|
| GPIO25 | L298N ENA | PWM (LEDC) | Motor izquierdo, 1 kHz (quitar jumper ENA) |
| GPIO26 | L298N IN1 | Salida | Dirección motor izq. |
| GPIO27 | L298N IN2 | Salida | Dirección motor izq. |
| GPIO14 | L298N ENB | PWM (LEDC) | Motor derecho (quitar jumper ENB) |
| GPIO33 | L298N IN3 | Salida | Dirección motor der. |
| GPIO32 | L298N IN4 | Salida | Dirección motor der. |
| GPIO21 | SDA (IMU, magnetómetro, VL53L0X) | I²C | Bus compartido |
| GPIO22 | SCL | I²C | 100–400 kHz |
| GPIO19 | HC-SR04 TRIG | Salida | 3,3 V es suficiente para disparar |
| GPIO18 | HC-SR04 ECHO | Entrada | **Con divisor 1 k / 2 k** (5 V → 3,3 V) |
| GPIO34 | H206 D0 izquierdo | Entrada (interrupción) | Solo entrada; el módulo trae pull-up |
| GPIO35 | H206 D0 derecho | Entrada (interrupción) | Solo entrada |
| GPIO36 (VP) | Divisor de batería 10 k / 3,3 k | ADC1 | ADC1 funciona con el WiFi activo (ADC2 no) |
| GPIO2 | LED integrado | Salida | Indicador de estado |
| VIN | Salida 5V del L298N (jumper 5V puesto) | Alimentación | |
| 3V3 | VCC del magnetómetro y de los H206 | Alimentación | |

**Pines que se evitaron a propósito:** GPIO12 (si está en alto al arrancar, el ESP32 no inicia), GPIO0/5/15 (pines de arranque),
GPIO6–11 (memoria flash) y TX0/RX0 (monitor serial).

## 3. Alimentación – puntos críticos

1. **Midan con el multímetro la salida 5V del L298N antes de conectarla al VIN del ESP32** (debe dar ~5 V con el jumper 5V puesto).
2. Todas las tierras (batería, buck, driver, ESP32, sensores) deben ir unidas en un punto común.
3. Pongan un capacitor de 470 µF entre 12V y GND del L298N, cerca del módulo, para absorber los picos de los motores.
4. Los motores TT son de 3–6 V. Con 7,4 V y la caída de ~2 V del L298N les llegan ~5,4 V: pueden usar el 100 % del PWM.
5. No conecten el USB y la batería al mismo tiempo, a menos que agreguen un diodo en VIN.
6. Lleven el cable I²C del sensor por dentro del mástil, trenzado (SDA con GND, SCL con 3V3), lejos de los cables de los motores.

## 4. Diagramas

- `diagrama_bloques.png` / `.svg`: arquitectura del sistema (para el informe)
- `diagrama_conexiones.png` / `.svg`: conexión pin a pin del ESP32
- `diagramas.py`: regenera ambos diagramas si cambian algún pin
