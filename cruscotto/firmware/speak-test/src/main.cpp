// Prova U1 / P6 "Speak" 0.1.1 — Cruscotto C3+AI (D-026, D-028).
// Tono 200 Hz per 10 s su IO17, poi su IO18, poi pausa: si misura P6 in V~.
#include <Arduino.h>

#include "board_8048s050.h"

namespace {
constexpr char kVersion[] = "0.1.1";
constexpr int kSdCs = 10;           // MicroSD esclusa (fonte comunitaria)
constexpr int kChannel = 0;
constexpr uint32_t kToneHz = 200;  // 0.1.1: entro la banda V~ di un tester comune
constexpr uint32_t kPhaseMs = 10000;
constexpr int kPins[] = {17, 18};

void idle(int pin) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

void phase(const char* name, int pin) {
  Serial.printf("speak_test version=%s fase=%s uptime_ms=%lu\n", kVersion, name, millis());
  if (pin >= 0) {
    ledcSetup(kChannel, kToneHz, 8);
    ledcAttachPin(pin, kChannel);
    ledcWrite(kChannel, 128);  // onda quadra 50%
  }
  delay(kPhaseMs);
  if (pin >= 0) {
    ledcWrite(kChannel, 0);
    ledcDetachPin(pin);
    idle(pin);
  }
}
}  // namespace

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(board::kBacklight, OUTPUT);
  digitalWrite(board::kBacklight, LOW);
  pinMode(kSdCs, OUTPUT);
  digitalWrite(kSdCs, HIGH);
  for (int pin : kPins) idle(pin);
}

void loop() {
  phase("TONO_IO17", 17);
  phase("TONO_IO18", 18);
  phase("PAUSA", -1);
}
