// Prova UI LVGL 0.1.1 — Cruscotto C3+AI (D-026, D-027).
// Contagiri e temperatura SIMULATI per misurare FPS e memoria. Nessun dato auto.
#include <Arduino.h>
#include <esp_heap_caps.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_rgb.h>
#include <lvgl.h>
#include <math.h>
#include <string.h>

#include "board_8048s050.h"

namespace {
constexpr char kVersion[] = "0.1.1";
constexpr int kRpmDigits = 4;
constexpr int kDigitWidth = 34;  // cella fissa per cifra: il numero non si sposta
constexpr int kBufRows = 40;
constexpr int kRpmMax = 5000;

esp_lcd_panel_handle_t panel = nullptr;
esp_err_t panelStatus = ESP_FAIL;
lv_disp_draw_buf_t drawBuf;
lv_disp_drv_t dispDrv;
lv_obj_t* rpmArc = nullptr;
lv_obj_t* rpmDigits[kRpmDigits] = {};
int shownRpm = -1, shownTemp = -1;
lv_obj_t* tempBar = nullptr;
lv_obj_t* tempLabel = nullptr;
uint32_t refreshes = 0, refreshMs = 0, lastReport = 0;

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

void flush(lv_disp_drv_t* drv, const lv_area_t* area, lv_color_t* pixels) {
  // Con IDF 4.4 la copia nel framebuffer PSRAM è sincrona.
  esp_lcd_panel_draw_bitmap(panel, area->x1, area->y1, area->x2 + 1, area->y2 + 1, pixels);
  lv_disp_flush_ready(drv);
}

void monitor(lv_disp_drv_t*, uint32_t timeMs, uint32_t) {
  ++refreshes;
  refreshMs += timeMs;
}

bool startLvgl() {
  lv_init();
  const size_t pixels = board::kWidth * kBufRows;
  const uint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_DMA;
  auto* buf1 = static_cast<lv_color_t*>(heap_caps_malloc(pixels * sizeof(lv_color_t), caps));
  auto* buf2 = static_cast<lv_color_t*>(heap_caps_malloc(pixels * sizeof(lv_color_t), caps));
  if (!buf1 || !buf2) return false;
  lv_disp_draw_buf_init(&drawBuf, buf1, buf2, pixels);
  lv_disp_drv_init(&dispDrv);
  dispDrv.hor_res = board::kWidth;
  dispDrv.ver_res = board::kHeight;
  dispDrv.flush_cb = flush;
  dispDrv.monitor_cb = monitor;
  dispDrv.draw_buf = &drawBuf;
  lv_disp_drv_register(&dispDrv);
  return true;
}

void buildUi() {
  lv_obj_t* screen = lv_scr_act();
  lv_obj_set_style_bg_color(screen, lv_color_black(), 0);

  rpmArc = lv_arc_create(screen);
  lv_obj_set_size(rpmArc, 400, 400);
  lv_obj_align(rpmArc, LV_ALIGN_LEFT_MID, 40, 20);
  lv_arc_set_bg_angles(rpmArc, 135, 45);
  lv_arc_set_range(rpmArc, 0, kRpmMax);
  lv_obj_remove_style(rpmArc, nullptr, LV_PART_KNOB);
  lv_obj_clear_flag(rpmArc, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_set_style_arc_width(rpmArc, 28, LV_PART_MAIN);
  lv_obj_set_style_arc_width(rpmArc, 28, LV_PART_INDICATOR);
  lv_obj_set_style_arc_color(rpmArc, lv_color_hex(0x303030), LV_PART_MAIN);
  lv_obj_set_style_arc_color(rpmArc, lv_color_hex(0xFFB000), LV_PART_INDICATOR);

  for (int i = 0; i < kRpmDigits; ++i) {
    rpmDigits[i] = lv_label_create(screen);
    lv_obj_set_width(rpmDigits[i], kDigitWidth);
    lv_obj_set_style_text_align(rpmDigits[i], LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_style_text_font(rpmDigits[i], &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(rpmDigits[i], lv_color_white(), 0);
    lv_label_set_text_static(rpmDigits[i], "");
    const int offset = (i - kRpmDigits / 2) * kDigitWidth + kDigitWidth / 2;
    lv_obj_align_to(rpmDigits[i], rpmArc, LV_ALIGN_CENTER, offset, -10);
  }

  lv_obj_t* unit = lv_label_create(screen);
  lv_label_set_text(unit, "giri/min");
  lv_obj_set_style_text_font(unit, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(unit, lv_color_hex(0xA0A0A0), 0);
  lv_obj_align_to(unit, rpmArc, LV_ALIGN_CENTER, 0, 45);

  tempBar = lv_bar_create(screen);
  lv_obj_set_size(tempBar, 260, 36);
  lv_obj_align(tempBar, LV_ALIGN_RIGHT_MID, -50, 40);
  lv_bar_set_range(tempBar, 40, 130);
  lv_obj_set_style_bg_color(tempBar, lv_color_hex(0x303030), LV_PART_MAIN);
  lv_obj_set_style_bg_color(tempBar, lv_color_hex(0x00C0FF), LV_PART_INDICATOR);

  tempLabel = lv_label_create(screen);
  lv_obj_set_style_text_font(tempLabel, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(tempLabel, lv_color_white(), 0);
  lv_obj_align_to(tempLabel, tempBar, LV_ALIGN_OUT_TOP_LEFT, 0, -12);

  lv_obj_t* demo = lv_label_create(screen);
  lv_label_set_text(demo, "DEMO - dati simulati");
  lv_obj_set_style_text_font(demo, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(demo, lv_color_hex(0xFF4040), 0);
  lv_obj_align(demo, LV_ALIGN_TOP_RIGHT, -30, 20);
}

void updateValues() {
  const float t = millis() / 1000.0f;
  const int rpm = 800 + static_cast<int>(1900.0f * (1.0f + sinf(t * 1.3f)));
  const int temp = 85 + static_cast<int>(10.0f * sinf(t * 0.2f));
  lv_arc_set_value(rpmArc, rpm);
  if (rpm != shownRpm) {
    // Ogni cifra in una cella fissa; si ridisegnano solo le cifre cambiate.
    static const char* const kDigitText[] = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"};
    int value = rpm;
    for (int i = kRpmDigits - 1; i >= 0; --i) {
      const bool blank = value == 0 && i < kRpmDigits - 1;
      const char* text = blank ? "" : kDigitText[value % 10];
      if (strcmp(lv_label_get_text(rpmDigits[i]), text) != 0) lv_label_set_text_static(rpmDigits[i], text);
      value /= 10;
    }
    shownRpm = rpm;
  }
  if (temp != shownTemp) {
    lv_bar_set_value(tempBar, temp, LV_ANIM_OFF);
    lv_label_set_text_fmt(tempLabel, "Acqua %d C", temp);
    shownTemp = temp;
  }
}

void report() {
  const uint32_t avg = refreshes ? refreshMs / refreshes : 0;
  Serial.printf("ui_test version=%s panel=%s fps=%u refr_avg_ms=%u heap_int_free=%u "
                "psram_free=%u uptime_ms=%lu\n",
                kVersion, esp_err_to_name(panelStatus), static_cast<unsigned>(refreshes / 5),
                static_cast<unsigned>(avg),
                static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
                static_cast<unsigned>(ESP.getFreePsram()), millis());
  refreshes = 0;
  refreshMs = 0;
}
}  // namespace

void setup() {
  Serial.begin(115200);
  delay(200);
  pinMode(board::kBacklight, OUTPUT);
  digitalWrite(board::kBacklight, LOW);
  panelStatus = psramFound() ? startPanel() : ESP_ERR_NO_MEM;
  if (panelStatus == ESP_OK && !startLvgl()) panelStatus = ESP_ERR_NO_MEM;
  if (panelStatus == ESP_OK) {
    buildUi();
    updateValues();
    lv_timer_handler();
    digitalWrite(board::kBacklight, HIGH);
  }
  lastReport = millis();
  report();
}

void loop() {
  if (panelStatus != ESP_OK) {
    delay(5000);
    report();
    return;
  }
  static uint32_t lastUpdate = 0;
  if (millis() - lastUpdate >= 33) {
    lastUpdate = millis();
    updateValues();
  }
  lv_timer_handler();
  if (millis() - lastReport >= 5000) {
    lastReport = millis();
    report();
  }
  delay(1);
}
