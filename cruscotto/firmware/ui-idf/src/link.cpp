// Collegamento UART con il front-end e sorgente simulata in loopback (D-029, D-037).
#include "link.h"

#include <cmath>
#include <cstring>

#include "driver/uart.h"
#include "esp_timer.h"
#include "fe_link.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "blackbox.h"
#include "labels.h"
#include "signal_store.h"

namespace {
constexpr uart_port_t kUart = UART_NUM_1;
constexpr int kTxPin = 12;  // P2 IO12 -> front-end GPIO33
constexpr int kRxPin = 11;  // P2 IO11 <- front-end GPIO25
constexpr int kBaud = 921600;

portMUX_TYPE statsLock = portMUX_INITIALIZER_UNLOCKED;
LinkStats stats;
SignalStore store;

void handleFrame(const felink::Frame& f, int64_t nowUs) {
  static bool haveSeq = false;
  static uint8_t lastSeq = 0;
  portENTER_CRITICAL(&statsLock);
  ++stats.frames;
  stats.lastFrameUs = nowUs;
  if (haveSeq) stats.lostSeq += static_cast<uint8_t>(f.seq - lastSeq - 1);
  portEXIT_CRITICAL(&statsLock);
  haveSeq = true;
  lastSeq = f.seq;
  if (f.type != felink::Type::kSignals) return;  // altri tipi: compiti successivi (D-037)
  felink::Signal s{};
  for (uint8_t i = 0; felink::getSignal(f, i, s); ++i) {
    store.put(s.id, s.quality, s.value, nowUs);
    blackbox::record(s.id, s.quality, s.value, nowUs);
    if (s.id == felink::sig::kStalkButtons) labels::onStalkButtons(s.value, nowUs);
  }
}

void rxTask(void*) {
  felink::Decoder decoder;
  felink::Frame frame;
  uint8_t buf[256];
  uint32_t reportedErrors = 0;
  while (true) {
    const int n = uart_read_bytes(kUart, buf, sizeof buf, pdMS_TO_TICKS(20));
    for (int i = 0; i < n; ++i) {
      if (decoder.push(buf[i], frame)) handleFrame(frame, esp_timer_get_time());
    }
    if (decoder.errors() != reportedErrors) {
      reportedErrors = decoder.errors();
      portENTER_CRITICAL(&statsLock);
      stats.errors = reportedErrors;
      portEXIT_CRITICAL(&statsLock);
    }
  }
}

// Sorgente simulata: valori sinusoidali con qualità "simulato", inviati come farebbe il
// front-end. Passano dalla UART reale in loopback, dal decodificatore e dall'archivio.
void simTask(void*) {
  uint8_t seq = 0;
  uint8_t wire[felink::kMaxEncoded];
  int64_t lastHeartbeat = 0;
  while (true) {
    const int64_t now = esp_timer_get_time();
    const float t = now / 1e6f;
    felink::Frame f;
    f.type = felink::Type::kSignals;
    f.seq = seq++;
    f.timeUs = static_cast<uint32_t>(now);
    const auto q = felink::Quality::kSimulated;
    felink::addSignal(f, felink::sig::kRpm, q, 800.0f + 1950.0f * (1.0f + sinf(t * 0.6f)));
    felink::addSignal(f, felink::sig::kSpeedKmh, q, 50.0f + 40.0f * sinf(t * 0.3f));
    // Acqua da 30 a 115 °C in 2 minuti: mostra bianco, azzurro, rosso e l'avviso.
    felink::addSignal(f, felink::sig::kCoolantC, q, 72.5f - 42.5f * cosf(t * 0.0524f));
    felink::addSignal(f, felink::sig::kOutsideC, q, 14.0f);
    felink::addSignal(f, felink::sig::kCabinC, q, 21.0f + 0.5f * sinf(t * 0.05f));
    const float rpmSim = 800.0f + 1950.0f * (1.0f + sinf(t * 0.6f));
    felink::addSignal(f, felink::sig::kFuelL100, q, 3.0f + (rpmSim - 800.0f) / 400.0f);
    // Gasolio dal 60 al 5 % in 5 minuti, poi di nuovo pieno: mostra la riserva.
    const float fuel = 60.0f - 55.0f * fmodf(t, 300.0f) / 300.0f;
    felink::addSignal(f, felink::sig::kFuelPct, q, fuel);
    // Luci e spie simulate: freccia sinistra 10 s ogni 40 s, candelette nei primi 8 s,
    // pressione olio 5 s ogni 120 s (dopo 60 s) per provare il riquadro degli avvisi.
    const bool blink = fmodf(t, 0.8f) < 0.4f;
    const uint32_t lights = (fmodf(t, 40.0f) < 10.0f && blink ? 1u : 0u) | (1u << 2);
    const uint32_t warnings = (t < 8.0f ? 1u << 4 : 0u) | (t > 60.0f && fmodf(t - 60.0f, 120.0f) < 5.0f ? 1u << 1 : 0u) |
                              (fuel <= 10.0f ? 1u << 9 : 0u);
    felink::addSignal(f, felink::sig::kLightsFlags, q, static_cast<float>(lights));
    felink::addSignal(f, felink::sig::kWarningFlags, q, static_cast<float>(warnings));
    felink::addSignal(f, felink::sig::kBatteryV, q, 13.9f + 0.3f * sinf(t * 0.7f));
    felink::addSignal(f, felink::sig::kIgnition, q, 1.0f);
    felink::addSignal(f, felink::sig::kAccelX, q, 0.2f * sinf(t * 0.9f));
    felink::addSignal(f, felink::sig::kNtcDisplayC, q, 38.0f + 2.0f * sinf(t * 0.05f));
    // Pressione lunga simulata di un comando al volante: 2,5 s ogni 90 s (dopo 30 s dall'avvio).
    const float phase = fmodf(t - 30.0f, 90.0f);
    felink::addSignal(f, felink::sig::kStalkButtons, q, (t > 30.0f && phase < 2.5f) ? 1.0f : 0.0f);
    uart_write_bytes(kUart, wire, felink::encode(f, wire));
    if (now - lastHeartbeat >= 1000000) {
      lastHeartbeat = now;
      felink::Frame hb;
      hb.type = felink::Type::kHeartbeat;
      hb.seq = seq++;
      hb.timeUs = static_cast<uint32_t>(now);
      uart_write_bytes(kUart, wire, felink::encode(hb, wire));
    }
    vTaskDelay(pdMS_TO_TICKS(33));
  }
}
}  // namespace

SignalStore& signalStore() { return store; }

void linkStart(bool simulate) {
  uart_config_t cfg = {};
  cfg.baud_rate = kBaud;
  cfg.data_bits = UART_DATA_8_BITS;
  cfg.parity = UART_PARITY_DISABLE;
  cfg.stop_bits = UART_STOP_BITS_1;
  cfg.flow_ctrl = UART_HW_FLOWCTRL_DISABLE;
  cfg.source_clk = UART_SCLK_DEFAULT;
  ESP_ERROR_CHECK(uart_driver_install(kUart, 4096, 4096, 0, nullptr, 0));
  ESP_ERROR_CHECK(uart_param_config(kUart, &cfg));
  ESP_ERROR_CHECK(uart_set_pin(kUart, kTxPin, kRxPin, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE));
  stats.simulated = simulate;
  if (simulate) ESP_ERROR_CHECK(uart_set_loop_back(kUart, true));
  xTaskCreatePinnedToCore(rxTask, "link_rx", 4096, nullptr, 6, nullptr, 0);
  if (simulate) xTaskCreatePinnedToCore(simTask, "link_sim", 4096, nullptr, 4, nullptr, 0);
}

LinkStats linkStats() {
  portENTER_CRITICAL(&statsLock);
  const LinkStats copy = stats;
  portEXIT_CRITICAL(&statsLock);
  return copy;
}

bool linkAlive(int64_t nowUs) {
  const LinkStats s = linkStats();
  return s.lastFrameUs != 0 && nowUs - s.lastFrameUs < 3000000;
}
