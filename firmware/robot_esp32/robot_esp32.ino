/*
  Robot movil diferencial - Entrega 1 (Guia 5)
  ESP32 DevKit V1 + L298N + motores TT 

*/
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include <Preferences.h>
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
const int PIN_LED = -1;                                // el LED de la placa S3 es RGB: no se usa
#else
// ESP32 DevKit V1
const int PIN_ENA = 25, PIN_IN1 = 26, PIN_IN2 = 27;   // motor izquierdo
const int PIN_ENB = 14, PIN_IN3 = 33, PIN_IN4 = 32;   // motor derecho
const int PIN_TRIG = 19, PIN_ECHO = 18;
const int PIN_ENC_IZQ = 34, PIN_ENC_DER = 35;
const int PIN_VBAT = 36;
const int PIN_SDA = 21, PIN_SCL = 22;
const int PIN_LED = 2;
#endif

// L298N
const bool INVERTIR_IZQ = false;   // cambiar si el motor gira al reves
const bool INVERTIR_DER = false;
const int PWM_FREQ = 1000;         // el L298N trabaja bien a ~1 kHz
const int PWM_RES = 8;             // 0..255
const int PWM_MIN = 110;           // PWM minimo para que el motor arranque
const int PWM_MAX = 255;

// HC-SR04 (ECHO con divisor 1k/2k)
const float DIST_PARADA_CM = 15.0;  // bloquea avanzar si hay obstaculo mas cerca

// Encoders H206 (opcionales) y bateria
const int RANURAS_DISCO = 20;
const float DIAMETRO_RUEDA_CM = 6.5;
const float DIVISOR_VBAT = (10.0 + 3.3) / 3.3;

// I2C y magnetometro
const float DECLINACION = -8.0;     // Bogota ~8 grados oeste. Verificar en ngdc.noaa.gov
const bool MAG_INVERTIR_Y = false;  // si al girar a la derecha el rumbo BAJA, poner true

const uint32_t TIMEOUT_CMD_MS = 600;   // sin comandos -> parar (perdida de WiFi)
const uint32_t T_CALIBRACION_MS = 20000;

// ================================ ESTADO ================================
WebServer server(80);
Preferences prefs;

enum Modo { MANUAL, CALIBRANDO, GIRO_AUTO };
Modo modo = MANUAL;

int cmdIzq = 0, cmdDer = 0;          // -100..100 pedidos por la app
int velIzq = 0, velDer = 0;          // aplicados realmente
uint32_t tUltimoCmd = 0;
bool obstaculo = false;

float distanciaCm = -1;

enum MagTipo { MAG_NINGUNO, MAG_QMC, MAG_HMC };
MagTipo magTipo = MAG_NINGUNO;
uint8_t magDir = 0;
int16_t magX = 0, magY = 0, magZ = 0;
float magOffX = 0, magOffY = 0, magEscX = 1, magEscY = 1, ajusteNorte = 0;
float rumbo = 0, rumboSinFiltro = 0;
float filtroSin = 0, filtroCos = 1;
bool calibrado = false;

uint32_t tInicioCal = 0;
int16_t calMinX, calMaxX, calMinY, calMaxY;
String mensaje = "";

float rumboObjetivo = 0;
uint32_t tInicioGiro = 0, tEnObjetivo = 0;

volatile uint32_t pulsosIzq = 0, pulsosDer = 0;
volatile uint32_t tPulsoIzq = 0, tPulsoDer = 0;
float rpmIzq = 0, rpmDer = 0, odometriaCm = 0;

float vbat = 0;

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
  motor(PIN_ENA, PIN_IN1, PIN_IN2, izq, INVERTIR_IZQ);
  motor(PIN_ENB, PIN_IN3, PIN_IN4, der, INVERTIR_DER);
}

// ============================== ENCODERS ==============================
void IRAM_ATTR isrEncIzq() {
  uint32_t t = micros();
  if (t - tPulsoIzq > 1000) { pulsosIzq = pulsosIzq + 1; tPulsoIzq = t; }   // antirrebote 1 ms
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
  // el H206 no da sentido: se toma el signo del comando aplicado
  float cmIzq = di / (float)RANURAS_DISCO * PI * DIAMETRO_RUEDA_CM * (velIzq >= 0 ? 1 : -1);
  float cmDer = dd / (float)RANURAS_DISCO * PI * DIAMETRO_RUEDA_CM * (velDer >= 0 ? 1 : -1);
  odometriaCm += (cmIzq + cmDer) / 2.0;
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
  uint32_t dur = pulseIn(PIN_ECHO, HIGH, 25000);   // ~4 m maximo
  distanciaCm = dur == 0 ? -1 : dur / 58.0;
}

// ============================== MAGNETOMETRO ==============================
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

void magIniciar() {
  if (existe(0x0D)) {                 // QMC5883L (la mayoria de GY-273 / GY-271 actuales)
    magTipo = MAG_QMC;
    magDir = 0x0D;
    escribirReg(magDir, 0x0B, 0x01);  // periodo set/reset
    escribirReg(magDir, 0x09, 0x1D);  // continuo, 200 Hz, 8 G, OSR 512
  } else if (existe(0x1E)) {          // HMC5883L original
    magTipo = MAG_HMC;
    magDir = 0x1E;
    escribirReg(magDir, 0x00, 0x70);  // 8 muestras, 15 Hz
    escribirReg(magDir, 0x01, 0x20);  // ganancia 1.3 G
    escribirReg(magDir, 0x02, 0x00);  // continuo
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

void actualizarRumbo() {
  static uint32_t tAnterior = 0;
  if (millis() - tAnterior < 20) return;
  tAnterior = millis();
  if (!magLeer()) return;

  if (modo == CALIBRANDO) {
    calMinX = min(calMinX, magX); calMaxX = max(calMaxX, magX);
    calMinY = min(calMinY, magY); calMaxY = max(calMaxY, magY);
  }

  // correccion hard-iron (offset) y soft-iron simple (escala por eje)
  float x = (magX - magOffX) * magEscX;
  float y = (magY - magOffY) * magEscY;
  if (MAG_INVERTIR_Y) y = -y;
  // X del sensor = frente del robot, Y = izquierda. Rumbo horario desde el norte.
  float h = atan2(y, x) * 180.0 / PI;
  rumboSinFiltro = normalizar360(h + DECLINACION + ajusteNorte);

  // filtro pasa bajos sobre seno/coseno (evita el salto 359 -> 0)
  const float a = 0.25;
  filtroSin += a * (sin(rumboSinFiltro * PI / 180.0) - filtroSin);
  filtroCos += a * (cos(rumboSinFiltro * PI / 180.0) - filtroCos);
  rumbo = normalizar360(atan2(filtroSin, filtroCos) * 180.0 / PI);
}

void cargarCalibracion() {
  prefs.begin("mag", true);
  calibrado = prefs.getBool("ok", false);
  magOffX = prefs.getFloat("ox", 0);
  magOffY = prefs.getFloat("oy", 0);
  magEscX = prefs.getFloat("sx", 1);
  magEscY = prefs.getFloat("sy", 1);
  ajusteNorte = prefs.getFloat("norte", 0);
  prefs.end();
}

void guardarCalibracion() {
  prefs.begin("mag", false);
  prefs.putBool("ok", calibrado);
  prefs.putFloat("ox", magOffX);
  prefs.putFloat("oy", magOffY);
  prefs.putFloat("sx", magEscX);
  prefs.putFloat("sy", magEscY);
  prefs.putFloat("norte", ajusteNorte);
  prefs.end();
}

void iniciarCalibracion() {
  if (magTipo == MAG_NINGUNO) { mensaje = "No hay magnetometro conectado"; return; }
  modo = CALIBRANDO;
  tInicioCal = millis();
  calMinX = calMinY = 32767;
  calMaxX = calMaxY = -32768;
  mensaje = "Calibrando: el robot gira solo, no lo toque";
}

void tareaCalibracion() {
  if (modo != CALIBRANDO) return;
  mover(45, -45);                    // giro en el sitio
  if (millis() - tInicioCal < T_CALIBRACION_MS) return;
  mover(0, 0);
  modo = MANUAL;
  float rx = (calMaxX - calMinX) / 2.0, ry = (calMaxY - calMinY) / 2.0;
  if (rx < 50 || ry < 50) {
    mensaje = "Calibracion fallida: el robot no giro lo suficiente";
    return;
  }
  magOffX = (calMaxX + calMinX) / 2.0;
  magOffY = (calMaxY + calMinY) / 2.0;
  float r = (rx + ry) / 2.0;
  magEscX = r / rx;
  magEscY = r / ry;
  calibrado = true;
  guardarCalibracion();
  mensaje = "Calibracion guardada";
  Serial.printf("Calibracion: off(%.0f, %.0f) esc(%.3f, %.3f)\n", magOffX, magOffY, magEscX, magEscY);
}

// ============================ MODO AUTONOMO (base) ============================
void tareaGiro() {
  if (modo != GIRO_AUTO) return;
  float err = diferenciaAngulo(rumboObjetivo, rumbo);
  if (fabs(err) < 4) {
    mover(0, 0);
    if (tEnObjetivo == 0) tEnObjetivo = millis();
    if (millis() - tEnObjetivo > 400) {
      modo = MANUAL;
      mensaje = "Rumbo alcanzado";
    }
    return;
  }
  tEnObjetivo = 0;
  if (millis() - tInicioGiro > 10000) {
    mover(0, 0);
    modo = MANUAL;
    mensaje = "Giro cancelado (10 s sin llegar)";
    return;
  }
  // control proporcional; rumbo crece en sentido horario = girar a la derecha
  const float KP = 0.8;
  int w = constrain((int)(KP * err), -60, 60);
  if (abs(w) < 30) w = w > 0 ? 30 : -30;   // zona muerta de los motores
  mover(w, -w);
}

// ================================ MANUAL ================================
void tareaManual() {
  if (modo != MANUAL) return;
  int izq = cmdIzq, der = cmdDer;
  if (millis() - tUltimoCmd > TIMEOUT_CMD_MS) izq = der = 0;
  obstaculo = distanciaCm > 0 && distanciaCm < DIST_PARADA_CM;
  if (obstaculo && izq > 0 && der > 0) izq = der = 0;   // no avanzar contra el obstaculo
  mover(izq, der);
}

// ================================ BATERIA ================================
void actualizarBateria() {
  static uint32_t tAnterior = 0;
  if (millis() - tAnterior < 1000) return;
  tAnterior = millis();
  float v = analogReadMilliVolts(PIN_VBAT) / 1000.0 * DIVISOR_VBAT;
  vbat = v < 1.0 ? 0 : v;   // 0 = divisor no conectado
}

// ================================ SERVIDOR ================================
const char* nombreModo() {
  switch (modo) {
    case CALIBRANDO: return "CALIBRANDO";
    case GIRO_AUTO: return "GIRO AUTO";
    default: return "MANUAL";
  }
}

void enviarEstado() {
  int progreso = modo == CALIBRANDO ? (millis() - tInicioCal) * 100 / T_CALIBRACION_MS : 0;
  char json[512];
  snprintf(json, sizeof(json),
           "{\"rumbo\":%.1f,\"crudo\":%.1f,\"mag\":%d,\"cal\":%d,\"mx\":%d,\"my\":%d,\"mz\":%d,"
           "\"dist\":%.1f,\"obst\":%d,\"modo\":\"%s\",\"prog\":%d,\"vi\":%d,\"vd\":%d,"
           "\"rpmi\":%.0f,\"rpmd\":%.0f,\"odo\":%.1f,\"vbat\":%.2f,\"msg\":\"%s\"}",
           rumbo, rumboSinFiltro, magTipo, calibrado, magX, magY, magZ,
           distanciaCm, obstaculo, nombreModo(), progreso, velIzq, velDer,
           rpmIzq, rpmDer, odometriaCm, vbat, mensaje.c_str());
  server.send(200, "application/json", json);
}

void manejarCtrl() {
  int izq = constrain(server.arg("l").toInt(), -100, 100);
  int der = constrain(server.arg("r").toInt(), -100, 100);
  if ((izq != 0 || der != 0) && modo == GIRO_AUTO) modo = MANUAL;   // el manual manda
  cmdIzq = izq;
  cmdDer = der;
  tUltimoCmd = millis();
  enviarEstado();
}

void manejarGirar() {
  if (magTipo == MAG_NINGUNO) { mensaje = "No hay magnetometro"; enviarEstado(); return; }
  rumboObjetivo = normalizar360(server.arg("h").toFloat());
  modo = GIRO_AUTO;
  tInicioGiro = millis();
  tEnObjetivo = 0;
  mensaje = "Girando a " + String(rumboObjetivo, 0) + " grados";
  enviarEstado();
}

void manejarNorte() {
  if (server.hasArg("borrar")) {
    ajusteNorte = 0;
    mensaje = "Ajuste de norte borrado";
  } else {
    // el robot esta mirando al norte real: el rumbo actual debe ser 0
    ajusteNorte = normalizar360(ajusteNorte - rumboSinFiltro);
    filtroSin = 0;
    filtroCos = 1;
    mensaje = "Norte fijado";
  }
  guardarCalibracion();
  enviarEstado();
}

void manejarStop() {
  modo = MANUAL;
  cmdIzq = cmdDer = 0;
  mover(0, 0);
  mensaje = "Detenido";
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
  if (PIN_LED >= 0) pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_ENC_IZQ, INPUT);
  pinMode(PIN_ENC_DER, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_IZQ), isrEncIzq, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_DER), isrEncDer, RISING);
  analogSetPinAttenuation(PIN_VBAT, ADC_11db);

  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
  magIniciar();
  cargarCalibracion();
  Serial.printf("Magnetometro: %s\n", magTipo == MAG_QMC ? "QMC5883L" :
                                     magTipo == MAG_HMC ? "HMC5883L" : "NO ENCONTRADO");
  mensaje = magTipo == MAG_NINGUNO ? "Sin magnetometro" :
            (calibrado ? "Listo" : "Listo - falta calibrar la brujula");

  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.printf("WiFi: %s  ->  http://%s\n", WIFI_SSID, WiFi.softAPIP().toString().c_str());

  server.on("/", []() { server.send(200, "text/html", PAGINA_WEB); });
  server.on("/ctrl", manejarCtrl);
  server.on("/calibrar", []() { iniciarCalibracion(); enviarEstado(); });
  server.on("/girar", manejarGirar);
  server.on("/norte", manejarNorte);
  server.on("/stop", manejarStop);
  server.begin();
}

void loop() {
  server.handleClient();
  actualizarDistancia();
  actualizarRumbo();
  actualizarEncoders();
  actualizarBateria();
  tareaCalibracion();
  tareaGiro();
  tareaManual();

  // LED: fijo con cliente conectado, parpadeo si no hay nadie
  bool conectado = millis() - tUltimoCmd < 2000;
  if (PIN_LED >= 0) digitalWrite(PIN_LED, conectado ? HIGH : (millis() / 500) % 2);

  static uint32_t tLog = 0;
  if (millis() - tLog > 1000) {
    tLog = millis();
    Serial.printf("rumbo=%.1f mag=(%d,%d,%d) dist=%.1f cm motores=(%d,%d) modo=%s\n",
                  rumbo, magX, magY, magZ, distanciaCm, velIzq, velDer, nombreModo());
  }
}
