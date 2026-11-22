// Escaner I2C para ESP32-S3.
// Prueba SDA=8/SCL=9 (lo normal) y tambien SDA=9/SCL=8 (por si estan cruzados).
// Abrir el Monitor Serie a 115200.
#include <Wire.h>

const int PIN_A = 8;
const int PIN_B = 9;

int escanear(int sda, int scl) {
  Wire.end();
  Wire.begin(sda, scl);
  Wire.setClock(100000);
  int n = 0;
  for (uint8_t dir = 1; dir < 127; dir++) {
    Wire.beginTransmission(dir);
    if (Wire.endTransmission() == 0) {
      Serial.printf("    Encontrado: 0x%02X", dir);
      if (dir == 0x0D) Serial.print("  -> QMC5883L (lo que busca robot_completo)");
      if (dir == 0x1E) Serial.print("  -> HMC5883L (lo que busca robot_completo)");
      if (dir == 0x2C) Serial.print("  -> QMC5883P (clon nuevo, NO compatible con robot_completo)");
      if (dir == 0x68) Serial.print("  -> MPU6050");
      Serial.println();
      n++;
    }
  }
  return n;
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\nEscaner I2C");
}

void loop() {
  // Prueba de continuidad: el ESP32 tira cada pin hacia abajo con una resistencia debil.
  // Si SDA/SCL del modulo estan bien conectados, las resistencias del modulo lo suben (ALTO).
  // Si el cable o la soldadura no hacen contacto, queda en BAJO.
  Wire.end();
  pinMode(PIN_A, INPUT_PULLDOWN);
  pinMode(PIN_B, INPUT_PULLDOWN);
  delay(10);
  bool a = digitalRead(PIN_A), b = digitalRead(PIN_B);
  Serial.printf("Continuidad: GPIO8=%s  GPIO9=%s\n", a ? "ALTO (conecta con el modulo)" : "BAJO (sin contacto)",
                b ? "ALTO (conecta con el modulo)" : "BAJO (sin contacto)");
  pinMode(PIN_A, INPUT);
  pinMode(PIN_B, INPUT);

  Serial.println("  Prueba normal (SDA=GPIO8, SCL=GPIO9):");
  int n1 = escanear(PIN_A, PIN_B);
  if (n1 == 0) Serial.println("    nada");

  Serial.println("  Prueba cruzada (SDA=GPIO9, SCL=GPIO8):");
  int n2 = escanear(PIN_B, PIN_A);
  if (n2 == 0) Serial.println("    nada");

  if (n1 > 0) Serial.println("  => CORRECTO: los cables estan bien (SDA en 8, SCL en 9).");
  else if (n2 > 0) Serial.println("  => CRUZADOS: intercambien los cables de SDA y SCL en el ESP32.");
  else Serial.println("  => No responde en ninguna: revisar GND, soldaduras o modulo danado.");
  Serial.println("---");
  delay(2000);
}
