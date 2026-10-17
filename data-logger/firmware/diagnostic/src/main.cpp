#include <Arduino.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <inttypes.h>

// Bench-only diagnostics: UART0 is the only external interface initialized.
// No GPIO probing, SPI, I2C, SD, RTC, vehicle bus, radio or persistent writes.
namespace {
constexpr uint32_t kReportIntervalMs = 5000;
uint32_t lastReportMs = 0;

void printStatus() {
  Serial.printf("status uptime_us=%" PRId64 " heap_free_bytes=%u heap_min_bytes=%u\n",
                esp_timer_get_time(), ESP.getFreeHeap(), ESP.getMinFreeHeap());
}
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\nc3_datalogger_diagnostic version=0.1.0");
  Serial.println("mode=bench_serial_only peripherals=disabled");
  Serial.printf("chip_model=%s chip_revision=%u cores=%u cpu_mhz=%u\n",
                ESP.getChipModel(), ESP.getChipRevision(), ESP.getChipCores(),
                ESP.getCpuFreqMHz());
  Serial.printf("flash_bytes=%u flash_hz=%u flash_mode=%u\n",
                ESP.getFlashChipSize(), ESP.getFlashChipSpeed(),
                static_cast<unsigned>(ESP.getFlashChipMode()));
  Serial.printf("sdk=%s reset_reason=%u heap_total_bytes=%u psram_bytes=%u\n",
                ESP.getSdkVersion(), static_cast<unsigned>(esp_reset_reason()),
                ESP.getHeapSize(), ESP.getPsramSize());
  Serial.println("reset_reason is ESP-IDF esp_reset_reason_t; uptime is monotonic, not RTC time.");
  Serial.println("commands: s + Enter = status; h + Enter = help");
  printStatus();
  lastReportMs = millis();
}

void loop() {
  // Bound input handling so continuous serial input cannot starve status reports.
  for (unsigned count = 0; count < 32 && Serial.available() > 0; ++count) {
    const int command = Serial.read();
    if (command == 's') {
      printStatus();
    } else if (command == 'h') {
      Serial.println("s=status h=help; no reset, write or bus commands available");
    }
  }
  const uint32_t now = millis();
  if (static_cast<uint32_t>(now - lastReportMs) >= kReportIntervalMs) {
    lastReportMs = now;
    printStatus();
  }
  delay(10);
}
