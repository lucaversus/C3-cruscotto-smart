// Firmware S3 su ESP-IDF 5.5 (versione in version.h) — Cruscotto C3+AI (D-026, D-029, D-037, D-039, D-041).
// Struttura: collegamento fe_link e sorgente simulata sul core 0, interfaccia LVGL sul
// core 1, report e autotest nel compito principale. Doppio framebuffer, scambio al vsync.
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstring>

#include "board_8048s050.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_heap_caps.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_rgb.h"
#include "esp_ota_ops.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "blackbox.h"
#include "backlight.h"
#include "dashboard.h"
#include "startup.h"
#include "sysstats.h"
#include "version.h"
#include "labels.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"

namespace {
constexpr const char* kVersion = fw::kVersion;
constexpr gpio_num_t kSdCs = GPIO_NUM_10;  // MicroSD della S3 esclusa (D-029)
constexpr int64_t kSelfTestUs = 10000000;  // D-039: conferma dopo 10 s di funzionamento

esp_lcd_panel_handle_t panel = nullptr;
esp_err_t panelStatus = ESP_FAIL;
SemaphoreHandle_t vsyncSem = nullptr;
std::atomic<uint32_t> vsyncCount{0};
lv_disp_draw_buf_t drawBuf;
lv_disp_drv_t dispDrv;
uint32_t refreshes = 0, refreshMs = 0;
lv_obj_t* dashScreen = nullptr;  // schermata della dashboard, mostrata dopo l'avvio

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
  sysstats::frames.fetch_add(1, std::memory_order_relaxed);
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

// Carico % di ciascuna CPU nell'intervallo: 100 meno la quota del compito di inattività.
void cpuLoad(unsigned load[2]) {
  static uint32_t lastIdle[2] = {0, 0};
  static int64_t lastUs = 0;
  const int64_t now = esp_timer_get_time();
  for (int core = 0; core < 2; ++core) {
    TaskStatus_t status;
    vTaskGetInfo(xTaskGetIdleTaskHandleForCore(core), &status, pdFALSE, eInvalid);
    const uint32_t idle = status.ulRunTimeCounter;
    const int64_t span = now - lastUs;
    const uint32_t busy = span > 0 ? 100 - static_cast<uint32_t>((idle - lastIdle[core]) * 100LL / span) : 0;
    load[core] = busy > 100 ? 0 : busy;
    lastIdle[core] = idle;
  }
  lastUs = now;
}

void report() {
  static uint32_t lastVsync = 0, lastFrames = 0;
  const unsigned cpu[2] = {sysstats::cpu[0].load(), sysstats::cpu[1].load()};
  const uint32_t vs = vsyncCount.load(std::memory_order_relaxed);
  const LinkStats ls = linkStats();
  const uint32_t avg = refreshes ? refreshMs / refreshes : 0;
  const blackbox::Stats bb = blackbox::stats();
  printf("ui_idf version=%s ota=%s panel=%s fps=%u refr_avg_ms=%u cpu0=%u%% cpu1=%u%% bl=%d%% panel_hz=%u link=%s frames_s=%u "
         "link_err=%u link_lost=%u bb_fill=%u/%u bb_events=%u bb_fail=%u fs=%u/%uKB labels=%u "
         "heap_int_free=%u psram_free=%u uptime_ms=%u\n",
         kVersion, esp_ota_get_running_partition()->label, esp_err_to_name(panelStatus),
         static_cast<unsigned>(refreshes / 5), static_cast<unsigned>(avg), cpu[0], cpu[1], backlight::percent(),
         static_cast<unsigned>((vs - lastVsync) / 5), ls.simulated ? "sim" : "uart",
         static_cast<unsigned>((ls.frames - lastFrames) / 5), static_cast<unsigned>(ls.errors),
         static_cast<unsigned>(ls.lostSeq), static_cast<unsigned>(bb.filled),
         static_cast<unsigned>(bb.capacity), static_cast<unsigned>(bb.eventsSaved),
         static_cast<unsigned>(bb.eventsFailed), static_cast<unsigned>(bb.fsUsedKb),
         static_cast<unsigned>(bb.fsTotalKb), static_cast<unsigned>(labels::count()),
         static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL)),
         static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM)),
         static_cast<unsigned>(esp_timer_get_time() / 1000));
  lastVsync = vs;
  lastFrames = ls.frames;
  refreshes = 0;
  refreshMs = 0;
}

// Comandi seriali di debug a banco (Invio a fine riga): "bl 0..100", "bl auto", "pwm <Hz>".
void serialCommands() {
  static char line[32];
  static size_t used = 0;
  uint8_t c;
  while (uart_read_bytes(UART_NUM_0, &c, 1, 0) == 1) {
    if (c != '\r' && c != '\n') {
      if (used + 1 < sizeof line) line[used++] = static_cast<char>(c);
      continue;
    }
    line[used] = '\0';
    used = 0;
    unsigned value = 0;
    if (std::strcmp(line, "bl auto") == 0) {
      backlight::setManual(-1);
      printf("ui_idf cmd bl=auto\n");
    } else if (std::sscanf(line, "bl %u", &value) == 1) {
      backlight::setManual(static_cast<int>(value));
      printf("ui_idf cmd bl=%u\n", value);
    } else if (std::sscanf(line, "pwm %u", &value) == 1) {
      printf("ui_idf cmd pwm=%u %s\n", value, backlight::setFrequency(value) ? "ok" : "rifiutata");
    } else if (line[0]) {
      printf("ui_idf comandi: bl 0..100 | bl auto | pwm <Hz>\n");
    }
  }
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
      // Prima la sequenza d'avvio, poi la dashboard (aggiornata subito per la dissolvenza).
      static bool booting = true;
      if (booting) booting = startup::update(now, dashScreen);
      if (!booting) dashboard::update(now);
    }
    backlight::update(now);  // anabbaglianti e protezione termica, variazione graduale
    const uint32_t waitMs = lv_timer_handler();
    vTaskDelay(pdMS_TO_TICKS(waitMs < 1 ? 1 : (waitMs > 10 ? 10 : waitMs)));
  }
}
}  // namespace

extern "C" void app_main() {
  backlight::start();  // PWM a 0: pannello spento fino al primo fotogramma
  outputLow(kSdCs, 1);
  printf("ui_idf blackbox=%s\n", blackbox::start() ? "OK" : "SENZA FILE SYSTEM");
  labels::start();
  linkStart(true);  // front-end non ancora presente: sorgente simulata in loopback
  vsyncSem = xSemaphoreCreateBinary();
  panelStatus = startPanel();
  if (panelStatus == ESP_OK) panelStatus = startLvgl();
  if (panelStatus == ESP_OK) {
    dashboard::build();
    dashScreen = lv_scr_act();
    startup::build();
    lv_timer_handler();
    xTaskCreatePinnedToCore(uiTask, "ui", 8192, nullptr, 5, nullptr, 1);
  }
  esp_ota_img_states_t state = ESP_OTA_IMG_UNDEFINED;
  esp_ota_get_state_partition(esp_ota_get_running_partition(), &state);
  printf("ui_idf ota_state=%d (pending=%d)\n", static_cast<int>(state), ESP_OTA_IMG_PENDING_VERIFY);
  bool confirmed = false;
  uart_driver_install(UART_NUM_0, 256, 0, 0, nullptr, 0);  // lettura dei comandi di debug
  for (unsigned tick = 1;; ++tick) {
    for (int i = 0; i < 10; ++i) {
      vTaskDelay(pdMS_TO_TICKS(100));
      serialCommands();
    }
    unsigned load[2];
    cpuLoad(load);  // ogni secondo, per lo schermo
    sysstats::cpu[0].store(load[0]);
    sysstats::cpu[1].store(load[1]);
    static uint32_t lastFrames = 0;
    const uint32_t frames = sysstats::frames.load();
    sysstats::fps.store(static_cast<uint16_t>(frames - lastFrames));
    lastFrames = frames;
    if (tick % 5 == 0) report();
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
