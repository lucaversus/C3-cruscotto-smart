// Sequenza d'avvio (interfaccia-requisiti rev B): apertura in stile "Matrix" con il codice
// che scende sullo sfondo, controlli del sistema elencati uno alla volta con l'esito, GO solo
// quando le candelette hanno finito il preriscaldo e tutti i controlli sono superati.
// In caso di errore resta l'elenco di ciò che non va, poi si passa comunque alla dashboard.
#include "startup.h"

#include <cstdio>
#include <cstring>
#include <initializer_list>

#include "blackbox.h"
#include "dash_logic.h"
#include "esp_heap_caps.h"
#include "esp_random.h"
#include "fe_link.h"
#include "link.h"
#include "signal_store.h"
#include "startup_logic.h"

LV_FONT_DECLARE(font_speed);

namespace startup {
namespace {
// Pioggia solo ai lati del pannello (opaco): sotto il pannello non verrebbe vista ma
// costerebbe un ridisegno a ogni passo.
constexpr int kPanelW = 620, kSideCols = 4, kColumns = 2 * kSideCols, kRainChars = 18, kRainStep = 21;
constexpr uint32_t kMatrixGreen = 0x00FF41;

struct Rain {
  lv_obj_t* label;
  char text[kRainChars * 2 + 1];
  int y, speed;
};
Rain rain[kColumns];

struct Line {
  const char* name;
  boot::State state;
  lv_obj_t* label;   // nome a sinistra
  lv_obj_t* status;  // esito allineato a destra: non esce dal pannello
  char shown[16];    // esito visualizzato: si ridisegna solo se cambia
};
// Controlli in ordine di comparsa. Moduli non ancora installati: "N/D", esclusi dal GO.
Line lines[] = {
    {"DISPLAY 800X480", boot::State::kPending, nullptr, nullptr, ""},
    {"MEMORIA PSRAM", boot::State::kPending, nullptr, nullptr, ""},
    {"FILE SYSTEM", boot::State::kPending, nullptr, nullptr, ""},
    {"COLLEGAMENTO FRONT-END", boot::State::kPending, nullptr, nullptr, ""},
    {"TENSIONE BATTERIA", boot::State::kPending, nullptr, nullptr, ""},
    {"TEMPERATURA ACQUA", boot::State::kPending, nullptr, nullptr, ""},
    {"IMU", boot::State::kPending, nullptr, nullptr, ""},
    {"NTC DISPLAY", boot::State::kPending, nullptr, nullptr, ""},
    {"RICEZIONE VAN", boot::State::kAbsent, nullptr, nullptr, ""},
    {"K-LINE", boot::State::kAbsent, nullptr, nullptr, ""},
    {"AUDIO", boot::State::kAbsent, nullptr, nullptr, ""},
    {"MODELLO IA", boot::State::kAbsent, nullptr, nullptr, ""},
    {"CANDELETTE", boot::State::kPending, nullptr, nullptr, ""},
};
constexpr int kLines = sizeof lines / sizeof lines[0];

lv_obj_t* screen = nullptr;
lv_obj_t* panel = nullptr;
lv_obj_t* result = nullptr;
lv_obj_t* goShadowObj = nullptr;
const lv_font_t* const kCheckFont = &lv_font_unscii_16;  // carattere dei controlli
int64_t startUs = 0, endUs = 0, lastRainUs = 0;
boot::Phase finalPhase = boot::Phase::kChecking;
bool switched = false;

void randomText(char* out) {
  static const char kChars[] = "0123456789ABCDEF<>/*+=#$%&@";
  for (int i = 0; i < kRainChars; ++i) {
    out[2 * i] = kChars[esp_random() % (sizeof kChars - 1)];
    out[2 * i + 1] = '\n';
  }
  out[2 * kRainChars - 1] = '\0';
}

const char* stateText(const Line& l, uint32_t ms) {
  switch (l.state) {
    case boot::State::kOk: return "OK";
    case boot::State::kFail: return "ERRORE";
    case boot::State::kAbsent: return "N/D";
    default: return &l == &lines[kLines - 1] ? "PRERISCALDO" : ((ms / 300) % 2 ? "..." : "..");
  }
}

uint32_t stateColor(boot::State s) {
  return s == boot::State::kOk ? kMatrixGreen : s == boot::State::kFail ? 0xFF2020
         : s == boot::State::kAbsent ? 0x707070 : 0xFFB000;
}

// Esito di ogni controllo, ricalcolato finché è in attesa.
boot::State evaluate(int i, int64_t nowUs, uint32_t ms) {
  SignalStore& store = signalStore();
  auto fresh = [&](uint16_t id, int64_t maxAgeUs, float& v) {
    const SignalValue s = store.get(id, nowUs, maxAgeUs);
    v = s.value;
    return s.valid() && s.quality != felink::Quality::kStale && s.quality != felink::Quality::kError;
  };
  float v = 0;
  switch (i) {
    case 0: return boot::State::kOk;  // la schermata è visibile: pannello e LVGL avviati
    case 1: return heap_caps_get_free_size(MALLOC_CAP_SPIRAM) > 1024 * 1024 ? boot::State::kOk : boot::State::kFail;
    case 2: return blackbox::stats().fsMounted ? boot::State::kOk : boot::State::kFail;
    case 3: return boot::dataCheck(linkAlive(nowUs), true, ms);
    case 4: { const bool f = fresh(felink::sig::kBatteryV, 3000000, v); return boot::dataCheck(f, v > 11.0f && v < 15.5f, ms); }
    case 5: { const bool f = fresh(felink::sig::kCoolantC, 3000000, v); return boot::dataCheck(f, v > -40.0f && v < 130.0f, ms); }
    case 6: { const bool f = fresh(felink::sig::kAccelX, 1000000, v); return boot::dataCheck(f, v > -4.0f && v < 4.0f, ms); }
    case 7: { const bool f = fresh(felink::sig::kNtcDisplayC, 3000000, v); return boot::dataCheck(f, v > -40.0f && v < 90.0f, ms); }
    case 12: {
      const bool f = fresh(felink::sig::kWarningFlags, 1000000, v);
      return boot::glowCheck(f, (static_cast<uint32_t>(v) & dash::kGlowPlugs) != 0, ms);
    }
    default: return lines[i].state;  // N/D: modulo non installato
  }
}

void showLine(int i, uint32_t ms) {
  Line& l = lines[i];
  const char* text = stateText(l, ms);
  if (std::strcmp(text, l.shown) == 0) return;
  if (l.shown[0] == '\0') lv_label_set_text_fmt(l.label, "> %s", l.name);  // prima comparsa
  std::snprintf(l.shown, sizeof l.shown, "%s", text);
  lv_label_set_text_static(l.status, l.shown);
  lv_obj_set_style_text_color(l.label, lv_color_hex(stateColor(l.state)), 0);
  lv_obj_set_style_text_color(l.status, lv_color_hex(stateColor(l.state)), 0);
}
}  // namespace

void build() {
  screen = lv_obj_create(nullptr);
  lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
  lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);
  for (int c = 0; c < kColumns; ++c) {
    Rain& r = rain[c];
    r.label = lv_label_create(screen);
    lv_obj_set_style_text_font(r.label, &lv_font_unscii_16, 0);
    lv_obj_set_style_text_color(r.label, lv_color_hex(0x00A030), 0);
    lv_obj_set_style_text_opa(r.label, 90 + esp_random() % 120, 0);
    randomText(r.text);
    lv_label_set_text_static(r.label, r.text);
    r.y = -static_cast<int>(esp_random() % 480);
    r.speed = 6 + esp_random() % 12;
    const int x = c < kSideCols ? c * kRainStep + 2 : 800 - (kColumns - c) * kRainStep + 4;
    lv_obj_set_pos(r.label, x, r.y);
  }
  panel = lv_obj_create(screen);
  lv_obj_set_size(panel, kPanelW, 420);
  lv_obj_center(panel);
  lv_obj_clear_flag(panel, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_bg_color(panel, lv_color_black(), 0);
  lv_obj_set_style_bg_opa(panel, LV_OPA_COVER, 0);
  lv_obj_set_style_border_color(panel, lv_color_hex(kMatrixGreen), 0);
  lv_obj_set_style_border_width(panel, 2, 0);
  lv_obj_set_style_radius(panel, 8, 0);
  lv_obj_set_style_bg_grad_color(panel, lv_color_hex(0x002008), 0);  // rilievo: luce in alto
  lv_obj_set_style_bg_grad_dir(panel, LV_GRAD_DIR_VER, 0);
  lv_obj_set_style_shadow_color(panel, lv_color_hex(kMatrixGreen), 0);  // alone verde
  lv_obj_set_style_shadow_width(panel, 24, 0);
  lv_obj_set_style_shadow_opa(panel, LV_OPA_50, 0);
  lv_obj_t* title = lv_label_create(panel);
  lv_obj_set_style_text_font(title, &lv_font_montserrat_28, 0);
  lv_obj_set_style_text_color(title, lv_color_hex(kMatrixGreen), 0);
  lv_label_set_text_static(title, "C3+AI  CONTROLLO SISTEMA");
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, -4);
  for (int i = 0; i < kLines; ++i) {
    for (lv_obj_t** part : {&lines[i].label, &lines[i].status}) {
      *part = lv_label_create(panel);
      lv_obj_set_style_text_font(*part, kCheckFont, 0);
      lv_label_set_text_static(*part, "");
    }
    lv_obj_set_pos(lines[i].label, 4, 36 + i * 24);
    lv_obj_align(lines[i].status, LV_ALIGN_TOP_RIGHT, -4, 36 + i * 24);
  }
  lv_obj_t* goShadow = lv_label_create(screen);  // ombra del GO
  lv_obj_set_style_text_font(goShadow, &font_speed, 0);
  lv_obj_set_style_text_color(goShadow, lv_color_hex(0x004010), 0);
  lv_label_set_text_static(goShadow, "GO");
  lv_obj_align(goShadow, LV_ALIGN_CENTER, 6, 6);
  lv_obj_add_flag(goShadow, LV_OBJ_FLAG_HIDDEN);
  goShadowObj = goShadow;
  result = lv_label_create(screen);
  lv_obj_set_style_text_font(result, &font_speed, 0);
  lv_obj_set_style_text_color(result, lv_color_hex(kMatrixGreen), 0);
  lv_label_set_text_static(result, "GO");
  lv_obj_center(result);
  lv_obj_add_flag(result, LV_OBJ_FLAG_HIDDEN);
  lv_scr_load(screen);
}

bool update(int64_t nowUs, lv_obj_t* next) {
  if (switched) return false;
  if (startUs == 0) startUs = nowUs;
  const uint32_t ms = static_cast<uint32_t>((nowUs - startUs) / 1000);

  if (nowUs - lastRainUs >= 50000) {  // pioggia di codice a 20 passi al secondo
    lastRainUs = nowUs;
    for (Rain& r : rain) {
      r.y += r.speed;
      if (r.y > 480) {
        r.y = -kRainChars * 16 - static_cast<int>(esp_random() % 200);
        randomText(r.text);
        lv_label_set_text_static(r.label, r.text);
      }
      lv_obj_set_y(r.label, r.y);
    }
  }

  if (finalPhase == boot::Phase::kChecking) {
    int pending = 0, failed = 0;
    const int shown = static_cast<int>(ms / boot::kStepMs);
    for (int i = 0; i < kLines; ++i) {
      if (i >= shown) { ++pending; continue; }
      if (lines[i].state == boot::State::kPending) lines[i].state = evaluate(i, nowUs, ms);
      showLine(i, ms);
      if (lines[i].state == boot::State::kPending) ++pending;
      if (lines[i].state == boot::State::kFail) ++failed;
    }
    finalPhase = boot::phase(pending, failed, ms);
    if (finalPhase != boot::Phase::kChecking) {
      endUs = nowUs;
      if (finalPhase == boot::Phase::kGo) {
        lv_obj_add_flag(panel, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(goShadowObj, LV_OBJ_FLAG_HIDDEN);
        lv_obj_clear_flag(result, LV_OBJ_FLAG_HIDDEN);
      } else {
        lv_obj_set_style_border_color(panel, lv_color_hex(0xFF2020), 0);
      }
      printf("ui_idf avvio: %s dopo %u ms\n", finalPhase == boot::Phase::kGo ? "GO" : "CONTROLLI FALLITI",
             static_cast<unsigned>(ms));
    }
    return true;
  }
  const int64_t showUs = (finalPhase == boot::Phase::kGo ? boot::kGoShowMs : boot::kFailShowMs) * 1000LL;
  if (nowUs - endUs >= showUs) {
    lv_scr_load_anim(next, LV_SCR_LOAD_ANIM_FADE_ON, 400, 0, true);  // la schermata d'avvio viene liberata
    switched = true;
    return false;
  }
  return true;
}

}  // namespace startup
