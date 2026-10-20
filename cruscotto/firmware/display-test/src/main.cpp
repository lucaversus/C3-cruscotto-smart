// Prova display ESP32-8048S050 0.1.0 — Cruscotto C3+AI (D-026, D-027).
// PSRAM, barre di colore RGB565 e scansione I2C. Nessun accesso al veicolo.
#include <Arduino.h>
#include <Wire.h>
#include <esp_heap_caps.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_rgb.h>

#include "board_8048s050.h"

namespace {
constexpr char kVersion[] = "0.1.0";
constexpr int kStripRows = 20;
// Bianco, giallo, ciano, verde, magenta, rosso, blu, nero.
constexpr uint16_t kBars[8] = {0xFFFF, 0xFFE0, 0x07FF, 0x07E0, 0xF81F, 0xF800, 0x001F, 0x0000};

esp_lcd_panel_handle_t panel = nullptr;
esp_err_t panelStatus = ESP_FAIL;
int i2cFound = 0;
char i2cList[96] = "";

esp_err_t startPanel() {
  esp_lcd_rgb_panel_config_t config = {};
  config.clk_src = LCD_CLK_SRC_PLL160M;
  config.timings.pclk_hz = board::kPclkHz;
  config.timings.h_res = board::kWidth;
  config.timings.v_res = board::kHeight;
  config.timings.hsync_pulse_width = board::kHsyncPulse;
  config.timings.hsync_back_porch = board::kHsyncBack;
  config.timings.hsync_front_porch = board::kHsyncFront;
  config.timings.vsync_pulse_width = board::kVsyncPulse;
  config.timings.vsync_back_porch = board::kVsyncBack;
  config.timings.vsync_front_porch = board::kVsyncFront;
  config.timings.flags.pclk_active_neg = 1;
  config.data_width = 16;
  config.sram_trans_align = 4;
  config.psram_trans_align = 64;
  config.hsync_gpio_num = board::kHsync;
  config.vsync_gpio_num = board::kVsync;
  config.de_gpio_num = board::kDe;
  config.pclk_gpio_num = board::kPclk;
  config.disp_gpio_num = -1;
  for (int i = 0; i < 16; ++i) config.data_gpio_nums[i] = board::kData[i];
  config.flags.fb_in_psram = 1;
  esp_err_t err = esp_lcd_new_rgb_panel(&config, &panel);
  if (err == ESP_OK) err = esp_lcd_panel_reset(panel);
  if (err == ESP_OK) err = esp_lcd_panel_init(panel);
  return err;
}

esp_err_t drawBars() {
  static uint16_t strip[board::kWidth * kStripRows];
  const int barWidth = board::kWidth / 8;
  for (int x = 0; x < board::kWidth; ++x) {
    const uint16_t color = kBars[x / barWidth];
    for (int y = 0; y < kStripRows; ++y) strip[y * board::kWidth + x] = color;
  }
  for (int y = 0; y < board::kHeight; y += kStripRows) {
    const esp_err_t err = esp_lcd_panel_draw_bitmap(panel, 0, y, board::kWidth, y + kStripRows, strip);
    if (err != ESP_OK) return err;
  }
  return ESP_OK;
}

void scanI2c() {
  Wire.begin(board::kI2cSda, board::kI2cScl, 100000);
  for (uint8_t address = 0x08; address < 0x78; ++address) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      const size_t used = strlen(i2cList);
      snprintf(i2cList + used, sizeof(i2cList) - used, "%s0x%02X", i2cFound ? "," : "", address);
      ++i2cFound;
    }
  }
  Wire.end();
}

void report() {
  Serial.printf("display_test version=%s psram_found=%d psram_bytes=%u psram_free=%u "
                "panel=%s i2c_sda=%d i2c_scl=%d i2c_devices=%d [%s] uptime_ms=%lu\n",
                kVersion, psramFound() ? 1 : 0, static_cast<unsigned>(ESP.getPsramSize()),
                static_cast<unsigned>(ESP.getFreePsram()), esp_err_to_name(panelStatus),
                board::kI2cSda, board::kI2cScl, i2cFound, i2cList, millis());
}
}  // namespace

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(board::kBacklight, OUTPUT);
  digitalWrite(board::kBacklight, LOW);
  panelStatus = psramFound() ? startPanel() : ESP_ERR_NO_MEM;
  if (panelStatus == ESP_OK) panelStatus = drawBars();
  digitalWrite(board::kBacklight, HIGH);
  scanI2c();
  report();
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last >= 5000) {
    last = millis();
    report();
  }
}
