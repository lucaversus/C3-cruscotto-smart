#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <esp_timer.h>
#include <inttypes.h>
#include "calendar.h"
#include "config.h"

// Bench logger only. No vehicle bus, radio, OLED, buttons or RTC clock writes.
namespace {
constexpr char kHeader[] = "schema_version,source,sequence,uptime_us,rtc_state,rtc_calendar,heap_free_bytes,heap_min_bytes,missed_intervals\n";
SPIClass sdSpi(VSPI);
bool wireReady = false, sdReady = false;
const char *rtcState = "not_read";
const char *sdState = "not_started";
char rtcCalendar[32] = {};
char sessionPath[32] = {};
uint64_t rowsWritten = 0, missedIntervals = 0, writeErrors = 0;
uint32_t lastSampleMs = 0, lastStatusMs = 0, lastRetryMs = 0;

bool readRtcRegisters(uint8_t reg, uint8_t *data, size_t count) {
  if (!wireReady) return false;
  Wire.beginTransmission(logger::kRtcAddress);
  Wire.write(reg); // Only the register pointer is written, never a register value.
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(logger::kRtcAddress, count, true) != count) return false;
  for (size_t i = 0; i < count; ++i) data[i] = static_cast<uint8_t>(Wire.read());
  return true;
}

void pollRtc() {
  rtcCalendar[0] = '\0';
  uint8_t status = 0, raw[7] = {};
  if (!readRtcRegisters(0x0f, &status, 1) || !readRtcRegisters(0x00, raw, 7)) {
    rtcState = "unavailable";
    return;
  }
  if (status & 0x80) { // Oscillator Stop Flag; do not silently clear it.
    rtcState = "oscillator_stop";
    return;
  }
  logger::Calendar c{};
  if (!logger::decodeCalendar(raw, c)) {
    rtcState = "invalid_calendar";
    return;
  }
  const int calendarLength = snprintf(rtcCalendar, sizeof(rtcCalendar), "%04u-%02u-%02uT%02u:%02u:%02u",
           static_cast<unsigned>(c.year), static_cast<unsigned>(c.month),
           static_cast<unsigned>(c.day), static_cast<unsigned>(c.hour),
           static_cast<unsigned>(c.minute), static_cast<unsigned>(c.second));
  if (calendarLength != 19) {
    rtcCalendar[0] = '\0';
    rtcState = "invalid_calendar";
    return;
  }
  rtcState = "calendar_ok"; // Not a UTC/synchronization guarantee.
}

void storageFailed(const char *reason) {
  sdReady = false;
  sdState = reason;
  SD.end();
  sessionPath[0] = '\0';
  lastRetryMs = millis();
  Serial.printf("storage state=%s retry_ms=%lu\n", reason,
                static_cast<unsigned long>(logger::kRetryMs));
}

// Arduino FS flush/close do not expose durable-commit errors. This checks byte
// count and stream errors, not power-loss safety or physical media persistence.
bool writeAndClose(File &file, const char *data, size_t length) {
  const size_t written = file.write(reinterpret_cast<const uint8_t *>(data), length);
  file.flush();
  const bool ok = written == length && file.getWriteError() == 0;
  file.close();
  return ok;
}

void startSession() {
  SD.end();
  // format_if_empty=false: never format a user's card automatically.
  if (!SD.begin(logger::kSdCs, sdSpi, logger::kSpiHz, "/sd", 1, false) ||
      SD.cardType() == CARD_NONE) {
    storageFailed("mount_failed");
    return;
  }
  // New, bounded file namespace; never truncate an existing recording.
  for (unsigned index = 1; index <= 9999; ++index) {
    snprintf(sessionPath, sizeof(sessionPath), "/bench_%04u.csv", index);
    if (SD.exists(sessionPath)) continue;
    File file = SD.open(sessionPath, FILE_WRITE);
    if (!file || !writeAndClose(file, kHeader, sizeof(kHeader) - 1)) {
      ++writeErrors;
      storageFailed("header_failed");
      return;
    }
    sdReady = true;
    sdState = "recording";
    Serial.printf("session file=%s source=bench_esp32 vehicle=disabled\n", sessionPath);
    return;
  }
  storageFailed("namespace_full");
}

void recordSample() {
  if (!sdReady) return;
  // Do not recreate a removed session with a headerless CSV.
  if (!SD.exists(sessionPath)) {
    ++writeErrors;
    storageFailed("session_missing");
    return;
  }
  char row[224];
  const int length = snprintf(row, sizeof(row),
      "1,bench_esp32,%" PRIu64 ",%" PRId64 ",%s,%s,%u,%u,%" PRIu64 "\n",
      rowsWritten + 1, esp_timer_get_time(), rtcState, rtcCalendar,
      ESP.getFreeHeap(), ESP.getMinFreeHeap(), missedIntervals);
  if (length <= 0 || static_cast<size_t>(length) >= sizeof(row)) {
    ++writeErrors;
    storageFailed("row_overflow");
    return;
  }
  File file = SD.open(sessionPath, FILE_APPEND);
  if (!file || !writeAndClose(file, row, static_cast<size_t>(length))) {
    ++writeErrors;
    storageFailed("write_failed");
    return;
  }
  ++rowsWritten;
}

void printStatus() {
  Serial.printf("status uptime_us=%" PRId64 " sd=%s rtc=%s rows=%" PRIu64
                " write_errors=%" PRIu64 " missed_intervals=%" PRIu64
                " heap_free_bytes=%u file=%s\n",
                esp_timer_get_time(), sdState, rtcState, rowsWritten,
                writeErrors, missedIntervals, ESP.getFreeHeap(),
                sessionPath[0] ? sessionPath : "none");
}
} // namespace

void setup() {
  Serial.begin(115200);
  delay(250);
  Serial.println("\nc3_datalogger version=0.2.0 mode=bench_health auto_start=1");
  Serial.println("vehicle=disabled oled=disabled buttons=disabled rtc_write=disabled");
  Serial.println("commands: h=help s=status; RTC calendar has no assumed timezone");
  wireReady = Wire.begin(logger::kSda, logger::kScl, 100000);
  Wire.setTimeOut(50);
  sdSpi.begin(logger::kSck, logger::kMiso, logger::kMosi, logger::kSdCs);
  pollRtc();
  startSession();
  const uint32_t now = millis();
  lastRetryMs = lastSampleMs = lastStatusMs = now;
  printStatus();
}

void loop() {
  for (unsigned count = 0; count < 32 && Serial.available() > 0; ++count) {
    const int command = Serial.read();
    if (command == 's') printStatus();
    if (command == 'h') Serial.println("h=help s=status; automatic bench logging; no vehicle commands");
  }
  uint32_t now = millis();
  if (!sdReady && logger::elapsed(now, lastRetryMs, logger::kRetryMs)) {
    lastRetryMs = now;
    startSession();
  }
  now = millis();
  if (logger::elapsed(now, lastSampleMs, logger::kSampleMs)) {
    // No burst of invented samples after blocking SD operations.
    const uint32_t intervals = static_cast<uint32_t>(now - lastSampleMs) / logger::kSampleMs;
    missedIntervals += intervals - 1;
    lastSampleMs = now;
    pollRtc();
    recordSample();
  }
  now = millis();
  if (logger::elapsed(now, lastStatusMs, logger::kStatusMs)) {
    lastStatusMs = now;
    printStatus();
  }
  delay(5);
}
