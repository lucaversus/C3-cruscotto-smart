#include "peripherals.h"
#include "acquisition.h"
#include "logger_logic.h"
#include <Wire.h>
#include <U8x8lib.h>
#include <Preferences.h>
#include <esp_timer.h>

RtcSnapshot rtc;
namespace {
bool ready = false, utcKnown = false;
Preferences settings;
U8X8_SH1106_128X64_NONAME_HW_I2C sh1106(U8X8_PIN_NONE, logger::kScl, logger::kSda);
U8X8_SSD1306_128X64_NONAME_HW_I2C ssd1306(U8X8_PIN_NONE, logger::kScl, logger::kSda);
U8X8 *oled = nullptr;
bool readRegisters(uint8_t reg, uint8_t *bytes, size_t count) {
  if (!ready) return false;
  Wire.beginTransmission(logger::kRtcAddress); Wire.write(reg);
  if (Wire.endTransmission(false)) return false;
  if (Wire.requestFrom(logger::kRtcAddress, count, true) != count) return false;
  for (size_t i = 0; i < count; ++i) bytes[i] = Wire.read();
  return true;
}
bool writeRegisters(uint8_t reg, const uint8_t *bytes, size_t count) {
  if (!ready) return false;
  Wire.beginTransmission(logger::kRtcAddress); Wire.write(reg); Wire.write(bytes, count);
  return Wire.endTransmission(true) == 0;
}
uint8_t bcd(unsigned value) { return (value / 10) * 16 + value % 10; }
bool openOled(bool useSsd) {
  oled = nullptr;
  if (!ready) return false;
  Wire.beginTransmission(logger::kOledAddress);
  if (Wire.endTransmission()) return false;
  oled = useSsd ? static_cast<U8X8 *>(&ssd1306) : static_cast<U8X8 *>(&sh1106);
  oled->setI2CAddress(logger::kOledAddress << 1);
  oled->setBusClock(100000); oled->begin(); oled->setPowerSave(0);
  oled->setFont(u8x8_font_chroma48medium8_r); oled->clearDisplay();
  Wire.setTimeOut(50);
  return true;
}
} // namespace
void beginPeripherals() {
  ready = Wire.begin(logger::kSda, logger::kScl, 100000); Wire.setTimeOut(50);
  settings.begin("c3logger", false); utcKnown = settings.getBool("utc", false);
  // Selectable starting profile, not identification of the actual controller.
  if (!openOled(settings.getBool("ssd1306", false))) Serial.println("oled=unavailable");
  pollRtc();
}
bool selectOled(const char *model) {
  const bool useSsd = strcmp(model, "ssd1306") == 0;
  if (!useSsd && strcmp(model, "sh1106")) return false;
  if (settings.putBool("ssd1306", useSsd) != 1) return false;
  return openOled(useSsd);
}
void pollRtc() {
  rtc.calendar[0] = '\0';
  uint8_t status = 0, raw[7] = {};
  rtc.readMonoUs = esp_timer_get_time();
  if (!readRegisters(0x0f, &status, 1) || !readRegisters(0, raw, sizeof(raw))) { rtc.state = "unavailable"; return; }
  if (status & 0x80) { rtc.state = "oscillator_stop"; utcKnown = false; return; }
  logger::Calendar c{};
  if (!logger::decodeCalendar(raw, c)) { rtc.state = "invalid_calendar"; return; }
  snprintf(rtc.calendar, sizeof(rtc.calendar), "%04u-%02u-%02uT%02u:%02u:%02u", c.year, c.month, c.day, c.hour, c.minute, c.second);
  rtc.state = utcKnown ? "utc_set_by_user" : "calendar_timezone_unknown";
}
bool setRtcUtc(const char *iso) {
  logger::Calendar checked{};
  if (!logger::parseUtc(iso, checked)) return false;
  uint8_t raw[] = {bcd(checked.second), bcd(checked.minute), bcd(checked.hour), logger::weekdaySunday1(checked), bcd(checked.day), bcd(checked.month), bcd(checked.year - 2000)};
  uint8_t status = 0, control = 0;
  if (!readRegisters(0x0e, &control, 1) || !readRegisters(0x0f, &status, 1)) return false;
  control &= ~0x80;
  if (!writeRegisters(0x0e, &control, 1) || !writeRegisters(0, raw, sizeof(raw))) return false;
  uint8_t verify[7] = {};
  if (!readRegisters(0, verify, sizeof(verify)) || memcmp(raw, verify, sizeof(raw))) return false;
  status &= ~0x80;
  if (!writeRegisters(0x0f, &status, 1)) return false;
  utcKnown = settings.putBool("utc", true) == 1;
  pollRtc();
  return utcKnown && strcmp(rtc.state, "utc_set_by_user") == 0;
}
void drawStatus(const char *title, const char *storage, uint64_t rows, uint32_t dropped) {
  if (!oled) return;
  char line[24]; oled->clearDisplay();
  oled->drawString(0, 0, "C3+AI LOGGER"); oled->drawString(0, 1, title); oled->drawString(0, 2, storage);
  snprintf(line, sizeof(line), "RIGHE %lu", static_cast<unsigned long>(rows)); oled->drawString(0, 3, line);
  snprintf(line, sizeof(line), "PERSI %lu", static_cast<unsigned long>(dropped)); oled->drawString(0, 4, line);
  oled->drawString(0, 5, rtc.calendar[0] ? rtc.calendar + 11 : "RTC NON VALIDO");
  snprintf(line, sizeof(line), "OBD:%s VAN:%s", capture.kwpConnected ? "ON" : "--", capture.vanReady ? "ON" : "--"); oled->drawString(0, 6, line);
  oled->drawString(0, 7, !strcmp(title, "SALVATO") ? "PUOI SPEGNERE" : "STOP=SALVA");
}
