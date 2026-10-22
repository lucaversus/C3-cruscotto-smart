// Configurazione LVGL 8.3 per la prova UI su ESP-IDF 5.5; valori non indicati: predefiniti LVGL.
#ifndef LV_CONF_H
#define LV_CONF_H
#define LV_COLOR_DEPTH 16
#define LV_COLOR_16_SWAP 0
#define LV_MEM_CUSTOM 1          // malloc di sistema: PSRAM disponibile
#define LV_TICK_CUSTOM 1
#define LV_TICK_CUSTOM_INCLUDE <esp_timer.h>
#define LV_TICK_CUSTOM_SYS_TIME_EXPR ((uint32_t)(esp_timer_get_time() / 1000))
#define LV_DISP_DEF_REFR_PERIOD 16
#define LV_USE_PERF_MONITOR 1    // FPS e CPU in basso a destra
#define LV_USE_LOG 0
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_MONTSERRAT_28 1
#define LV_FONT_MONTSERRAT_48 1
#define LV_FONT_UNSCII_16 1       // sequenza d'avvio in stile "Matrix"
#endif  // LV_CONF_H
