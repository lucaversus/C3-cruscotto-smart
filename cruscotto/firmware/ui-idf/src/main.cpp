// Firmware S3 su ESP-IDF 5.5 0.3.0 — Cruscotto C3+AI (D-026, D-029, D-037, D-039).
// Struttura: collegamento fe_link e sorgente simulata sul core 0, interfaccia LVGL sul
// core 1, report e autotest nel compito principale. Doppio framebuffer, scambio al vsync.
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>

#include "board_8048s050.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_rgb.h"
#include "esp_ota_ops.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"

namespace {
constexpr char kVersion[] = "0.3.0";  // compiti separati, archivio segnali, collegamento fe_link
constexpr int kRpmMax = 5000;
constexpr int kRpmDigits = 4;
constexpr int kDigitWidth = 34;
constexpr gpio_num_t kSdCs = GPIO_NUM_10;  // MicroSD della S3 esclusa (D-029)
constexpr int64_t kSelfTestUs = 10000000;  // D-039: conferma dopo 10 s di funzionamento

esp_lcd_panel_handle_t panel = nullptr;
esp_err_t panelStatus = ESP_FAIL;
SemaphoreHandle_t vsyncSem = nullptr;
std::atomic<uint32_t> vsyncCount{0};
lv_disp_draw_buf_t drawBuf;
lv_disp_drv_t dispDrv;
lv_obj_t* rpmArc = nullptr;
lv_obj_t* rpmDigits[kRpmDigits] = {};
lv_obj_t* tempBar = nullptr;
lv_obj_t* tempLabel = nullptr;
lv_obj_t* statusLabel = nullptr;
const char* shownStatus = nullptr;
int shownRpm = -1, shownTemp = -1;
uint32_t refreshes = 0, refreshMs = 0;

bool IRAM_ATTR onVsync(esp_lcd_panel_handle_t, const esp_lcd_rgb_panel_event_data_t*, void*) {
  vsyncCount.fetch_add(1, std::memory_order_relaxed);
  BaseType_t woken = pdFALSE;
  xSemaphoreGiveFromISR(vsyncSem, &woken);
  return woken == pdTRUE;
}

esp_err_t startPanel() {
  esp_lcd_rgb_panel_config_t config = {};
  config.clk_src = LCD_CLK_SRC_DEFAULT;
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
  config.bits_per_pixel = 16;
  config.num_fbs = 2;
  config.bounce_buffer_size_px = board::kWidth * 10;
  config.dma_burst_size = 64;
  config.hsync_gpio_num = board::kHsync;
  config.vsync_gpio_num = board::kVsync;
  config.de_gpio_num = board::kDe;
  config.pclk_gpio_num = board::kPclk;
  config.disp_gpio_num = -1;
  for (int i = 0; i < 16; ++i) config.data_gpio_nums[i] = board::kData[i];
  config.flags.fb_in_psram = 1;
  esp_err_t err = esp_lcd_new_rgb_panel(&config, &panel);
  if (err != ESP_OK) return err;
  esp_lcd_rgb_panel_event_callbacks_t callbacks = {};
  callbacks.on_vsync = onVsync;
  err = esp_lcd_rgb_panel_register_event_callbacks(panel, &callbacks, nullptr);
  if (err == ESP_OK) err = esp_lcd_panel_reset(panel);
  if (err == ESP_OK) err = esp_lcd_panel_init(panel);
  return err;
}

// Direct mode: LVGL ridisegna solo le zone cambiate nel framebuffer non visibile.
// All'ultima zona si chiede lo scambio (completato al vsync), poi le stesse zone
// vengono copiate nell'altro framebuffer, che diventa quello su cui disegnare.
void* fbs[2] = {nullptr, nullptr};

void syncDirtyAreas(const lv_color_t* front) {
  lv_disp_t* disp = _lv_refr_get_disp_refreshing();
  lv_color_t* back = static_cast<lv_color_t*>(front == fbs[0] ? fbs[1] : fbs[0]);
  for (uint16_t i = 0; i < disp->inv_p; ++i) {
    if (disp->inv_area_joined[i]) continue;
    const lv_area_t& a = disp->inv_areas[i];
    const int width = lv_area_get_width(&a);
    for (int y = a.y1; y <= a.y2; ++y) {
      const size_t offset = static_cast<size_t>(y) * board::kWidth + a.x1;
      memcpy(back + offset, front + offset, width * sizeof(lv_color_t));
    }
  }
}

void flush(lv_disp_drv_t* drv, const lv_area_t*, lv_color_t* pixels) {
  if (lv_disp_flush_is_last(drv)) {
    esp_lcd_panel_draw_bitmap(panel, 0, 0, board::kWidth, board::kHeight, pixels);
    xSemaphoreTake(vsyncSem, 0);
    xSemaphoreTake(vsyncSem, pdMS_TO_TICKS(100));
    syncDirtyAreas(pixels);
  }
  lv_disp_flush_ready(drv);
}

void monitor(lv_disp_drv_t*, uint32_t timeMs, uint32_t) {
  ++refreshes;
  refreshMs += timeMs;
}

esp_err_t startLvgl() {
  void* fb0 = nullptr;
  void* fb1 = nullptr;
  esp_err_t err = esp_lcd_rgb_panel_get_frame_buffer(panel, 2, &fb0, &fb1);
  if (err != ESP_OK) return err;
  fbs[0] = fb0;
  fbs[1] = fb1;
  lv_init();
  lv_disp_draw_buf_init(&drawBuf, fb0, fb1, board::kWidth * board::kHeight);
  lv_disp_drv_init(&dispDrv);
  dispDrv.hor_res = board::kWidth;
  dispDrv.ver_res = board::kHeight;
  dispDrv.flush_cb = flush;
  dispDrv.monitor_cb = monitor;
  dispDrv.draw_buf = &drawBuf;
  dispDrv.direct_mode = 1;
  lv_disp_drv_register(&dispDrv);
  return ESP_OK;
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

  statusLabel = lv_label_create(screen);
  lv_label_set_text_static(statusLabel, "");
  lv_obj_set_style_text_font(statusLabel, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(statusLabel, lv_color_hex(0xFF4040), 0);
  lv_obj_align(statusLabel, LV_ALIGN_TOP_RIGHT, -30, 20);
}

// Legge l'archivio dei segnali (mai i dati grezzi) e aggiorna solo ciò che cambia.
void updateValues() {
  SignalStore& store = signalStore();
  const int64_t now = esp_timer_get_time();
  const SignalValue rpmV = store.get(felink::sig::kRpm, now, 500000);
  const SignalValue tempV = store.get(felink::sig::kCoolantC, now, 3000000);
  const int rpm = rpmV.quality == felink::Quality::kStale ? 0 : static_cast<int>(rpmV.value + 0.5f);
  const int temp = tempV.quality == felink::Quality::kStale ? -1 : static_cast<int>(tempV.value + 0.5f);
  lv_arc_set_value(rpmArc, rpm);
  if (rpm != shownRpm) {
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
    lv_bar_set_value(tempBar, temp < 0 ? 40 : temp, LV_ANIM_OFF);
    if (temp < 0) lv_label_set_text_static(tempLabel, "Acqua --");
    else lv_label_set_text_fmt(tempLabel, "Acqua %d C", temp);
    shownTemp = temp;
  }
  // Stato: DEMO se il dato è simulato, avviso se il collegamento è perso (D-016, D-037).
  const char* status = !linkAlive(now) ? "COLLEGAMENTO ASSENTE"
                       : rpmV.quality == felink::Quality::kSimulated ? "DEMO - dati simulati" : "";
  if (status != shownStatus) {
    lv_label_set_text_static(statusLabel, status);
    shownStatus = status;
  }
}

void report() {
  static uint32_t lastVsync = 0, lastFrames = 0;
  const uint32_t vs = vsyncCount.load(std::memory_order_relaxed);
  const LinkStats ls = linkStats();
  const uint32_t avg = refreshes ? refreshMs / refreshes : 0;
  printf("ui_idf version=%s ota=%s panel=%s fps=%u refr_avg_ms=%u panel_hz=%u link=%s frames_s=%u "
         "link_err=%u link_lost=%u heap_int_free=%u psram_free=%u uptime_ms=%u\n",
         kVersion, esp_ota_get_running_partition()->label, esp_err_to_name(panelStatus),
         static_cast<unsigned>(refreshes / 5), static_cast<unsigned>(avg),
         static_cast<unsigned>((vs - lastVsync) / 5), ls.simulated ? "sim" : "uart",
         static_cast<unsigned>((ls.frames - lastFrames) / 5), static_cast<unsigned>(ls.errors),
         static_cast<unsigned>(ls.lostSeq),
         static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
         static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)),
         static_cast<unsigned>(esp_timer_get_time() / 1000));
  lastVsync = vs;
  lastFrames = ls.frames;
  refreshes = 0;
  refreshMs = 0;
}

void outputLow(gpio_num_t pin, int level) {
  gpio_reset_pin(pin);
  gpio_set_direction(pin, GPIO_MODE_OUTPUT);
  gpio_set_level(pin, level);
}

// Compito dell'interfaccia sul core 1: unico punto che chiama LVGL.
void uiTask(void*) {
  int64_t lastUpdate = 0;
  while (true) {
    const int64_t now = esp_timer_get_time();
    if (now - lastUpdate >= 33000) {
      lastUpdate = now;
      updateValues();
    }
    const uint32_t waitMs = lv_timer_handler();
    vTaskDelay(pdMS_TO_TICKS(waitMs < 1 ? 1 : (waitMs > 10 ? 10 : waitMs)));
  }
}
}  // namespace

extern "C" void app_main() {
  outputLow(static_cast<gpio_num_t>(board::kBacklight), 0);
  outputLow(kSdCs, 1);
  linkStart(true);  // 0.3.0: front-end non ancora presente, sorgente simulata in loopback
  vsyncSem = xSemaphoreCreateBinary();
  panelStatus = startPanel();
  if (panelStatus == ESP_OK) panelStatus = startLvgl();
  if (panelStatus == ESP_OK) {
    buildUi();
    updateValues();
    lv_timer_handler();
    gpio_set_level(static_cast<gpio_num_t>(board::kBacklight), 1);
    xTaskCreatePinnedToCore(uiTask, "ui", 8192, nullptr, 5, nullptr, 1);
  }
  esp_ota_img_states_t state = ESP_OTA_IMG_UNDEFINED;
  esp_ota_get_state_partition(esp_ota_get_running_partition(), &state);
  printf("ui_idf ota_state=%d (pending=%d)\n", static_cast<int>(state), ESP_OTA_IMG_PENDING_VERIFY);
  bool confirmed = false;
  while (true) {
    vTaskDelay(pdMS_TO_TICKS(5000));
    report();
    // Autotest (D-039): display inizializzato, collegamento attivo, 10 s senza blocchi.
    // Se la nuova versione non arriva qui, al riavvio successivo il bootloader torna alla precedente.
    const int64_t now = esp_timer_get_time();
    if (!confirmed && panelStatus == ESP_OK && linkAlive(now) && now >= kSelfTestUs) {
      confirmed = true;
      if (state == ESP_OTA_IMG_PENDING_VERIFY) {
        printf("ui_idf autotest superato: %s\n", esp_err_to_name(esp_ota_mark_app_valid_cancel_rollback()));
      }
    }
  }
}
