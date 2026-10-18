#include <Arduino.h>
#include <SPI.h>

// Bench only: H/L must remain physically disconnected from every CAN bus.
// No normal/loopback mode, RTS command or TX buffer access is implemented.
namespace {
constexpr int kSck = 18, kMiso = 19, kMosi = 23, kCs = 26;
constexpr uint8_t kCanstat = 0x0E, kCanctrl = 0x0F, kCnf1 = 0x2A;
const SPISettings settings(100000, MSBFIRST, SPI_MODE0);
bool passed = false;
uint32_t lastReport = 0;

void select() {
  SPI.beginTransaction(settings);
  digitalWrite(kCs, LOW);
}
void release() {
  digitalWrite(kCs, HIGH);
  SPI.endTransaction();
}
uint8_t readRegister(uint8_t address) {
  select();
  SPI.transfer(0x03);
  SPI.transfer(address);
  const uint8_t value = SPI.transfer(0);
  release();
  return value;
}
void writeRegister(uint8_t address, uint8_t value) {
  select();
  SPI.transfer(0x02);
  SPI.transfer(address);
  SPI.transfer(value);
  release();
}
bool configurationMode() {
  return (readRegister(kCanstat) & 0xE0) == 0x80 &&
         (readRegister(kCanctrl) & 0xE0) == 0x80;
}
bool runTest() {
  select();
  SPI.transfer(0xC0);  // SPI reset returns the controller to configuration mode.
  release();
  delay(20);
  Serial.printf("CANSTAT=0x%02X CANCTRL=0x%02X\n",
                readRegister(kCanstat), readRegister(kCanctrl));
  if (!configurationMode()) {
    Serial.println("FAIL: configuration mode not confirmed; no register writes");
    return false;
  }
  const uint8_t original = readRegister(kCnf1);
  bool ok = true;
  for (uint8_t pattern : {uint8_t(0x55), uint8_t(0xAA), uint8_t(0x00)}) {
    if (!configurationMode()) { ok = false; break; }
    writeRegister(kCnf1, pattern);
    const uint8_t actual = readRegister(kCnf1);
    Serial.printf("CNF1 wrote=0x%02X read=0x%02X\n", pattern, actual);
    if (actual != pattern) { ok = false; break; }
  }
  if (!configurationMode()) {
    Serial.println("FAIL: configuration mode lost");
    return false;
  }
  writeRegister(kCnf1, original);
  return ok && readRegister(kCnf1) == original && configurationMode();
}
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\nc3_mcp2515_spi_test version=0.1.0");
  Serial.println("BENCH ONLY: CAN H/L disconnected; SPI=100kHz mode0; power=3.3V");
  // Drive CS inactive before starting the SPI peripheral.
  digitalWrite(kCs, HIGH);
  pinMode(kCs, OUTPUT);
  SPI.begin(kSck, kMiso, kMosi, kCs);
  passed = runTest();
  Serial.println(passed ? "SPI_TEST=PASS (CAN not tested)" : "SPI_TEST=FAIL");
  lastReport = millis();
}

void loop() {
  const uint32_t now = millis();
  if (static_cast<uint32_t>(now - lastReport) >= 5000) {
    lastReport = now;
    Serial.printf("status SPI_TEST=%s uptime_ms=%lu\n",
                  passed ? "PASS" : "FAIL", static_cast<unsigned long>(now));
  }
  delay(10);  // No automatic retries or changes to the controller after the test.
}
