// Sequenza d'avvio (interfaccia-requisiti rev B): apertura in stile "Matrix" con il codice
// che scende sullo sfondo e una finestra piccola dove i controlli scorrono con l'esito: quelli
// superati salgono e spariscono, gli errori restano fissi in alto (utente 23/10/2026). GO
// scritto in grande nella finestra solo quando le candelette hanno finito il preriscaldo e
// tutti i controlli sono superati. In caso di errore restano gli errori, poi la dashboard.
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

LV_FONT_DECLARE(font_check);  // Share Tech Mono 20 px con antialias (tools/genera-font-avvio.py)
LV_FONT_DECLARE(font_go);     // Share Tech Mono 120 px, solo "GO"

namespace startup {
namespace {
// Pioggia solo ai lati del pannello (opaco): sotto il pannello non verrebbe vista ma
// costerebbe un ridisegno a ogni passo.
constexpr int kPanelW = 400, kPanelH = 270, kRows = 8, kSideCols = 7, kColumns = 2 * kSideCols, kRainChars = 12, kRainStep = 28;
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
};
// Controlli in ordine di comparsa. Moduli non ancora installati: "N/D", esclusi dal GO.
Line lines[] = {
    {"DISPLAY 800X480", boot::State::kPending},
    {"MEMORIA PSRAM", boot::State::kPending},
    {"FILE SYSTEM", boot::State::kPending},
    {"COLLEGAMENTO FRONT-END", boot::State::kPending},
    {"TENSIONE BATTERIA", boot::State::kPending},
    {"TEMPERATURA ACQUA", boot::State::kPending},
    {"IMU", boot::State::kPending},
    {"NTC DISPLAY", boot::State::kPending},
    {"RICEZIONE VAN", boot::State::kAbsent},
    {"K-LINE", boot::State::kAbsent},
    {"AUDIO", boot::State::kAbsent},
    {"MODELLO IA", boot::State::kAbsent},
    {"CANDELETTE", boot::State::kPending},
};
constexpr int kLines = sizeof lines / sizeof lines[0];

// Righe visibili della finestra: nome a sinistra, esito allineato a destra.
struct Row {
  lv_obj_t* name;
  lv_obj_t* status;
  int line = -1;           // controllo mostrato (-1 = riga vuota)
  const char* text = "";   // esito mostrato: si ridisegna solo se cambia
};
Row rows[kRows];

lv_obj_t* screen = nullptr;
lv_obj_t* panel = nullptr;
lv_obj_t* goLabel = nullptr;
const lv_font_t* const kCheckFont = &font_check;  // carattere dei controlli, stile terminale Matrix
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

// Riempie le righe: prima gli errori (fissi), poi gli ultimi controlli comparsi, così i
// superati scorrono verso l'alto e spariscono.
void showRows(int shown, uint32_t ms) {
  int order[kLines];
  int n = 0;
  for (int i = 0; i < shown && n < kRows; ++i)
    if (lines[i].state == boot::State::kFail) order[n++] = i;
  int others = 0;
  for (int i = 0; i < shown; ++i)
    if (lines[i].state != boot::State::kFail) ++others;
  int skip = others - (kRows - n);
  for (int i = 0; i < shown && n < kRows; ++i) {
    if (lines[i].state == boot::State::kFail) continue;
    if (skip-- > 0) continue;
    order[n++] = i;
  }
  for (int r = 0; r < kRows; ++r) {
    Row& row = rows[r];
    const int line = r < n ? order[r] : -1;
    const char* text = line < 0 ? "" : stateText(lines[line], ms);
    if (line == row.line && std::strcmp(text, row.text) == 0) continue;
    if (line != row.line) {
      if (line < 0) lv_label_set_text_static(row.name, "");
      else lv_label_set_text_fmt(row.name, "> %s", lines[line].name);
    }
    row.line = line;
    row.text = text;
    lv_label_set_text_static(row.status, text);
    if (line >= 0) {
      const lv_color_t c = lv_color_hex(stateColor(lines[line].state));
      lv_obj_set_style_text_color(row.name, c, 0);
      lv_obj_set_style_text_color(row.status, c, 0);
    }
  }
}
}  // namespace

void build() {
  screen = lv_obj_create(nullptr);
  lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
  lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);
  for (int c = 0; c < kColumns; ++c) {
    Rain& r = rain[c];
    r.label = lv_label_create(screen);
    lv_obj_set_style_text_font(r.label, &font_check, 0);
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
  lv_obj_set_size(panel, kPanelW, kPanelH);
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
  lv_obj_set_style_text_font(title, kCheckFont, 0);
  lv_obj_set_style_text_color(title, lv_color_hex(kMatrixGreen), 0);
  lv_label_set_text_static(title, "C3+AI // CONTROLLO SISTEMA");
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, -6);
  for (int r = 0; r < kRows; ++r) {
    for (lv_obj_t** part : {&rows[r].name, &rows[r].status}) {
      *part = lv_label_create(panel);
      lv_obj_set_style_text_font(*part, kCheckFont, 0);
      lv_label_set_text_static(*part, "");
    }
    lv_obj_set_pos(rows[r].name, 0, 24 + r * 24);
    lv_obj_align(rows[r].status, LV_ALIGN_TOP_RIGHT, 0, 24 + r * 24);
  }
  // GO in grande dentro la finestra, con lo stesso carattere dei controlli.
  goLabel = lv_label_create(panel);
  lv_obj_set_style_text_font(goLabel, &font_go, 0);
  lv_obj_set_style_text_color(goLabel, lv_color_hex(kMatrixGreen), 0);
  lv_label_set_text_static(goLabel, "GO");
  lv_obj_align(goLabel, LV_ALIGN_CENTER, 0, 10);
  lv_obj_add_flag(goLabel, LV_OBJ_FLAG_HIDDEN);
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
        r.y = -kRainChars * 24 - static_cast<int>(esp_random() % 200);
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
      if (lines[i].state == boot::State::kPending) ++pending;
      if (lines[i].state == boot::State::kFail) ++failed;
    }
    showRows(shown < kLines ? shown : kLines, ms);
    finalPhase = boot::phase(pending, failed, ms);
    if (finalPhase != boot::Phase::kChecking) {
      endUs = nowUs;
      if (finalPhase == boot::Phase::kGo) {
        for (Row& row : rows) {
          lv_obj_add_flag(row.name, LV_OBJ_FLAG_HIDDEN);
          lv_obj_add_flag(row.status, LV_OBJ_FLAG_HIDDEN);
        }
        lv_obj_clear_flag(goLabel, LV_OBJ_FLAG_HIDDEN);
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
