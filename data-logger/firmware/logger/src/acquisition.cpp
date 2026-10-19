#include "acquisition.h"
#include "logger_logic.h"
#include <driver/rmt.h>
#include <esp_timer.h>
#include <freertos/ringbuf.h>

CaptureStatus capture;
namespace {
void sleepUntilStop(uint32_t ms) {
  const uint32_t begin = millis();
  while (!capture.stop && !logger::elapsed(millis(), begin, ms)) vTaskDelay(1);
}

void vanTask(void *) {
  rmt_config_t config{};
  config.rmt_mode = RMT_MODE_RX;
  config.channel = RMT_CHANNEL_0;
  config.gpio_num = static_cast<gpio_num_t>(logger::kVanRx);
  config.clk_div = 80; // One microsecond per tick on the original ESP32.
  config.mem_block_num = 4;
  config.rx_config.filter_en = false;
  config.rx_config.idle_threshold = LOGGER_VAN_BODY ? 160 : 80;
  bool installed = false;
  RingbufHandle_t ring = nullptr;
  esp_err_t error = rmt_config(&config);
  if (error == ESP_OK) {
    error = rmt_driver_install(config.channel, 16384, 0);
    installed = error == ESP_OK;
  }
  if (error == ESP_OK) error = rmt_get_ringbuf_handle(config.channel, &ring);
  if (error == ESP_OK) error = rmt_rx_start(config.channel, true);
  if (error != ESP_OK || !ring) {
    systemRecord("van_start_failed", static_cast<uint32_t>(error));
  } else {
    capture.vanReady = true;
    bool hardwareStopped = false;
    for (;;) {
      if (capture.stop && !hardwareStopped) {
        rmt_rx_stop(config.channel); hardwareStopped = true;
      }
      size_t bytes = 0;
      auto *items = static_cast<rmt_item32_t *>(xRingbufferReceive(ring, &bytes, hardwareStopped ? 0 : 1));
      if (!items) {
        if (hardwareStopped) break;
        vTaskDelay(1); continue;
      }
      Record row{};
      row.source = Source::Van;
      row.monoUs = esp_timer_get_time(); // Delivery timestamp, not an ISR/SOF timestamp.
      row.frame = ++capture.vanFrames;
      logger::VanDecoder decoded{};
      for (size_t i = 0; i < bytes / sizeof(*items); ++i) {
        decoded.pulse(items[i].level0, items[i].duration0, LOGGER_VAN_BODY ? 16 : 8, LOGGER_VAN_INVERT);
        decoded.pulse(items[i].level1, items[i].duration1, LOGGER_VAN_BODY ? 16 : 8, LOGGER_VAN_INVERT);
      }
      row.length = static_cast<uint8_t>(decoded.length);
      memcpy(row.raw, decoded.data, row.length);
      const bool crc = logger::vanCrcOk(row.raw, row.length);
      row.event = decoded.overflow ? "overflow" : decoded.timingError ? "timing_error" : crc ? "crc_ok" : "crc_bad";
      if (row.length >= 3) row.id = (row.raw[1] << 4) | (row.raw[2] >> 4);
      if (!crc || decoded.overflow || decoded.timingError) ++capture.vanBad;
      submitRecord(row); // Preserve invalid/unknown frames as well as valid ones.
      vRingbufferReturnItem(ring, items);
    }
  }
  if (installed) rmt_driver_uninstall(config.channel);
  capture.vanReady = false; capture.vanDone = true;
  vTaskDelete(nullptr);
}

HardwareSerial kwp(2);
uint8_t ecu = 0;
uint32_t kwpNumber = 0;

void rawKwp(Source source, const char *event, const uint8_t *bytes, size_t count, int64_t at) {
  const uint32_t frame = ++kwpNumber;
  for (size_t offset = 0; offset < count; offset += sizeof(Record::raw)) {
    Record row{}; row.source = source; row.event = event; row.monoUs = at;
    row.frame = frame; row.offset = offset; row.length = min(sizeof(row.raw), count - offset);
    memcpy(row.raw, bytes + offset, row.length);
    submitRecord(row);
  }
}

bool sendKwp(uint8_t service, uint8_t pid, bool init) {
  if (capture.stop) return false;
  const uint8_t length = init ? 1 : 2;
  uint8_t frame[] = {static_cast<uint8_t>((init ? 0xc0 : 0x80) | length),
                     static_cast<uint8_t>(init ? 0x33 : ecu), 0xf1, service, pid, 0};
  const size_t size = length + 4;
  frame[size - 1] = logger::checksum(frame, size - 1);
  uint8_t leftover[64]; size_t leftoverCount = 0;
  while (kwp.available() && leftoverCount < sizeof(leftover)) leftover[leftoverCount++] = kwp.read();
  if (leftoverCount) rawKwp(Source::KwpRx, "unsolicited", leftover, leftoverCount, esp_timer_get_time());
  if (kwp.available()) { ++capture.kwpErrors; return false; }
  const int64_t at = esp_timer_get_time();
  size_t sent = 0;
  bool echoed = true;
  // Finish an already-started request; STOP forbids the next request. At most six bytes.
  for (; sent < size; ++sent) {
    if (kwp.write(frame[sent]) != 1) break;
    kwp.flush(true);
    const uint32_t began = millis();
    while (!kwp.available() && !logger::elapsed(millis(), began, 20)) vTaskDelay(1);
    if (!kwp.available() || kwp.read() != frame[sent]) { ++sent; echoed = false; break; }
    vTaskDelay(pdMS_TO_TICKS(5)); // P4 inter-byte delay, must be measured on actual interface.
  }
  rawKwp(Source::KwpTx, echoed && sent == size ? "tx_echo_ok" : "tx_echo_error", frame, sent, at);
  if (!echoed || sent != size) { ++capture.kwpErrors; return false; }
  return true;
}

bool decodedPid(uint8_t pid, const uint8_t *data, size_t n, Record &row) {
  if (!n) return false;
  const unsigned ab = n >= 2 ? (data[0] << 8) | data[1] : 0;
  switch (pid) {
    case 0x04: case 0x11: case 0x2f: row.value = data[0] * 100.0f / 255; row.unit = "percent"; break;
    case 0x05: case 0x0f: case 0x46: case 0x5c: row.value = int(data[0]) - 40; row.unit = "degC"; break;
    case 0x0b: case 0x33: row.value = data[0]; row.unit = "kPa_abs"; break;
    case 0x0c: if (n < 2) return false; row.value = ab / 4.0f; row.unit = "rpm"; break;
    case 0x0d: row.value = data[0]; row.unit = "km_h"; break;
    case 0x10: if (n < 2) return false; row.value = ab / 100.0f; row.unit = "g_s"; break;
    case 0x23: if (n < 2) return false; row.value = ab * 10.0f; row.unit = "kPa"; break;
    case 0x42: if (n < 2) return false; row.value = ab / 1000.0f; row.unit = "V"; break;
    default: return false; // Unknown PIDs remain in the raw response, never guessed.
  }
  return true;
}

bool receiveKwp(bool init, uint8_t pid, uint8_t *bitmap) {
  uint8_t bytes[260] = {}; size_t count = 0;
  uint32_t start = millis(), lastByte = start;
  int64_t at = 0;
  bool accepted = false;
  auto process = [&]() {
    if (!count) return;
    const logger::KwpFrame frame = logger::parseKwp(bytes, count);
    rawKwp(Source::KwpRx, frame.valid ? "checksum_ok" : "invalid_frame", bytes, count, at);
    ++capture.kwpFrames;
    if (!frame.valid) { ++capture.kwpErrors; return; }
    if (frame.target != 0xf1) return;
    const uint8_t *p = bytes + frame.offset;
    if (init && frame.length >= 3 && p[0] == 0xc1) { ecu = frame.source; accepted = true; }
    if (!init && frame.source == ecu && frame.length >= 2 && p[0] == 0x41 && p[1] == pid) {
      if (bitmap) {
        if (frame.length < 6) return;
        memcpy(bitmap, p + 2, 4);
      }
      Record row{}; row.source = Source::ObdPid; row.monoUs = at;
      row.id = (ecu << 8) | pid;
      if (decodedPid(pid, p + 2, frame.length - 2, row)) { row.event = "decoded"; submitRecord(row); }
      accepted = true;
    }
  };
  // Drain the response to an already-sent request before acknowledging STOP.
  while (!logger::elapsed(millis(), start, 800)) {
    if (kwp.available()) {
      if (!count) at = esp_timer_get_time();
      bytes[count++] = kwp.read(); lastByte = millis();
      const auto f = logger::parseKwp(bytes, count);
      if (f.complete || count == sizeof(bytes)) { process(); count = 0; }
    } else {
      if (count && logger::elapsed(millis(), lastByte, 25)) { process(); count = 0; }
      if (accepted && logger::elapsed(millis(), lastByte, 60)) break;
      vTaskDelay(1);
    }
  }
  if (count) process();
  return accepted;
}

void releaseKline() {
  kwp.end(); pinMode(logger::kKwpTx, OUTPUT); digitalWrite(logger::kKwpTx, LOW);
  capture.kwpConnected = false;
}
bool connectKwp() {
  releaseKline(); sleepUntilStop(300);
  if (capture.stop) return false;
  // NPN inversion: GPIO HIGH pulls the vehicle line LOW.
  digitalWrite(logger::kKwpTx, HIGH); sleepUntilStop(25);
  digitalWrite(logger::kKwpTx, LOW); sleepUntilStop(25);
  if (capture.stop) return false;
  kwp.setRxBufferSize(2048);
  kwp.begin(10400, SERIAL_8N1, logger::kKwpRx, logger::kKwpTx, true);
  kwp.setRxInvert(false); // Only TX is inverted, per the discrete interface.
  return sendKwp(0x81, 0, true) && receiveKwp(true, 0, nullptr);
}
void kwpTask(void *) {
  while (!capture.stop) {
    if (!connectKwp()) { ++capture.kwpErrors; systemRecord("kwp_init_failed"); sleepUntilStop(5000); continue; }
    capture.kwpConnected = true; systemRecord("kwp_connected", ecu);
    bool supported[256] = {};
    bool discovered = true;
    for (unsigned block = 0; block <= 0xe0 && !capture.stop; block += 32) {
      uint8_t bitmap[4] = {};
      sleepUntilStop(100);
      if (!sendKwp(0x01, block, false) || !receiveKwp(false, block, bitmap)) { discovered = false; break; }
      for (unsigned pid = block + 1; pid <= block + 32 && pid < 256; ++pid)
        supported[pid] = logger::pidSupported(bitmap, block, pid);
      if (!(bitmap[3] & 1)) break;
    }
    if (!discovered) { ++capture.kwpErrors; systemRecord("pid_discovery_failed"); releaseKline(); sleepUntilStop(5000); continue; }
    unsigned errors = 0;
    bool any = false;
    for (unsigned pid = 1; pid < 256; ++pid) any |= logger::isLivePid(supported, pid);
    if (!any) { systemRecord("no_live_pids"); releaseKline(); sleepUntilStop(5000); continue; }
    auto poll = [&](unsigned pid) {
      sleepUntilStop(logger::kKwpRequestGapMs);
      if (capture.stop) return;
      if (sendKwp(0x01, pid, false) && receiveKwp(false, pid, nullptr)) errors = 0;
      else { ++errors; ++capture.kwpErrors; systemRecord("pid_timeout", (ecu << 8) | pid); }
    };
    unsigned slowCursor = 0;
    while (!capture.stop && errors < 3) {
      for (uint8_t pid : logger::kPriorityPids)
        if (!capture.stop && errors < 3 && logger::isLivePid(supported, pid)) poll(pid);
      const unsigned slow = logger::nextSlowPid(supported, slowCursor);
      if (slow && !capture.stop && errors < 3) { slowCursor = slow; poll(slow); }
    }
    releaseKline();
  }
  releaseKline(); capture.kwpDone = true;
  vTaskDelete(nullptr);
}
} // namespace

bool startAcquisition() {
  if (LOGGER_ENABLE_VAN) {
    capture.vanDone = false;
    if (xTaskCreatePinnedToCore(vanTask, "van_rx", 4096, nullptr, 3, nullptr, 0) != pdPASS) {
      capture.vanDone = true; systemRecord("van_task_failed"); return false;
    }
  }
  if (LOGGER_ENABLE_KWP) {
    capture.kwpDone = false;
    if (xTaskCreatePinnedToCore(kwpTask, "kwp_rx", 6144, nullptr, 2, nullptr, 0) != pdPASS) {
      capture.kwpDone = true; systemRecord("kwp_task_failed"); return false;
    }
  }
  return true;
}
