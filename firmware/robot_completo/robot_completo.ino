/*
  Robot movil de coordenadas polares - Entregas 1 y 2 (Guias 5 y 6)
  ESP32-S3 (o ESP32) + L298N + 2 motores TT + HC-SR04 + magnetometro QMC5883L / HMC5883L
  Opcionales: IMU MPU6050 (GY-521) y encoders H206.

  - Red WiFi "ROBOT_MOVIL" (clave robot1234). Abrir http://192.168.4.1
  - Modo manual (botones o teclado W A S D)
  - Rumbo respecto al norte (magnetometro calibrado; si hay MPU6050 se fusiona con el giroscopio)
  - Modo autonomo: ir a un rumbo (grados desde el norte) durante una distancia (cm),
    manteniendo el rumbo con control proporcional
  - Evasion de obstaculos con el HC-SR04 y recuperacion del rumbo objetivo
  - Estado completo + registro de eventos hacia la app (comunicacion bidireccional)

  Placa: "ESP32S3 Dev Module" (o "ESP32 Dev Module"). Solo usa librerias incluidas en el core.
*/
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Preferences.h>
#include <stdarg.h>
#include <math.h>
#include "pagina_web.h"

// ============================== CONFIGURACION ==============================
const char* WIFI_SSID = "ROBOT_MOVIL";
const char* WIFI_PASS = "robot1234";        // minimo 8 caracteres

#if CONFIG_IDF_TARGET_ESP32S3
// ESP32-S3 (DevKitC-1): se evitan 0,3,45,46 (arranque), 19,20 (USB), 26-37 (flash/PSRAM), 43,44 (UART0)
const int PIN_ENA = 4,  PIN_IN1 = 5,  PIN_IN2 = 6;    // motor izquierdo
const int PIN_ENB = 7,  PIN_IN3 = 15, PIN_IN4 = 16;   // motor derecho
const int PIN_TRIG = 17, PIN_ECHO = 18;
const int PIN_ENC_IZQ = 10, PIN_ENC_DER = 11;
const int PIN_VBAT = 1;
const int PIN_SDA = 8, PIN_SCL = 9;
#else
// ESP32 DevKit V1
const int PIN_ENA = 25, PIN_IN1 = 26, PIN_IN2 = 27;
const int PIN_ENB = 14, PIN_IN3 = 33, PIN_IN4 = 32;
const int PIN_TRIG = 19, PIN_ECHO = 18;
const int PIN_ENC_IZQ = 34, PIN_ENC_DER = 35;
const int PIN_VBAT = 36;
const int PIN_SDA = 21, PIN_SCL = 22;
#endif

// --- Motores (L298N) ---
const bool INVERTIR_IZQ = false;   // cambiar si el motor gira al reves
const bool INVERTIR_DER = true;    // el motor derecho estaba cableado al reves
const bool INTERCAMBIAR_LADOS = true;   // true si "derecha" gira a la izquierda (motores cruzados)
const int PWM_FREQ = 1000;
const int PWM_RES = 8;             // 0..255
const int PWM_MIN = 110;           // PWM minimo para que el motor arranque
const int PWM_MAX = 255;
const uint32_t TIMEOUT_CMD_MS = 600;   // modo manual: sin ordenes -> parar

// --- HC-SR04 (ECHO con divisor 1k/2k) ---
const float DIST_PARADA_CM = 15.0;     // manual: no avanzar si hay algo mas cerca
const float DIST_EVASION_CM = 25.0;    // autonomo: iniciar evasion

// --- Encoders H206 (opcionales) y bateria (opcional) ---
const int RANURAS_DISCO = 20;
const float DIAMETRO_RUEDA_CM = 6.5;
const float CM_POR_PULSO = PI * DIAMETRO_RUEDA_CM / RANURAS_DISCO;
const bool USAR_DIVISOR_BATERIA = false;   // true solo si arman el divisor 10k/3.3k en PIN_VBAT
const float DIVISOR_VBAT = (10.0 + 3.3) / 3.3;

// --- Orientacion ---
const float DECLINACION = -8.0;     // Bogota ~8 grados oeste (verificar en ngdc.noaa.gov)
const float K_FUSION = 0.02;        // peso del magnetometro en la fusion con el giroscopio
const uint32_t T_CALIBRACION_MS = 20000;

// --- Navegacion (ajustar con las pruebas) ---
const float KP_GIRO = 0.7;          // giro en el sitio: PWM% por grado de error
const int GIRO_MIN = 28, GIRO_MAX = 55;
const float TOL_GIRO = 6.0;         // grados
const float KP_RUMBO = 0.9;         // mantener rumbo avanzando
const float MAX_CORR = 30.0;        // correccion maxima entre ruedas (PWM%)
const float ERR_REALINEAR = 40.0;   // si el error supera esto, detenerse y girar en el sitio
const float PASO_LATERAL_CM = 35.0; // avance lateral en cada evasion
const int MAX_INTENTOS_EV = 6;
const uint32_t T_PRUEBA_MS = 3000;  // duracion de la prueba de distancia

// ================================ ESTADO ================================
WebServer server(80);
Preferences prefs;

enum Modo { MANUAL, CALIBRANDO, GIRO_SOLO, MISION, PRUEBA_DIST };
enum Fase { F_NINGUNA, F_ALINEAR, F_AVANZAR, F_EV_GIRO, F_EV_LADO, F_EV_VOLVER, F_EV_REVISAR };
Modo modo = MANUAL;
Fase fase = F_NINGUNA;

int cmdIzq = 0, cmdDer = 0;          // pedido por la app (-100..100)
int velIzq = 0, velDer = 0;          // aplicado a los motores
uint32_t tUltimoCmd = 0;

// distancia
float distanciaCm = -1;
int lecturasCerca = 0;               // lecturas consecutivas por debajo de DIST_EVASION_CM

// magnetometro
enum MagTipo { MAG_NINGUNO, MAG_QMC, MAG_HMC };
MagTipo magTipo = MAG_NINGUNO;
uint8_t magDir = 0;
int16_t magX = 0, magY = 0, magZ = 0;
float magOffX = 0, magOffY = 0, magEscX = 1, magEscY = 1, ajusteNorte = 0;
bool magInvY = false;
bool calibrado = false;

// IMU
const uint8_t IMU_DIR = 0x68;
bool imuOk = false;
float axG = 0, ayG = 0, azG = 0, gxDps = 0, gyDps = 0, gzRaw = 0, gzBias = 0, gzDps = 0;
int giroSigno = 1;
bool giroSignoOk = false;

// rumbo
// Si no hay magnetometro, estimar el rumbo (queda marcado como ESTIMADO en la app).
const bool PERMITIR_RUMBO_ESTIMADO = true;
float kGiro = 1.5;                   // grados/s por cada 1% de diferencia entre ruedas (ajustar con /kgiro)
bool rumboEstimado() { return PERMITIR_RUMBO_ESTIMADO && magTipo == MAG_NINGUNO; }
float rumbo = 0, rumboMag = 0;
float filtroSin = 0, filtroCos = 1, yaw = 0;
bool yawInit = false;

// calibracion
uint32_t tInicioCal = 0;
int16_t calMinX, calMaxX, calMinY, calMaxY;
const int CAL_BUF = 150;
int16_t calBufX[CAL_BUF], calBufY[CAL_BUF];
int calBufN = 0;
float gzSumCal = 0;
int gzNCal = 0;

// navegacion
float rumboObjetivo = 0, distanciaObjetivoCm = 0, progresoCm = 0, ladoRecorridoCm = 0;
int velAuto = 60;
int ladoEv = 1;                      // +1 evade por la derecha, -1 por la izquierda
int intentosEv = 0;
uint32_t tFase = 0, tEnObjetivo = 0;
bool usarEncoders = true;
float pulsosEnTramo = 0;
float cmPorSeg = 20.0;               // distancia por tiempo (se calibra con la prueba)
float factorEnc = 1.0;               // correccion de los encoders (se calibra con la prueba)
float pulsosPrueba = 0;

// encoders
volatile uint32_t pulsosIzq = 0, pulsosDer = 0;
volatile uint32_t tPulsoIzq = 0, tPulsoDer = 0;
float rpmIzq = 0, rpmDer = 0, odometriaCm = 0;

float vbat = 0;

// registro de eventos
const int N_EV = 8;
char evTxt[N_EV][72];
uint32_t evId = 0;

void evento(const char* fmt, ...) {
  char msg[56];
  va_list ap;
  va_start(ap, fmt);
  vsnprintf(msg, sizeof(msg), fmt, ap);
  va_end(ap);
  snprintf(evTxt[evId % N_EV], sizeof(evTxt[0]), "[%.1fs] %s", millis() / 1000.0, msg);
  Serial.println(evTxt[evId % N_EV]);
  evId++;
}

// ================================ UTILIDADES ================================
float normalizar360(float a) {
  while (a < 0) a += 360;
  while (a >= 360) a -= 360;
  return a;
}

float diferenciaAngulo(float objetivo, float actual) {   // -180..180
  float d = objetivo - actual;
  while (d > 180) d -= 360;
  while (d < -180) d += 360;
  return d;
}

void escribirReg(uint8_t dir, uint8_t reg, uint8_t val) {
  Wire.beginTransmission(dir);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

bool existe(uint8_t dir) {
  Wire.beginTransmission(dir);
  return Wire.endTransmission() == 0;
}

// ================================ MOTORES ================================
void motor(int en, int a, int b, int vel, bool invertir) {
  if (invertir) vel = -vel;
  vel = constrain(vel, -100, 100);
  if (vel == 0) {
    digitalWrite(a, LOW);
    digitalWrite(b, LOW);
    ledcWrite(en, 0);
    return;
  }
  digitalWrite(a, vel > 0 ? HIGH : LOW);
  digitalWrite(b, vel > 0 ? LOW : HIGH);
  ledcWrite(en, map(abs(vel), 1, 100, PWM_MIN, PWM_MAX));
}

void mover(int izq, int der) {
  velIzq = izq;
  velDer = der;
  if (INTERCAMBIAR_LADOS) {          // el canal A esta en el lado derecho y el B en el izquierdo
    motor(PIN_ENA, PIN_IN1, PIN_IN2, der, INVERTIR_IZQ);
    motor(PIN_ENB, PIN_IN3, PIN_IN4, izq, INVERTIR_DER);
  } else {
    motor(PIN_ENA, PIN_IN1, PIN_IN2, izq, INVERTIR_IZQ);
    motor(PIN_ENB, PIN_IN3, PIN_IN4, der, INVERTIR_DER);
  }
}

// ============================== ENCODERS ==============================
void IRAM_ATTR isrEncIzq() {
  uint32_t t = micros();
  if (t - tPulsoIzq > 1000) { pulsosIzq = pulsosIzq + 1; tPulsoIzq = t; }
}

void IRAM_ATTR isrEncDer() {
  uint32_t t = micros();
  if (t - tPulsoDer > 1000) { pulsosDer = pulsosDer + 1; tPulsoDer = t; }
}

void actualizarEncoders() {
  static uint32_t tAnterior = 0, antIzq = 0, antDer = 0;
  uint32_t ahora = millis();
  if (ahora - tAnterior < 500) return;
  float dt = (ahora - tAnterior) / 1000.0;
  tAnterior = ahora;
  noInterrupts();
  uint32_t pi = pulsosIzq, pd = pulsosDer;
  interrupts();
  uint32_t di = pi - antIzq, dd = pd - antDer;
  antIzq = pi;
  antDer = pd;
  rpmIzq = di / (float)RANURAS_DISCO / dt * 60.0;
  rpmDer = dd / (float)RANURAS_DISCO / dt * 60.0;
  float cmIzq = di * CM_POR_PULSO * (velIzq >= 0 ? 1 : -1);
  float cmDer = dd * CM_POR_PULSO * (velDer >= 0 ? 1 : -1);
  odometriaCm += (cmIzq + cmDer) / 2.0;
}

// Distancia recorrida avanzando (solo cuenta cuando las dos ruedas van hacia adelante)
void actualizarProgreso() {
  static uint32_t tPrev = 0, pI = 0, pD = 0;
  uint32_t ahora = millis();
  float dt = (ahora - tPrev) / 1000.0;
  tPrev = ahora;
  if (dt > 0.2) dt = 0.2;
  noInterrupts();
  uint32_t ci = pulsosIzq, cd = pulsosDer;
  interrupts();
  float dPulsos = ((ci - pI) + (cd - pD)) / 2.0;
  pI = ci;
  pD = cd;

  if (modo == PRUEBA_DIST) { pulsosPrueba += dPulsos; return; }
  if (modo != MISION) return;
  bool avanzando = (fase == F_AVANZAR || fase == F_EV_LADO) && velIzq > 0 && velDer > 0;
  if (!avanzando) return;

  float dCm;
  if (usarEncoders) {
    dCm = dPulsos * CM_POR_PULSO * factorEnc;
    if (fase == F_AVANZAR) pulsosEnTramo += dPulsos;
  } else {
    dCm = cmPorSeg * ((velIzq + velDer) / 2.0 / velAuto) * dt;
  }
  if (fase == F_EV_LADO) ladoRecorridoCm += dCm;
  else progresoCm += dCm;
}

// ============================== ULTRASONICO ==============================
void actualizarDistancia() {
  static uint32_t tAnterior = 0;
  if (millis() - tAnterior < 70) return;
  tAnterior = millis();
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);
  uint32_t dur = pulseIn(PIN_ECHO, HIGH, 15000);   // ~2.5 m maximo
  distanciaCm = dur == 0 ? -1 : dur / 58.0;
  if (distanciaCm > 0 && distanciaCm < DIST_EVASION_CM) lecturasCerca++;
  else lecturasCerca = 0;
}

bool obstaculoCerca() { return lecturasCerca >= 2; }   // 2 lecturas seguidas: evita falsos positivos

// ============================== MAGNETOMETRO ==============================
void magIniciar() {
  if (existe(0x0D)) {                 // QMC5883L (la mayoria de GY-273)
    magTipo = MAG_QMC;
    magDir = 0x0D;
    escribirReg(magDir, 0x0B, 0x01);
    escribirReg(magDir, 0x09, 0x1D);  // continuo, 200 Hz, 8 G, OSR 512
  } else if (existe(0x1E)) {          // HMC5883L original
    magTipo = MAG_HMC;
    magDir = 0x1E;
    escribirReg(magDir, 0x00, 0x70);
    escribirReg(magDir, 0x01, 0x20);
    escribirReg(magDir, 0x02, 0x00);
  } else {
    magTipo = MAG_NINGUNO;
  }
}

bool magLeer() {
  if (magTipo == MAG_NINGUNO) return false;
  Wire.beginTransmission(magDir);
  Wire.write(magTipo == MAG_QMC ? 0x00 : 0x03);
  if (Wire.endTransmission() != 0) return false;
  if (Wire.requestFrom(magDir, (uint8_t)6) != 6) return false;
  uint8_t b[6];
  for (int i = 0; i < 6; i++) b[i] = Wire.read();
  if (magTipo == MAG_QMC) {           // LSB primero, orden X Y Z
    magX = (int16_t)(b[1] << 8 | b[0]);
    magY = (int16_t)(b[3] << 8 | b[2]);
    magZ = (int16_t)(b[5] << 8 | b[4]);
  } else {                            // MSB primero, orden X Z Y
    magX = (int16_t)(b[0] << 8 | b[1]);
    magZ = (int16_t)(b[2] << 8 | b[3]);
    magY = (int16_t)(b[4] << 8 | b[5]);
  }
  return true;
}

// ================================== IMU ==================================
void imuIniciar() {
  imuOk = false;
  if (!existe(IMU_DIR)) return;
  escribirReg(IMU_DIR, 0x6B, 0x01);   // despertar, reloj del giroscopio
  delay(50);
  escribirReg(IMU_DIR, 0x1A, 0x03);   // filtro pasa bajos ~44 Hz
  escribirReg(IMU_DIR, 0x1B, 0x10);   // giroscopio +-1000 dps (32.8 LSB/dps)
  escribirReg(IMU_DIR, 0x1C, 0x00);   // acelerometro +-2 g (16384 LSB/g)
  imuOk = true;
}

bool imuLeer() {
  if (!imuOk) return false;
  Wire.beginTransmission(IMU_DIR);
  Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(IMU_DIR, (uint8_t)14) != 14) return false;
  uint8_t b[14];
  for (int i = 0; i < 14; i++) b[i] = Wire.read();
  int16_t v[7];
  for (int i = 0; i < 7; i++) v[i] = (int16_t)(b[2 * i] << 8 | b[2 * i + 1]);
  axG = v[0] / 16384.0;
  ayG = v[1] / 16384.0;
  azG = v[2] / 16384.0;
  gxDps = v[4] / 32.8;
  gyDps = v[5] / 32.8;
  gzRaw = v[6] / 32.8;
  gzDps = gzRaw - gzBias;
  return true;
}

void imuSesgo() {                      // el robot debe estar quieto al encender
  if (!imuOk) return;
  float suma = 0;
  int n = 0;
  for (int i = 0; i < 200; i++) {
    if (imuLeer()) { suma += gzRaw; n++; }
    delay(5);
  }
  if (n > 50) gzBias = suma / n;
}

// ================================ RUMBO ================================
void actualizarRumbo() {
  static uint32_t tAnterior = 0;
  uint32_t ahora = millis();
  if (ahora - tAnterior < 20) return;
  float dt = (ahora - tAnterior) / 1000.0;
  tAnterior = ahora;
  if (dt > 0.2) dt = 0.2;

  bool magOk = magLeer();
  bool imuLeida = imuLeer();

  // RESPALDO sin magnetometro: el rumbo es una ESTIMACION (no una medicion).
  // Con MPU6050 se integra el giroscopio; sin el, se integra la orden a los motores.
  if (rumboEstimado()) {
    if (!yawInit) { yaw = 0; yawInit = true; }
    float d = (imuOk && imuLeida) ? giroSigno * gzDps * dt
                                  : kGiro * (float)(velIzq - velDer) * dt;
    yaw = normalizar360(yaw + d);
    rumbo = yaw;
    return;
  }

  if (modo == CALIBRANDO) {
    if (magOk) {
      calMinX = min(calMinX, magX); calMaxX = max(calMaxX, magX);
      calMinY = min(calMinY, magY); calMaxY = max(calMaxY, magY);
      calBufX[calBufN % CAL_BUF] = magX;
      calBufY[calBufN % CAL_BUF] = magY;
      calBufN++;
    }
    if (imuLeida) { gzSumCal += gzDps; gzNCal++; }
  }

  if (magOk) {
    float x = (magX - magOffX) * magEscX;
    float y = (magY - magOffY) * magEscY;
    if (magInvY) y = -y;
    // X del sensor = frente, Y = izquierda: rumbo horario desde el norte
    rumboMag = normalizar360(atan2(y, x) * 180.0 / PI + DECLINACION + ajusteNorte);
  }

  bool usarGiro = imuOk && giroSignoOk && imuLeida;
  if (usarGiro) {
    if (!yawInit && magOk) { yaw = rumboMag; yawInit = true; }
    yaw = normalizar360(yaw + giroSigno * gzDps * dt);          // integrar el giroscopio
    if (magOk) yaw = normalizar360(yaw + K_FUSION * diferenciaAngulo(rumboMag, yaw));
    rumbo = yaw;
  } else if (magOk) {
    const float a = 0.25;                                       // filtro sobre seno/coseno
    filtroSin += a * (sin(rumboMag * PI / 180.0) - filtroSin);
    filtroCos += a * (cos(rumboMag * PI / 180.0) - filtroCos);
    rumbo = normalizar360(atan2(filtroSin, filtroCos) * 180.0 / PI);
    yaw = rumbo;
  }
}

// ============================ CALIBRACION / MEMORIA ============================
void cargarCalibracion() {
  prefs.begin("robot", true);
  calibrado = prefs.getBool("ok", false);
  magOffX = prefs.getFloat("ox", 0);
  magOffY = prefs.getFloat("oy", 0);
  magEscX = prefs.getFloat("sx", 1);
  magEscY = prefs.getFloat("sy", 1);
  ajusteNorte = prefs.getFloat("norte", 0);
  magInvY = prefs.getBool("invy", false);
  giroSigno = prefs.getInt("gsig", 1);
  giroSignoOk = prefs.getBool("gok", false);
  cmPorSeg = prefs.getFloat("cmps", 20.0);
  factorEnc = prefs.getFloat("fenc", 1.0);
  kGiro = prefs.getFloat("kgiro", 1.5);
  prefs.end();
}

void guardarCalibracion() {
  prefs.begin("robot", false);
  prefs.putBool("ok", calibrado);
  prefs.putFloat("ox", magOffX);
  prefs.putFloat("oy", magOffY);
  prefs.putFloat("sx", magEscX);
  prefs.putFloat("sy", magEscY);
  prefs.putFloat("norte", ajusteNorte);
  prefs.putBool("invy", magInvY);
  prefs.putInt("gsig", giroSigno);
  prefs.putBool("gok", giroSignoOk);
  prefs.putFloat("cmps", cmPorSeg);
  prefs.putFloat("fenc", factorEnc);
  prefs.putFloat("kgiro", kGiro);
  prefs.end();
}

void iniciarCalibracion() {
  if (magTipo == MAG_NINGUNO) { evento("No hay magnetometro conectado"); return; }
  modo = CALIBRANDO;
  fase = F_NINGUNA;
  tInicioCal = millis();
  calMinX = calMinY = 32767;
  calMaxX = calMaxY = -32768;
  calBufN = 0;
  gzSumCal = 0;
  gzNCal = 0;
  evento("Calibrando: el robot gira solo 20 s");
}

void finalizarCalibracion() {
  mover(0, 0);
  modo = MANUAL;
  float rx = (calMaxX - calMinX) / 2.0, ry = (calMaxY - calMinY) / 2.0;
  if (rx < 50 || ry < 50) {
    evento("Calibracion fallida: no giro lo suficiente");
    return;
  }
  magOffX = (calMaxX + calMinX) / 2.0;
  magOffY = (calMaxY + calMinY) / 2.0;
  float r = (rx + ry) / 2.0;
  magEscX = r / rx;
  magEscY = r / ry;
  calibrado = true;

  // Sentido del magnetometro: el robot giro en sentido horario, el rumbo debe SUBIR
  int n = min(calBufN, CAL_BUF);
  if (n > 20) {
    float total = 0, prev = 0;
    for (int i = 0; i < n; i++) {
      int k = (calBufN > CAL_BUF) ? (calBufN + i) % CAL_BUF : i;
      float ang = atan2((calBufY[k] - magOffY) * magEscY, (calBufX[k] - magOffX) * magEscX) * 180.0 / PI;
      if (i > 0) total += diferenciaAngulo(ang, prev);
      prev = ang;
    }
    if (total > 90) magInvY = false;
    else if (total < -90) magInvY = true;
    else evento("Sentido de la brujula no claro: use Invertir");
  }

  // Sentido del giroscopio con el mismo giro horario
  if (imuOk && gzNCal > 20) {
    float media = gzSumCal / gzNCal;
    if (fabs(media) > 15) {
      giroSigno = media > 0 ? 1 : -1;
      giroSignoOk = true;
    } else {
      giroSignoOk = false;
      evento("Giroscopio sin senal clara: solo brujula");
    }
  }
  yawInit = false;
  filtroSin = 0;
  filtroCos = 1;
  guardarCalibracion();
  evento("Calibracion lista. Fije el norte");
}

void tareaCalibracion() {
  if (modo != CALIBRANDO) return;
  mover(45, -45);                                // giro horario en el sitio
  if (millis() - tInicioCal >= T_CALIBRACION_MS) finalizarCalibracion();
}

// ============================ NAVEGACION AUTONOMA ============================
void cambiarFase(int f) {
  fase = (Fase)f;
  tFase = millis();
  tEnObjetivo = 0;
}

void terminarMision(const char* texto) {
  mover(0, 0);
  modo = MANUAL;
  fase = F_NINGUNA;
  cmdIzq = cmdDer = 0;
  evento("%s", texto);
}

// Giro en el sitio hacia un rumbo. Devuelve true cuando lleva 0.4 s dentro de la tolerancia.
bool girarHacia(float objetivo) {
  float err = diferenciaAngulo(objetivo, rumbo);
  if (fabs(err) < TOL_GIRO) {
    mover(0, 0);
    if (tEnObjetivo == 0) tEnObjetivo = millis();
    return millis() - tEnObjetivo > 400;
  }
  tEnObjetivo = 0;
  int w = constrain((int)(KP_GIRO * err), -GIRO_MAX, GIRO_MAX);
  if (abs(w) < GIRO_MIN) w = w > 0 ? GIRO_MIN : -GIRO_MIN;
  mover(w, -w);                                  // err > 0: girar a la derecha (horario)
  return false;
}

// Avanza manteniendo un rumbo. err > 0: el objetivo esta a la derecha -> rueda izquierda mas rapida
void avanzarConRumbo(float objetivo, int v) {
  float err = diferenciaAngulo(objetivo, rumbo);
  if (fabs(err) > ERR_REALINEAR) {
    int w = constrain((int)(KP_GIRO * err), -GIRO_MAX, GIRO_MAX);
    if (abs(w) < GIRO_MIN) w = w > 0 ? GIRO_MIN : -GIRO_MIN;
    mover(w, -w);
    return;
  }
  float c = constrain(KP_RUMBO * err, -MAX_CORR, MAX_CORR);
  mover(constrain((int)(v + c), -100, 100), constrain((int)(v - c), -100, 100));
}

void iniciarMision(float h, float d, int v) {
  if (magTipo == MAG_NINGUNO && !rumboEstimado()) { evento("Sin magnetometro: no hay mision"); return; }
  rumboObjetivo = normalizar360(h);
  distanciaObjetivoCm = constrain(d, 10, 2000);
  velAuto = constrain(v, 35, 90);
  progresoCm = 0;
  ladoRecorridoCm = 0;
  intentosEv = 0;
  pulsosEnTramo = 0;
  usarEncoders = true;
  ladoEv = 1;
  modo = MISION;
  cambiarFase(F_ALINEAR);
  evento("Mision: %.0f grados, %.0f cm, vel %d%%", rumboObjetivo, distanciaObjetivoCm, velAuto);
}

void tareaMision() {
  if (modo != MISION) return;
  switch (fase) {
    case F_ALINEAR:
      if (girarHacia(rumboObjetivo)) {
        evento("Alineado a %.0f grados (real %.0f)", rumboObjetivo, rumbo);
        cambiarFase(F_AVANZAR);
      } else if (millis() - tFase > 12000) {
        terminarMision("Abortada: no logra alinearse (revise la brujula)");
      }
      break;

    case F_AVANZAR:
      if (progresoCm >= distanciaObjetivoCm) {
        char t[56];
        snprintf(t, sizeof(t), "Meta: %.0f cm recorridos, rumbo %.0f", progresoCm, rumbo);
        terminarMision(t);
        break;
      }
      if (obstaculoCerca()) {
        mover(0, 0);
        evento("Obstaculo a %.0f cm", distanciaCm);
        intentosEv = 0;
        ladoEv = 1;
        cambiarFase(F_EV_GIRO);
        break;
      }
      if (usarEncoders && millis() - tFase > 1500 && pulsosEnTramo < 2) {
        usarEncoders = false;
        evento("Sin encoders: distancia por tiempo");
      }
      avanzarConRumbo(rumboObjetivo, velAuto);
      break;

    case F_EV_GIRO: {
      float rumboLado = normalizar360(rumboObjetivo + 90.0 * ladoEv);
      if (girarHacia(rumboLado)) {
        ladoRecorridoCm = 0;
        evento("Evadiendo por la %s", ladoEv > 0 ? "derecha" : "izquierda");
        cambiarFase(F_EV_LADO);
      } else if (millis() - tFase > 12000) {
        terminarMision("Abortada: no logra girar para evadir");
      }
      break;
    }

    case F_EV_LADO: {
      float rumboLado = normalizar360(rumboObjetivo + 90.0 * ladoEv);
      if (obstaculoCerca()) {
        mover(0, 0);
        intentosEv++;
        if (intentosEv >= MAX_INTENTOS_EV) { terminarMision("Abortada: obstaculo no evadido"); break; }
        ladoEv = -ladoEv;
        evento("Lado bloqueado: cambio de lado");
        cambiarFase(F_EV_GIRO);
        break;
      }
      if (ladoRecorridoCm >= PASO_LATERAL_CM) {
        mover(0, 0);
        evento("Recuperando rumbo %.0f", rumboObjetivo);
        cambiarFase(F_EV_VOLVER);
        break;
      }
      avanzarConRumbo(rumboLado, velAuto);
      break;
    }

    case F_EV_VOLVER:
      if (girarHacia(rumboObjetivo)) cambiarFase(F_EV_REVISAR);
      else if (millis() - tFase > 12000) terminarMision("Abortada: no recupera el rumbo");
      break;

    case F_EV_REVISAR:
      if (millis() - tFase < 350) break;          // esperar lecturas nuevas del HC-SR04
      if (obstaculoCerca()) {
        intentosEv++;
        if (intentosEv >= MAX_INTENTOS_EV) { terminarMision("Abortada: obstaculo no evadido"); break; }
        evento("Sigue el obstaculo: otro paso lateral");
        cambiarFase(F_EV_GIRO);
      } else {
        evento("Rumbo recuperado: %.0f grados", rumbo);
        cambiarFase(F_AVANZAR);
      }
      break;

    default:
      break;
  }
}

// Giro solo (sin avanzar), util para probar el control de rumbo
void tareaGiroSolo() {
  if (modo != GIRO_SOLO) return;
  if (girarHacia(rumboObjetivo)) {
    mover(0, 0);
    modo = MANUAL;
    evento("Rumbo alcanzado: %.0f grados", rumbo);
  } else if (millis() - tFase > 12000) {
    mover(0, 0);
    modo = MANUAL;
    evento("Giro cancelado (12 s sin llegar)");
  }
}

// Prueba de distancia: avanza 3 s en linea recta para medir cuanto recorre
void tareaPrueba() {
  if (modo != PRUEBA_DIST) return;
  if (millis() - tFase < T_PRUEBA_MS) { mover(velAuto, velAuto); return; }
  mover(0, 0);
  modo = MANUAL;
  evento("Prueba lista: encoders %.0f cm. Mida y escriba", pulsosPrueba * CM_POR_PULSO);
}

// ================================ MANUAL ================================
void tareaManual() {
  if (modo != MANUAL) return;
  int izq = cmdIzq, der = cmdDer;
  if (millis() - tUltimoCmd > TIMEOUT_CMD_MS) izq = der = 0;
  if (distanciaCm > 0 && distanciaCm < DIST_PARADA_CM && izq > 0 && der > 0) izq = der = 0;
  mover(izq, der);
}

void actualizarBateria() {
  static uint32_t tAnterior = 0;
  if (millis() - tAnterior < 1000) return;
  tAnterior = millis();
  if (!USAR_DIVISOR_BATERIA) { vbat = 0; return; }
  vbat = analogReadMilliVolts(PIN_VBAT) / 1000.0 * DIVISOR_VBAT;
}

// ================================ SERVIDOR ================================
const char* nombreModo() {
  switch (modo) {
    case CALIBRANDO: return "CALIBRANDO";
    case GIRO_SOLO: return "GIRO";
    case MISION: return "AUTONOMO";
    case PRUEBA_DIST: return "PRUEBA";
    default: return "MANUAL";
  }
}

const char* nombreFase() {
  switch (fase) {
    case F_ALINEAR: return "Alineando";
    case F_AVANZAR: return "Avanzando";
    case F_EV_GIRO: return "Evasion: giro";
    case F_EV_LADO: return "Evasion: paso lateral";
    case F_EV_VOLVER: return "Evasion: recuperar rumbo";
    case F_EV_REVISAR: return "Evasion: revisando";
    default: return "-";
  }
}

void enviarEstado() {
  static char b[2000];
  int calProg = modo == CALIBRANDO ? (int)((millis() - tInicioCal) * 100UL / T_CALIBRACION_MS) : 0;
  bool usarGiro = imuOk && giroSignoOk;
  int n = 0;
  n += snprintf(b + n, sizeof(b) - n,
                "{\"t\":%lu,\"rumbo\":%.1f,\"crudo\":%.1f,\"mag\":%d,\"cal\":%d,\"mx\":%d,\"my\":%d,\"mz\":%d,"
                "\"imu\":%d,\"giro\":%d,\"ax\":%.2f,\"ay\":%.2f,\"az\":%.2f,\"gx\":%.1f,\"gy\":%.1f,\"gz\":%.1f,",
                (unsigned long)millis(), rumbo, rumboMag, magTipo, calibrado, magX, magY, magZ,
                imuOk, usarGiro, axG, ayG, azG, gxDps, gyDps, gzDps);
  n += snprintf(b + n, sizeof(b) - n,
                "\"dist\":%.1f,\"obst\":%d,\"modo\":\"%s\",\"fase\":\"%s\",\"obj\":%.1f,\"dobj\":%.0f,"
                "\"prog\":%.1f,\"cal_prog\":%d,\"vi\":%d,\"vd\":%d,\"rpmi\":%.0f,\"rpmd\":%.0f,\"odo\":%.1f,",
                distanciaCm, distanciaCm > 0 && distanciaCm < DIST_EVASION_CM, nombreModo(), nombreFase(),
                rumboObjetivo, distanciaObjetivoCm, progresoCm, calProg, velIzq, velDer, rpmIzq, rpmDer,
                odometriaCm);
  n += snprintf(b + n, sizeof(b) - n,
                "\"enc\":%d,\"cmps\":%.1f,\"fenc\":%.3f,\"pcm\":%.1f,\"vbat\":%.2f,\"invy\":%d,\"est\":%d,\"ev\":[",
                usarEncoders, cmPorSeg, factorEnc, pulsosPrueba * CM_POR_PULSO, vbat, magInvY, rumboEstimado());
  uint32_t desde = evId > N_EV ? evId - N_EV : 0;
  for (uint32_t i = desde; i < evId; i++) {
    n += snprintf(b + n, sizeof(b) - n, "%s\"%s\"", i > desde ? "," : "", evTxt[i % N_EV]);
  }
  snprintf(b + n, sizeof(b) - n, "]}");
  server.send(200, "application/json", b);
}

void cancelarAutomatico(const char* motivo) {
  if (modo == MISION || modo == GIRO_SOLO || modo == PRUEBA_DIST) {
    modo = MANUAL;
    fase = F_NINGUNA;
    evento("%s", motivo);
  }
}

void manejarCtrl() {
  int izq = constrain(server.arg("l").toInt(), -100, 100);
  int der = constrain(server.arg("r").toInt(), -100, 100);
  if (izq != 0 || der != 0) cancelarAutomatico("Cancelado: control manual");
  cmdIzq = izq;
  cmdDer = der;
  tUltimoCmd = millis();
  enviarEstado();
}

void manejarMision() {
  if (modo == CALIBRANDO) { enviarEstado(); return; }
  iniciarMision(server.arg("h").toFloat(), server.arg("d").toFloat(), server.arg("v").toInt());
  enviarEstado();
}

void manejarGirar() {
  if (modo == CALIBRANDO || (magTipo == MAG_NINGUNO && !rumboEstimado())) { enviarEstado(); return; }
  rumboObjetivo = normalizar360(server.arg("h").toFloat());
  modo = GIRO_SOLO;
  cambiarFase(F_NINGUNA);
  evento("Girando a %.0f grados", rumboObjetivo);
  enviarEstado();
}

void manejarPrueba() {
  if (modo == CALIBRANDO) { enviarEstado(); return; }
  if (server.hasArg("v")) velAuto = constrain(server.arg("v").toInt(), 35, 90);
  pulsosPrueba = 0;
  modo = PRUEBA_DIST;
  tFase = millis();
  evento("Prueba de distancia: 3 s en linea recta");
  enviarEstado();
}

void manejarCalDist() {
  float cm = server.arg("cm").toFloat();
  if (cm >= 5) {
    cmPorSeg = cm / (T_PRUEBA_MS / 1000.0);
    if (pulsosPrueba > 5) factorEnc = constrain(cm / (pulsosPrueba * CM_POR_PULSO), 0.5, 2.0);
    guardarCalibracion();
    evento("Distancia calibrada: %.1f cm/s, factor enc %.2f", cmPorSeg, factorEnc);
  }
  enviarEstado();
}

void manejarNorte() {
  if (server.hasArg("borrar")) {
    ajusteNorte = 0;
    evento("Ajuste de norte borrado");
  } else {
    ajusteNorte = normalizar360(ajusteNorte - rumboMag);     // el rumbo actual pasa a ser 0
    filtroSin = 0;
    filtroCos = 1;
    yaw = 0;
    yawInit = true;
    evento("Norte fijado (rumbo = 0)");
  }
  guardarCalibracion();
  enviarEstado();
}

// /kgiro?cmd=90&real=75 : "ordene 90 grados y giro 75": corrige la constante de giro estimado
void manejarKGiro() {
  float c = server.arg("cmd").toFloat(), r = server.arg("real").toFloat();
  if (c > 5 && r > 5) {
    float mag = constrain(fabs(kGiro) * r / c, 0.2, 10.0);
    kGiro = kGiro < 0 ? -mag : mag;
    guardarCalibracion();
    evento("Constante de giro: %.2f grados/s por %%", kGiro);
  }
  enviarEstado();
}

void manejarInvertir() {
  if (rumboEstimado()) {                         // sin magnetometro: invierte el sentido del giro estimado
    if (imuOk) giroSigno = -giroSigno; else kGiro = -kGiro;
    guardarCalibracion();
    evento("Sentido del giro estimado invertido");
    enviarEstado();
    return;
  }
  magInvY = !magInvY;
  yawInit = false;
  guardarCalibracion();
  evento("Sentido de la brujula invertido");
  enviarEstado();
}

void manejarStop() {
  modo = MANUAL;
  fase = F_NINGUNA;
  cmdIzq = cmdDer = 0;
  mover(0, 0);
  evento("Detenido");
  enviarEstado();
}

// ================================ SETUP / LOOP ================================
void setup() {
  Serial.begin(115200);
  pinMode(PIN_IN1, OUTPUT); pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_IN3, OUTPUT); pinMode(PIN_IN4, OUTPUT);
  ledcAttach(PIN_ENA, PWM_FREQ, PWM_RES);
  ledcAttach(PIN_ENB, PWM_FREQ, PWM_RES);
  mover(0, 0);

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_ENC_IZQ, INPUT_PULLUP);
  pinMode(PIN_ENC_DER, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_IZQ), isrEncIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_DER), isrEncDer, RISING);
  if (USAR_DIVISOR_BATERIA) analogSetPinAttenuation(PIN_VBAT, ADC_11db);

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
  Wire.setTimeOut(30);
  magIniciar();
  imuIniciar();
  imuSesgo();
  cargarCalibracion();

  Serial.printf("Magnetometro: %s | IMU: %s\n",
                magTipo == MAG_QMC ? "QMC5883L" : magTipo == MAG_HMC ? "HMC5883L" : "NO ENCONTRADO",
                imuOk ? "MPU6050" : "no detectado");
  if (magTipo == MAG_NINGUNO) evento(rumboEstimado() ? "SIN magnetometro: rumbo ESTIMADO" : "Sin magnetometro");
  else if (!calibrado) evento("Falta calibrar la brujula");
  else evento("Listo");

  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.printf("WiFi: %s  ->  http://%s\n", WIFI_SSID, WiFi.softAPIP().toString().c_str());

  server.on("/", []() { server.send(200, "text/html", PAGINA_WEB); });
  server.on("/ctrl", manejarCtrl);
  server.on("/estado", enviarEstado);
  server.on("/stop", manejarStop);
  server.on("/calibrar", []() { iniciarCalibracion(); enviarEstado(); });
  server.on("/norte", manejarNorte);
  server.on("/invertir", manejarInvertir);
  server.on("/girar", manejarGirar);
  server.on("/mision", manejarMision);
  server.on("/pruebadist", manejarPrueba);
  server.on("/caldist", manejarCalDist);
  server.on("/kgiro", manejarKGiro);
  server.begin();
}

void loop() {
  server.handleClient();
  actualizarDistancia();
  actualizarRumbo();
  actualizarEncoders();
  actualizarProgreso();
  actualizarBateria();
  tareaCalibracion();
  tareaGiroSolo();
  tareaMision();
  tareaPrueba();
  tareaManual();

  static uint32_t tLog = 0;
  if (millis() - tLog > 1000) {
    tLog = millis();
    Serial.printf("%s/%s rumbo=%.1f obj=%.0f dist=%.1f prog=%.0f/%.0f motores=(%d,%d)\n",
                  nombreModo(), nombreFase(), rumbo, rumboObjetivo, distanciaCm,
                  progresoCm, distanciaObjetivoCm, velIzq, velDer);
  }
}
