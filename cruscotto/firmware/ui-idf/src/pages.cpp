// Pagina 2 "Tecnica": valori della vettura in riquadri con nome, valore e unità; il colore
// del valore indica la qualità del dato (bianco valido, ambra simulato/non verificato,
// grigio assente). Pagina 3 "Diagnostica": stato del cruscotto in stile terminale.
#include "pages.h"

#include <cstdio>
#include <cstring>

#include "backlight.h"
#include "blackbox.h"
#include "esp_heap_caps.h"
#include "esp_ota_ops.h"
#include "fe_link.h"
#include "labels.h"
#include "link.h"
#include "signal_store.h"
#include "sysstats.h"
#include "version.h"

LV_FONT_DECLARE(font_check);  // Share Tech Mono 20 px (tools/genera-font-avvio.py)

namespace pages {
namespace {
lv_obj_t* screenBase(const char* title) {
  lv_obj_t* scr = lv_obj_create(nullptr);
  lv_obj_set_style_bg_color(scr, lv_color_black(), 0);
  lv_obj_clear_flag(scr, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_t* t = lv_label_create(scr);
  lv_obj_set_style_text_font(t, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(t, lv_color_hex(0x909090), 0);
  lv_label_set_text_static(t, title);
  lv_obj_align(t, LV_ALIGN_TOP_LEFT, 20, 12);
  return scr;
}

// --- Pagina 2 ------------------------------------------------------------------------
struct Tile {
  const char* name;
  uint16_t id;
  const char* format;  // printf del valore
  const char* unit;
  int64_t maxAgeUs;
  lv_obj_t* value;
  lv_obj_t* unitLabel;
  char shown[16];
};
Tile tiles[] = {
    {"GIRI MOTORE", felink::sig::kRpm, "%.0f", "giri/min", 500000, nullptr, nullptr, ""},
    {"VELOCITA", felink::sig::kSpeedKmh, "%.0f", "km/h", 1000000, nullptr, nullptr, ""},
    {"TEMPERATURA ACQUA", felink::sig::kCoolantC, "%.0f", "°C", 3000000, nullptr, nullptr, ""},
    {"GASOLIO", felink::sig::kFuelPct, "%.0f", "%", 10000000, nullptr, nullptr, ""},
    {"BATTERIA", felink::sig::kBatteryV, "%.2f", "V", 3000000, nullptr, nullptr, ""},
    {"CONSUMO ISTANTANEO", felink::sig::kFuelL100, "%.1f", "l/100 km", 1000000, nullptr, nullptr, ""},
    {"TEMPERATURA ESTERNA", felink::sig::kOutsideC, "%.0f", "°C", 10000000, nullptr, nullptr, ""},
    {"ABITACOLO", felink::sig::kCabinC, "%.1f", "°C", 10000000, nullptr, nullptr, ""},
    {"ACCELERAZIONE X", felink::sig::kAccelX, "%.2f", "g", 1000000, nullptr, nullptr, ""},
    {"ACCELERAZIONE Y", felink::sig::kAccelY, "%.2f", "g", 1000000, nullptr, nullptr, ""},
    {"NTC DISPLAY", felink::sig::kNtcDisplayC, "%.1f", "°C", 5000000, nullptr, nullptr, ""},
    {"CHIAVE", felink::sig::kIgnition, "%.0f", "", 3000000, nullptr, nullptr, ""},
};
constexpr int kCols = 3, kTileW = 248, kTileH = 96;

uint32_t qualityColor(const SignalValue& v) {
  if (!v.valid() || v.quality == felink::Quality::kStale || v.quality == felink::Quality::kError) return 0x606060;
  return v.quality == felink::Quality::kValid ? 0xFFFFFF : 0xFFB000;
}

// --- Pagina 3 ------------------------------------------------------------------------
constexpr int kDiagLines = 14;
lv_obj_t* diagLines[kDiagLines];
char diagShown[kDiagLines][72];
}  // namespace

lv_obj_t* buildTech() {
  lv_obj_t* scr = screenBase("TECNICA");
  for (int i = 0; i < static_cast<int>(sizeof tiles / sizeof tiles[0]); ++i) {
    Tile& t = tiles[i];
    lv_obj_t* box = lv_obj_create(scr);
    lv_obj_set_size(box, kTileW, kTileH);
    lv_obj_set_pos(box, 20 + (i % kCols) * (kTileW + 8), 56 + (i / kCols) * (kTileH + 8));
    lv_obj_clear_flag(box, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_color(box, lv_color_hex(0x101010), 0);
    lv_obj_set_style_bg_grad_color(box, lv_color_hex(0x1E1E1E), 0);
    lv_obj_set_style_bg_grad_dir(box, LV_GRAD_DIR_VER, 0);
    lv_obj_set_style_border_color(box, lv_color_hex(0x3A3A3A), 0);
    lv_obj_set_style_radius(box, 8, 0);
    lv_obj_set_style_pad_all(box, 8, 0);
    lv_obj_t* name = lv_label_create(box);
    lv_obj_set_style_text_font(name, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(name, lv_color_hex(0x909090), 0);
    lv_label_set_text_static(name, t.name);
    lv_obj_align(name, LV_ALIGN_TOP_LEFT, 0, 0);
    t.value = lv_label_create(box);
    lv_obj_set_style_text_font(t.value, &lv_font_montserrat_48, 0);
    lv_label_set_text_static(t.value, "--");
    lv_obj_align(t.value, LV_ALIGN_BOTTOM_LEFT, 0, 4);
    t.unitLabel = lv_label_create(box);
    lv_obj_set_style_text_font(t.unitLabel, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(t.unitLabel, lv_color_hex(0x909090), 0);
    lv_label_set_text_static(t.unitLabel, t.unit);
    lv_obj_align(t.unitLabel, LV_ALIGN_BOTTOM_RIGHT, 0, -4);
  }
  return scr;
}

void updateTech(int64_t nowUs) {
  SignalStore& store = signalStore();
  for (Tile& t : tiles) {
    const SignalValue v = store.get(t.id, nowUs, t.maxAgeUs);
    char text[sizeof t.shown] = "--";
    if (v.valid() && v.quality != felink::Quality::kStale) std::snprintf(text, sizeof text, t.format, static_cast<double>(v.value));
    if (std::strcmp(text, t.shown) != 0) {
      std::strcpy(t.shown, text);
      lv_label_set_text_static(t.value, t.shown);
    }
    lv_obj_set_style_text_color(t.value, lv_color_hex(qualityColor(v)), 0);
  }
}

lv_obj_t* buildDiag() {
  lv_obj_t* scr = screenBase("DIAGNOSTICA");
  for (int i = 0; i < kDiagLines; ++i) {
    diagLines[i] = lv_label_create(scr);
    lv_obj_set_style_text_font(diagLines[i], &font_check, 0);
    lv_obj_set_style_text_color(diagLines[i], lv_color_hex(0x00FF41), 0);
    lv_label_set_text_static(diagLines[i], "");
    diagShown[i][0] = '\0';
    lv_obj_set_pos(diagLines[i], 24, 60 + i * 28);
  }
  return scr;
}

void updateDiag(int64_t nowUs) {
  static int64_t lastUs = 0;
  static uint32_t lastFrames = 0;
  static unsigned framesPerS = 0;
  const LinkStats ls = linkStats();
  if (nowUs - lastUs >= 1000000) {  // trame al secondo
    framesPerS = static_cast<unsigned>(ls.frames - lastFrames);
    lastFrames = ls.frames;
    lastUs = nowUs;
  }
  const blackbox::Stats bb = blackbox::stats();
  const unsigned up = static_cast<unsigned>(nowUs / 1000000);
  char line[kDiagLines][72];
  std::snprintf(line[0], 72, "FIRMWARE      %s  (%s)", fw::kVersion, esp_ota_get_running_partition()->label);
  std::snprintf(line[1], 72, "ACCESO DA     %02u:%02u:%02u", up / 3600, up / 60 % 60, up % 60);
  std::snprintf(line[2], 72, "FLUIDITA      %u FPS", static_cast<unsigned>(sysstats::fps.load()));
  std::snprintf(line[3], 72, "CPU0 / CPU1   %u%% / %u%%", static_cast<unsigned>(sysstats::cpu[0].load()),
                static_cast<unsigned>(sysstats::cpu[1].load()));
  std::snprintf(line[4], 72, "LUMINOSITA    %d%% a %u Hz", backlight::percent(), static_cast<unsigned>(backlight::frequency()));
  std::snprintf(line[5], 72, "COLLEGAMENTO  %s  %s  %u trame/s", ls.simulated ? "SIMULATO" : "UART",
                linkAlive(nowUs) ? "ATTIVO" : "ASSENTE", framesPerS);
  std::snprintf(line[6], 72, "  ERRORI      %u scartate, %u perse", static_cast<unsigned>(ls.errors),
                static_cast<unsigned>(ls.lostSeq));
  std::snprintf(line[7], 72, "SCATOLA NERA  %u/%u campioni", static_cast<unsigned>(bb.filled), static_cast<unsigned>(bb.capacity));
  std::snprintf(line[8], 72, "  EVENTI      %u salvati, %u falliti, %u cancellati", static_cast<unsigned>(bb.eventsSaved),
                static_cast<unsigned>(bb.eventsFailed), static_cast<unsigned>(bb.eventsDeleted));
  std::snprintf(line[9], 72, "  MEMORIA     %u / %u KB%s", static_cast<unsigned>(bb.fsUsedKb), static_cast<unsigned>(bb.fsTotalKb),
                bb.fsMounted ? "" : "  NON MONTATA");
  std::snprintf(line[10], 72, "ETICHETTE     %u", static_cast<unsigned>(labels::count()));
  std::snprintf(line[11], 72, "RAM INTERNA   %u KB liberi", static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_INTERNAL) / 1024));
  std::snprintf(line[12], 72, "PSRAM         %u KB liberi", static_cast<unsigned>(heap_caps_get_free_size(MALLOC_CAP_SPIRAM) / 1024));
  std::snprintf(line[13], 72, "IA            modello non presente");
  for (int i = 0; i < kDiagLines; ++i) {
    if (std::strcmp(line[i], diagShown[i]) == 0) continue;
    std::strcpy(diagShown[i], line[i]);
    lv_label_set_text_static(diagLines[i], diagShown[i]);
  }
}
}  // namespace pages
