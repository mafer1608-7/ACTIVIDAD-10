/*
  Robot movil diferencial - Entrega 1 (version solo modo manual)
  ESP32-S3 (o ESP32) + L298N + 2 motores TT

  El ESP32 crea la red WiFi "ROBOT_MOVIL". Desde el PC o el celular se abre
  http://192.168.4.1 y se maneja con botones o con el teclado (W A S D).
*/
#include <WiFi.h>
#include <WebServer.h>
#include "pagina_web.h"

// ============================== CONFIGURACION ==============================
const char* WIFI_SSID = "ROBOT_MOVIL";
const char* WIFI_PASS = "robot1234";        // minimo 8 caracteres

#if CONFIG_IDF_TARGET_ESP32S3
const int PIN_ENA = 4,  PIN_IN1 = 5,  PIN_IN2 = 6;    // motor izquierdo
const int PIN_ENB = 7,  PIN_IN3 = 15, PIN_IN4 = 16;   // motor derecho
#else
const int PIN_ENA = 25, PIN_IN1 = 26, PIN_IN2 = 27;   // motor izquierdo
const int PIN_ENB = 14, PIN_IN3 = 33, PIN_IN4 = 32;   // motor derecho
#endif

const bool INVERTIR_IZQ = false;   // cambiar a true si ese motor gira al reves
const bool INVERTIR_DER = false;
const int PWM_FREQ = 1000;         // el L298N trabaja bien a ~1 kHz
const int PWM_RES = 8;             // resolucion: valores de 0 a 255
const int PWM_MIN = 110;           // PWM minimo para que el motor arranque
const int PWM_MAX = 255;
const uint32_t TIMEOUT_CMD_MS = 600;   // sin ordenes durante 0,6 s -> parar

// ================================ ESTADO ================================
WebServer server(80);

int cmdIzq = 0, cmdDer = 0;     // lo que pide la pagina (-100 a 100)
int velIzq = 0, velDer = 0;     // lo que se aplica realmente a los motores
uint32_t tUltimoCmd = 0;        // instante de la ultima orden recibida

// ================================ MOTORES ================================
// Mueve un motor. vel: -100 (reversa maxima) a 100 (adelante maxima), 0 = parado.
void motor(int en, int a, int b, int vel, bool invertir) {
  if (invertir) vel = -vel;
  vel = constrain(vel, -100, 100);
  if (vel == 0) {
    digitalWrite(a, LOW);
    digitalWrite(b, LOW);
    ledcWrite(en, 0);
    return;
  }
  digitalWrite(a, vel > 0 ? HIGH : LOW);     // IN1/IN2 definen el sentido
  digitalWrite(b, vel > 0 ? LOW : HIGH);
  ledcWrite(en, map(abs(vel), 1, 100, PWM_MIN, PWM_MAX));   // ENA/ENB definen la velocidad
}

void mover(int izq, int der) {
  velIzq = izq;
  velDer = der;
  motor(PIN_ENA, PIN_IN1, PIN_IN2, izq, INVERTIR_IZQ);
  motor(PIN_ENB, PIN_IN3, PIN_IN4, der, INVERTIR_DER);
}

// ================================ MODO MANUAL ================================
void tareaManual() {
  int izq = cmdIzq, der = cmdDer;
  if (millis() - tUltimoCmd > TIMEOUT_CMD_MS) izq = der = 0;   // seguridad: si se pierde el WiFi, parar
  mover(izq, der);
}

// ================================ SERVIDOR WEB ================================
void enviarEstado() {
  char json[64];
  snprintf(json, sizeof(json), "{\"vi\":%d,\"vd\":%d}", velIzq, velDer);
  server.send(200, "application/json", json);
}

// La pagina llama a /ctrl?l=70&r=70 cada 100 ms con la velocidad de cada lado
void manejarCtrl() {
  cmdIzq = constrain(server.arg("l").toInt(), -100, 100);
  cmdDer = constrain(server.arg("r").toInt(), -100, 100);
  tUltimoCmd = millis();
  enviarEstado();
}

void manejarStop() {
  cmdIzq = cmdDer = 0;
  mover(0, 0);
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

  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  Serial.printf("WiFi: %s  ->  http://%s\n", WIFI_SSID, WiFi.softAPIP().toString().c_str());

  server.on("/", []() { server.send(200, "text/html", PAGINA_WEB); });
  server.on("/ctrl", manejarCtrl);
  server.on("/stop", manejarStop);
  server.begin();
}

void loop() {
  server.handleClient();   // atiende las peticiones de la pagina
  tareaManual();           // aplica la orden a los motores
}
