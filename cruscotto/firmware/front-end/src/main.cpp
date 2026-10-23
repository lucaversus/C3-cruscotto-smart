// Front-end del cruscotto C3+AI 0.1.0 (D-029): ESP32 che raccoglie i dati dell'auto e li
// manda all'S3 con il protocollo fe_link v1 (cruscotto/docs/protocollo-fe-s3.md).
// Prima versione: solo il collegamento reale verso l'S3, con dati simulati (qualità
// "simulato"); K-line, VAN e sensori si aggiungeranno riusando il codice del logger.
#include <Arduino.h>

#include "fe_link.h"

namespace {
constexpr char kVersion[] = "0.1.0";
constexpr int kTxPin = 25;  // verso S3 P2 IO11 (RX dell'S3)
constexpr int kRxPin = 33;  // da S3 P2 IO12 (TX dell'S3)
constexpr uint32_t kBaud = 921600;
constexpr uint32_t kSignalsMs = 33, kHeartbeatMs = 1000, kReportMs = 5000;

HardwareSerial s3link(1);
felink::Decoder decoder;
uint8_t seq = 0;
uint32_t sentFrames = 0, receivedFrames = 0;

void send(felink::Frame& f) {
  static uint8_t wire[felink::kMaxEncoded];
  f.seq = seq++;
  f.timeUs = static_cast<uint32_t>(esp_timer_get_time());
  const size_t n = felink::encode(f, wire);
  if (n) {
    s3link.write(wire, n);
    ++sentFrames;
  }
}

// Stessi andamenti del simulatore interno dell'S3, così le pagine si possono confrontare.
void sendSignals() {
  const float t = esp_timer_get_time() / 1e6f;
  const auto q = felink::Quality::kSimulated;
  felink::Frame f;
  f.type = felink::Type::kSignals;
  const float rpm = 800.0f + 1950.0f * (1.0f + sinf(t * 0.6f));
  felink::addSignal(f, felink::sig::kRpm, q, rpm);
  felink::addSignal(f, felink::sig::kSpeedKmh, q, 50.0f + 40.0f * sinf(t * 0.3f));
  felink::addSignal(f, felink::sig::kCoolantC, q, 72.5f - 42.5f * cosf(t * 0.0524f));
  felink::addSignal(f, felink::sig::kOutsideC, q, 14.0f);
  felink::addSignal(f, felink::sig::kCabinC, q, 21.0f + 0.5f * sinf(t * 0.05f));
  felink::addSignal(f, felink::sig::kFuelL100, q, 3.0f + (rpm - 800.0f) / 400.0f);
  felink::addSignal(f, felink::sig::kFuelPct, q, 60.0f - 55.0f * fmodf(t, 300.0f) / 300.0f);
  felink::addSignal(f, felink::sig::kBatteryV, q, 13.9f + 0.3f * sinf(t * 0.7f));
  felink::addSignal(f, felink::sig::kIgnition, q, 1.0f);
  felink::addSignal(f, felink::sig::kAccelX, q, 0.2f * sinf(t * 0.9f));
  felink::addSignal(f, felink::sig::kNtcDisplayC, q, 38.0f + 2.0f * sinf(t * 0.05f));
  const bool blink = fmodf(t, 0.8f) < 0.4f;
  const uint32_t lights = (fmodf(t, 40.0f) < 10.0f && blink ? 1u : 0u) | (fmodf(t, 60.0f) >= 40.0f ? 1u << 2 : 0u);
  const uint32_t warnings = (t < 8.0f ? 1u << 4 : 0u) | (t > 60.0f && fmodf(t - 60.0f, 120.0f) < 5.0f ? 1u << 1 : 0u);
  felink::addSignal(f, felink::sig::kLightsFlags, q, static_cast<float>(lights));
  felink::addSignal(f, felink::sig::kWarningFlags, q, static_cast<float>(warnings));
  send(f);
}
}  // namespace

void setup() {
  Serial.begin(115200);
  s3link.begin(kBaud, SERIAL_8N1, kRxPin, kTxPin);
  Serial.printf("\nc3_front_end version=%s link=UART1 tx=%d rx=%d baud=%lu dati=simulati\n", kVersion, kTxPin, kRxPin,
                static_cast<unsigned long>(kBaud));
}

void loop() {
  static uint32_t lastSignals = 0, lastHeartbeat = 0, lastReport = 0;
  const uint32_t now = millis();
  if (now - lastSignals >= kSignalsMs) {
    lastSignals = now;
    sendSignals();
  }
  if (now - lastHeartbeat >= kHeartbeatMs) {
    lastHeartbeat = now;
    felink::Frame hb;
    hb.type = felink::Type::kHeartbeat;
    send(hb);
  }
  // Trame dall'S3 (comandi, conferme): per ora solo conteggio.
  felink::Frame in;
  while (s3link.available()) {
    if (decoder.push(static_cast<uint8_t>(s3link.read()), in)) ++receivedFrames;
  }
  if (now - lastReport >= kReportMs) {
    lastReport = now;
    Serial.printf("c3_front_end sent=%lu received=%lu rx_errors=%lu uptime_ms=%lu\n", static_cast<unsigned long>(sentFrames),
                  static_cast<unsigned long>(receivedFrames), static_cast<unsigned long>(decoder.errors()),
                  static_cast<unsigned long>(now));
  }
}
