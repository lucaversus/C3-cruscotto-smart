#include <Arduino.h>
#include <esp_timer.h>
#include <inttypes.h>
#include "acquisition.h"
#include "logger_logic.h"
#include "peripherals.h"
#include "storage.h"

namespace {
QueueHandle_t queue = nullptr;
LogStorage storage;
logger::SaveGate gate;
uint32_t lastRtc = 0, lastFlush = 0, lastStatus = 0, lastMount = 0;
bool firstMount = true;
void buttonTask(void *) {
  logger::StopButton button;
  for (;;) {
    if (button.update(digitalRead(logger::kStopPin) == LOW, millis())) capture.stop = true;
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}
const char *title() {
  switch (gate.state) {
    case logger::SaveState::Recording: return "REGISTRAZIONE";
    case logger::SaveState::Stopping: return "SALVATAGGIO";
    case logger::SaveState::Saved: return "SALVATO";
    case logger::SaveState::Error: return "ERRORE SD/SIST";
    case logger::SaveState::NoSession: return "NESSUN FILE";
    default: return "ATTESA SD";
  }
}
void printStatus() {
  Serial.printf("status state=%s file=%s rows=%" PRIu64 " dropped=%lu rtc=%s van_frames=%lu van_bad=%lu kwp_frames=%lu kwp_errors=%lu storage=%s heap=%u\n",
    title(), storage.path, storage.rows, static_cast<unsigned long>(capture.dropped.load()), rtc.state,
    static_cast<unsigned long>(capture.vanFrames.load()), static_cast<unsigned long>(capture.vanBad.load()),
    static_cast<unsigned long>(capture.kwpFrames.load()), static_cast<unsigned long>(capture.kwpErrors.load()), storage.error, ESP.getFreeHeap());
}
void fail() { gate.fail(); capture.stop = true; storage.abandon(); printStatus(); }
void command(const char *text) {
  if (!strcmp(text, "stop")) capture.stop = true;
  else if (!strcmp(text, "s") || !strcmp(text, "status")) printStatus();
  else if (!strncmp(text, "time ", 5)) {
    const bool ok = setRtcUtc(text + 5); Serial.printf("rtc_set=%s\n", ok ? "ok" : "failed");
    if (gate.state == logger::SaveState::Recording) systemRecord(ok ? "rtc_set" : "rtc_set_failed");
  } else if (!strncmp(text, "oled ", 5)) Serial.printf("oled_select=%s\n", selectOled(text + 5) ? "ok" : "failed");
  else Serial.println("commands (Enter): status | stop | time YYYY-MM-DDTHH:MM:SSZ | oled sh1106 | oled ssd1306 | help");
}
void serialCommands() {
  static char line[64] = {};
  static size_t used = 0;
  static bool overflow = false;
  for (unsigned count = 0; count < 64 && Serial.available(); ++count) {
    const char c = Serial.read();
    if (c == '\r' || c == '\n') {
      if (overflow) Serial.println("command_too_long");
      else if (used) { line[used] = 0; command(line); }
      used = 0; overflow = false;
    } else if (c >= 32 && c <= 126) {
      if (used + 1 < sizeof(line) && !overflow) line[used++] = c; else overflow = true;
    }
  }
}
} // namespace
bool submitRecord(const Record &record) {
  if (queue && xQueueSend(queue, &record, 0) == pdPASS) return true;
  ++capture.dropped; return false;
}
void systemRecord(const char *event, uint32_t id) {
  Record row{}; row.monoUs = esp_timer_get_time(); row.event = event; row.id = id; submitRecord(row);
}
void setup() {
  Serial.begin(115200);
  pinMode(logger::kUnusedCanCs, OUTPUT); digitalWrite(logger::kUnusedCanCs, HIGH);
  pinMode(logger::kKwpTx, OUTPUT); digitalWrite(logger::kKwpTx, LOW);
  pinMode(logger::kStopPin, INPUT_PULLUP);
  queue = xQueueCreate(logger::kQueueDepth, sizeof(Record));
  if (!queue || xTaskCreatePinnedToCore(buttonTask, "stop_button", 2048, nullptr, 4, nullptr, 0) != pdPASS) { gate.fail(); capture.stop = true; }
  beginPeripherals();
  Serial.printf("\nc3_datalogger version=%s auto_start=1 kwp=%u van=%u no_radio=1 no_format=1\n", logger::kVersion, LOGGER_ENABLE_KWP, LOGGER_ENABLE_VAN);
  Serial.println("RTC is never set from build time. Use explicit time command with UTC Z.");
  command("help"); lastRtc = lastFlush = lastStatus = millis();
}
void loop() {
  serialCommands();
  const uint32_t now = millis();
  if (capture.stop) gate.stop();
  if (gate.state == logger::SaveState::Waiting && !capture.stop && (firstMount || logger::elapsed(now, lastMount, logger::kRetryMs))) {
    firstMount = false; lastMount = now;
    if (storage.begin()) {
      if (capture.stop) { gate.opened(); gate.stop(); }
      else {
        gate.opened(); systemRecord("boot");
        systemRecord(LOGGER_ENABLE_KWP || LOGGER_ENABLE_VAN ? "profile_vehicle" : "profile_bench");
        if (LOGGER_ENABLE_KWP) systemRecord("kwp_profile", 10400);
        if (LOGGER_ENABLE_VAN) systemRecord("van_profile", LOGGER_VAN_BODY ? 62500 : 125000);
        if (!startAcquisition()) fail();
      }
    } else { Serial.printf("storage=%s retry_ms=%lu\n", storage.error, static_cast<unsigned long>(logger::kRetryMs)); storage.abandon(); }
  }
  if (gate.state == logger::SaveState::Recording || gate.state == logger::SaveState::Stopping) {
    Record row{};
    for (unsigned i = 0; i < 32 && xQueueReceive(queue, &row, 0) == pdPASS; ++i) { if (!storage.append(row)) { fail(); break; } }
    if (gate.state == logger::SaveState::Recording && logger::elapsed(now, lastFlush, logger::kFlushMs)) { lastFlush = now; if (!storage.sync()) fail(); }
    if (gate.state == logger::SaveState::Stopping && capture.kwpDone && capture.vanDone && uxQueueMessagesWaiting(queue) == 0) {
      const bool ok = storage.finish("stop_footer");
      gate.finish(true, true, ok, ok, ok);
      if (!ok) storage.abandon();
      printStatus(); drawStatus(title(), ok ? "SD CHIUSA" : "SALVATAGGIO KO", storage.rows, capture.dropped);
    }
  }
  if (logger::elapsed(now, lastRtc, logger::kSampleMs)) {
    lastRtc = now; pollRtc();
    if (gate.state == logger::SaveState::Recording) systemRecord("health", ESP.getFreeHeap());
    drawStatus(title(), gate.state == logger::SaveState::Saved ? "SD CHIUSA" : gate.state == logger::SaveState::Error ? "NON SPEGNERE" : "", storage.rows, capture.dropped);
  }
  if (logger::elapsed(now, lastStatus, logger::kStatusMs)) { lastStatus = now; printStatus(); }
  delay(1);
}
