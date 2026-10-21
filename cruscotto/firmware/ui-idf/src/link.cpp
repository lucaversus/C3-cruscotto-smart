// Collegamento UART con il front-end e sorgente simulata in loopback (D-029, D-037).
#include "link.h"

#include <cmath>
#include <cstring>

#include "driver/uart.h"
#include "esp_timer.h"
#include "fe_link.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
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
  for (uint8_t i = 0; felink::getSignal(f, i, s); ++i) store.put(s.id, s.quality, s.value, nowUs);
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
    felink::addSignal(f, felink::sig::kRpm, q, 800.0f + 1900.0f * (1.0f + sinf(t * 1.3f)));
    felink::addSignal(f, felink::sig::kSpeedKmh, q, 50.0f + 40.0f * sinf(t * 0.3f));
    felink::addSignal(f, felink::sig::kCoolantC, q, 85.0f + 10.0f * sinf(t * 0.2f));
    felink::addSignal(f, felink::sig::kBatteryV, q, 13.9f + 0.3f * sinf(t * 0.7f));
    felink::addSignal(f, felink::sig::kIgnition, q, 1.0f);
    felink::addSignal(f, felink::sig::kAccelX, q, 0.2f * sinf(t * 0.9f));
    felink::addSignal(f, felink::sig::kNtcDisplayC, q, 38.0f + 2.0f * sinf(t * 0.05f));
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
