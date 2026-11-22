// Busca un modulo I2C probando los pares de pines libres del ESP32-S3.
// Cada hallazgo se VERIFICA leyendo el registro de identidad del chip (evita falsos positivos).
// Se excluyen GPIO 17 y 18 (HC-SR04) y los de motores. Monitor Serie a 115200.
#include <Wire.h>

const int PINES[] = {1, 2, 8, 9, 10, 11, 12, 13, 14, 21, 38, 39, 40, 41, 42, 47, 48};
const int N = sizeof(PINES) / sizeof(PINES[0]);

// Lee un registro de 1 byte; devuelve -1 si falla
int leerReg(uint8_t dir, uint8_t reg) {
  Wire.beginTransmission(dir);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return -1;
  if (Wire.requestFrom((int)dir, 1) != 1) return -1;
  return Wire.read();
}

void loop() {
  int hallados = 0;
  for (int i = 0; i < N; i++) {
    for (int j = 0; j < N; j++) {
      if (i == j) continue;
      Wire.end();
      if (!Wire.begin(PINES[i], PINES[j])) continue;
      Wire.setClock(100000);
      Wire.setTimeOut(5);
      int id;
      id = leerReg(0x68, 0x75);                         // MPU6050: WHO_AM_I = 0x68 (o 0x70-0x73 en clones)
      if (id == 0x68 || (id >= 0x70 && id <= 0x73)) {
        Serial.printf("  CONFIRMADO MPU6050 (0x68, id 0x%02X) con SDA=GPIO%d, SCL=GPIO%d\n", id, PINES[i], PINES[j]);
        hallados++;
      }
      id = leerReg(0x0D, 0x0D);                         // QMC5883L: registro de ID = 0xFF
      if (id == 0xFF) {
        Serial.printf("  CONFIRMADO QMC5883L (0x0D) con SDA=GPIO%d, SCL=GPIO%d\n", PINES[i], PINES[j]);
        hallados++;
      }
      id = leerReg(0x1E, 0x0A);                         // HMC5883L: registro de ID A = 'H' (0x48)
      if (id == 0x48) {
        Serial.printf("  CONFIRMADO HMC5883L (0x1E) con SDA=GPIO%d, SCL=GPIO%d\n", PINES[i], PINES[j]);
        hallados++;
      }
      id = leerReg(0x2C, 0x00);                         // QMC5883P: chip ID = 0x80
      if (id == 0x80) {
        Serial.printf("  CONFIRMADO QMC5883P (0x2C, no compatible) con SDA=GPIO%d, SCL=GPIO%d\n", PINES[i], PINES[j]);
        hallados++;
      }
    }
  }
  if (hallados == 0) Serial.println("  Nada confirmado en ningun par: el modulo no esta recibiendo alimentacion/GND o esta danado.");
  Serial.println("--- fin de la busqueda ---");
  delay(3000);
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  Serial.println("\nBuscando y verificando el modulo (sin GPIO17/18)...");
}
