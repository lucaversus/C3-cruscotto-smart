// Pagina 1 "Dashboard" (D-041, interfaccia-requisiti rev B). Barre lineari colorate per
// intero (giri verde->rosso, acqua bianco->azzurro->rosso), velocità al centro, spie che
// compaiono solo se accese sopra la fascia dei dati secondari, prova lampade all'avvio,
// riquadro grande per gli avvisi. Legge solo l'archivio dei segnali.
#include "dashboard.h"

#include <cstdio>
#include <cstring>

#include "dash_logic.h"
#include "fe_link.h"
#include "labels.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"

namespace dashboard {
namespace {
constexpr int kRpmDigits = 4;
constexpr int kDigitWidth = 34;

struct Lamp {
  uint32_t bit;
  bool warning;  // true: campo spie 0x0008, false: campo luci 0x0007
  const char* text;
  uint32_t color;
  int col, row;  // posto fisso: col -1/-2 = frecce ai lati; righe 0-2 sotto la barra dei giri
  lv_obj_t* obj;
};

// Spie dinamiche: nascoste se spente. Riga 0 sicurezza (sempre visibili se accese), riga 1
// motore e ritenuta, riga 2 luci e avvisi minori. Testi provvisori: icone da definire.
Lamp lamps[] = {
    {dash::kTurnLeft, false, LV_SYMBOL_LEFT, 0x00E040, -1, 0, nullptr},
    {dash::kTurnRight, false, LV_SYMBOL_RIGHT, 0x00E040, -2, 0, nullptr},
    {dash::kBrake, true, "FRENI", 0xFF2020, 0, 0, nullptr},
    {dash::kOilPressure, true, "OLIO", 0xFF2020, 1, 0, nullptr},
    {dash::kCoolantHot, true, "ACQUA", 0xFF2020, 2, 0, nullptr},
    {dash::kCharge, true, "BATT", 0xFF2020, 3, 0, nullptr},
    {dash::kParkBrake, true, "F.MANO", 0xFF2020, 4, 0, nullptr},
    {dash::kEngine, true, "MOTORE", 0xFFB000, 0, 1, nullptr},
    {dash::kGlowPlugs, true, "CAND.", 0xFFB000, 1, 1, nullptr},
    {dash::kAbs, true, "ABS", 0xFFB000, 2, 1, nullptr},
    {dash::kAirbag, true, "AIRBAG", 0xFF2020, 3, 1, nullptr},
    {dash::kSeatBelt, true, "CINT.", 0xFF2020, 4, 1, nullptr},
    {dash::kHighBeam, false, "ABBAG.", 0x2060FF, 0, 2, nullptr},
    {dash::kFrontFog, false, "FENDI", 0x00E040, 1, 2, nullptr},
    {dash::kRearFog, false, "RETRO", 0xFFB000, 2, 2, nullptr},
    {dash::kDoorOpen, true, "PORTE", 0xFFB000, 3, 2, nullptr},
    {dash::kFuelLow, true, "RISERVA", 0xFFB000, 4, 2, nullptr},
};

lv_obj_t* rpmBar = nullptr;
lv_obj_t* rpmDigits[kRpmDigits] = {};
lv_obj_t* speedSeg[3][7] = {};  // cifre a sette segmenti: centinaia, decine, unità
lv_obj_t* coolantBar = nullptr;
lv_obj_t* coolantLabel = nullptr;
lv_obj_t* secondaryLabel = nullptr;
lv_obj_t* alertBox = nullptr;
lv_obj_t* alertLabel = nullptr;
lv_obj_t* statusLabel = nullptr;
int64_t startUs = 0;
int shownRpm = -1, shownSpeed = -2, shownCoolant = -2;
uint32_t shownRpmColor = 1, shownCoolantColor = 1;
dash::Alert shownAlert = dash::Alert::kNone;
const char* shownStatus = nullptr;
char shownSecondary[96] = "";

lv_obj_t* label(lv_obj_t* parent, const lv_font_t* font, uint32_t color) {
  lv_obj_t* l = lv_label_create(parent);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, lv_color_hex(color), 0);
  lv_label_set_text_static(l, "");
  return l;
}

lv_obj_t* bar(lv_obj_t* parent, int w, int h, int min, int max) {
  lv_obj_t* b = lv_bar_create(parent);
  lv_obj_set_size(b, w, h);
  lv_bar_set_range(b, min, max);
  lv_obj_set_style_radius(b, 6, LV_PART_MAIN);
  lv_obj_set_style_radius(b, 6, LV_PART_INDICATOR);
  lv_obj_set_style_bg_color(b, lv_color_hex(0x262626), LV_PART_MAIN);
  return b;
}

const char* alertText(dash::Alert a) {
  switch (a) {
    case dash::Alert::kLinkLost: return "COLLEGAMENTO ASSENTE\ndati dell'auto non disponibili";
    case dash::Alert::kOilPressure: return "PRESSIONE OLIO\nfermarsi appena possibile";
    case dash::Alert::kBrake: return "IMPIANTO FRENANTE\ncontrollare";
    case dash::Alert::kCoolantHot: return "TEMPERATURA ACQUA ALTA\nridurre il carico";
    case dash::Alert::kCharge: return "BATTERIA NON IN CARICA\ncontrollare";
    default: return "";
  }
}

void showRpm(int rpm) {
  static const char* const kDigitText[] = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"};
  int value = rpm < 0 ? 0 : rpm;
  for (int i = kRpmDigits - 1; i >= 0; --i) {
    const bool blank = (value == 0 && i < kRpmDigits - 1) || rpm < 0;
    const char* text = rpm < 0 && i == kRpmDigits - 1 ? "-" : blank ? "" : kDigitText[value % 10];
    if (strcmp(lv_label_get_text(rpmDigits[i]), text) != 0) lv_label_set_text_static(rpmDigits[i], text);
    value /= 10;
  }
}
}  // namespace

void build() {
  lv_obj_t* screen = lv_scr_act();
  lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
  lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);

  // Giri: barra lineare a tutta larghezza con scala in migliaia.
  rpmBar = bar(screen, 760, 46, 0, dash::kRpmMax);
  lv_obj_align(rpmBar, LV_ALIGN_TOP_MID, 0, 14);
  for (int k = 0; k <= dash::kRpmMax / 1000; ++k) {
    lv_obj_t* tick = label(screen, &lv_font_montserrat_14, 0x909090);
    lv_label_set_text_fmt(tick, "%d", k);
    lv_obj_set_pos(tick, 20 + k * 760 * 1000 / dash::kRpmMax - (k == dash::kRpmMax / 1000 ? 10 : 0), 64);
  }
  lv_obj_t* rpmUnit = label(screen, &lv_font_montserrat_14, 0x909090);
  lv_label_set_text_static(rpmUnit, "x1000 giri/min");
  lv_obj_align(rpmUnit, LV_ALIGN_TOP_MID, 0, 64);

  // Fascia dei dati secondari: le spie vi compaiono sopra quando accese.
  secondaryLabel = label(screen, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_align(secondaryLabel, LV_ALIGN_TOP_MID, 0, 104);

  // Velocità al centro con cifre a sette segmenti (nessun carattere grande disponibile)
  // e giri in cifre a destra.
  for (int d = 0; d < 3; ++d) {
    const int x0 = 400 - 135 + d * 95, y0 = 190, w = 72, h = 130, t = 14;
    const int seg[7][4] = {{t, 0, w - 2 * t, t},           {w - t, t, t, h / 2 - t},
                           {w - t, h / 2, t, h / 2 - t},   {t, h - t, w - 2 * t, t},
                           {0, h / 2, t, h / 2 - t},       {0, t, t, h / 2 - t},
                           {t, h / 2 - t / 2, w - 2 * t, t}};
    for (int k = 0; k < 7; ++k) {
      lv_obj_t* o = lv_obj_create(screen);
      lv_obj_remove_style_all(o);
      lv_obj_set_pos(o, x0 + seg[k][0], y0 + seg[k][1]);
      lv_obj_set_size(o, seg[k][2], seg[k][3]);
      lv_obj_set_style_bg_color(o, lv_color_white(), 0);
      lv_obj_set_style_bg_opa(o, LV_OPA_COVER, 0);
      lv_obj_set_style_radius(o, 4, 0);
      lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
      speedSeg[d][k] = o;
    }
  }
  lv_obj_t* speedUnit = label(screen, &lv_font_montserrat_28, 0x909090);
  lv_label_set_text_static(speedUnit, "km/h");
  lv_obj_align(speedUnit, LV_ALIGN_TOP_MID, 0, 330);
  for (int i = 0; i < kRpmDigits; ++i) {
    rpmDigits[i] = label(screen, &lv_font_montserrat_48, 0xFFFFFF);
    lv_obj_set_width(rpmDigits[i], kDigitWidth);
    lv_obj_set_style_text_align(rpmDigits[i], LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_pos(rpmDigits[i], 640 + i * kDigitWidth, 250);
  }
  lv_obj_t* rpmText = label(screen, &lv_font_montserrat_14, 0x909090);
  lv_label_set_text_static(rpmText, "giri/min");
  lv_obj_set_pos(rpmText, 670, 308);

  // Temperatura acqua: barra lineare in basso, colore dell'intera barra.
  coolantBar = bar(screen, 460, 36, 40, 130);
  lv_obj_align(coolantBar, LV_ALIGN_BOTTOM_LEFT, 20, -20);
  coolantLabel = label(screen, &lv_font_montserrat_28, 0xFFFFFF);
  lv_obj_align_to(coolantLabel, coolantBar, LV_ALIGN_OUT_TOP_LEFT, 0, -8);

  statusLabel = label(screen, &lv_font_montserrat_14, 0xFFB000);
  lv_obj_align(statusLabel, LV_ALIGN_BOTTOM_RIGHT, -20, -26);

  // Riquadro degli avvisi, in primo piano, sotto la fascia delle spie.
  alertBox = lv_obj_create(screen);
  lv_obj_set_size(alertBox, 620, 170);
  lv_obj_align(alertBox, LV_ALIGN_CENTER, 0, 40);
  lv_obj_clear_flag(alertBox, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_bg_color(alertBox, lv_color_hex(0x400000), 0);
  lv_obj_set_style_border_color(alertBox, lv_color_hex(0xFF2020), 0);
  lv_obj_set_style_border_width(alertBox, 6, 0);
  lv_obj_set_style_radius(alertBox, 12, 0);
  alertLabel = label(alertBox, &lv_font_montserrat_28, 0xFFFFFF);
  lv_obj_set_style_text_align(alertLabel, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_center(alertLabel);
  lv_obj_add_flag(alertBox, LV_OBJ_FLAG_HIDDEN);

  // Spie: create per ultime, quindi disegnate sopra a tutto (anche al riquadro).
  for (Lamp& l : lamps) {
    l.obj = lv_label_create(screen);
    lv_label_set_text_static(l.obj, l.text);
    lv_obj_set_style_text_font(l.obj, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(l.obj, lv_color_black(), 0);
    lv_obj_set_style_bg_color(l.obj, lv_color_hex(l.color), 0);
    lv_obj_set_style_bg_opa(l.obj, LV_OPA_COVER, 0);
    lv_obj_set_style_radius(l.obj, 6, 0);
    lv_obj_set_style_pad_hor(l.obj, 6, 0);
    lv_obj_set_style_pad_ver(l.obj, 2, 0);
    const int y = 96 + l.row * 40;
    if (l.col == -1) lv_obj_set_pos(l.obj, 20, y);
    else if (l.col == -2) lv_obj_align(l.obj, LV_ALIGN_TOP_RIGHT, -20, y);
    else lv_obj_set_pos(l.obj, 90 + l.col * 124, y);
    lv_obj_add_flag(l.obj, LV_OBJ_FLAG_HIDDEN);
  }
}

void update(int64_t nowUs) {
  if (startUs == 0) startUs = nowUs;
  SignalStore& store = signalStore();
  const SignalValue rpmV = store.get(felink::sig::kRpm, nowUs, 500000);
  const SignalValue speedV = store.get(felink::sig::kSpeedKmh, nowUs, 1000000);
  const SignalValue coolV = store.get(felink::sig::kCoolantC, nowUs, 3000000);
  const SignalValue battV = store.get(felink::sig::kBatteryV, nowUs, 3000000);
  const SignalValue outV = store.get(felink::sig::kOutsideC, nowUs, 10000000);
  const SignalValue lightsV = store.get(felink::sig::kLightsFlags, nowUs, 1000000);
  const SignalValue warnV = store.get(felink::sig::kWarningFlags, nowUs, 1000000);
  auto fresh = [](const SignalValue& v) { return v.valid() && v.quality != felink::Quality::kStale; };

  const int rpm = fresh(rpmV) ? static_cast<int>(rpmV.value + 0.5f) : -1;
  lv_bar_set_value(rpmBar, rpm < 0 ? 0 : rpm, LV_ANIM_OFF);
  const uint32_t rpmColor = dash::rpmColor(rpm < 0 ? 0 : rpm);
  if (rpmColor != shownRpmColor) {
    lv_obj_set_style_bg_color(rpmBar, lv_color_hex(rpmColor), LV_PART_INDICATOR);
    shownRpmColor = rpmColor;
  }
  if (rpm != shownRpm) {
    showRpm(rpm);
    shownRpm = rpm;
  }

  const int speed = fresh(speedV) ? static_cast<int>(speedV.value + 0.5f) : -1;
  if (speed != shownSpeed) {
    for (int d = 0; d < 3; ++d) {
      const uint8_t mask = dash::speedSegments(speed, 2 - d);
      for (int k = 0; k < 7; ++k) {
        lv_obj_t* o = speedSeg[d][k];
        const bool on = (mask >> k) & 1;
        if (on == lv_obj_has_flag(o, LV_OBJ_FLAG_HIDDEN)) {
          if (on) lv_obj_clear_flag(o, LV_OBJ_FLAG_HIDDEN);
          else lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
        }
      }
    }
    shownSpeed = speed;
  }

  const bool coolValid = fresh(coolV);
  const int coolant = coolValid ? static_cast<int>(coolV.value + 0.5f) : -1;
  if (coolant != shownCoolant) {
    lv_bar_set_value(coolantBar, coolant < 40 ? 40 : coolant, LV_ANIM_OFF);
    if (coolant < 0) lv_label_set_text_static(coolantLabel, "Acqua --");
    else lv_label_set_text_fmt(coolantLabel, "Acqua %d °C", coolant);
    shownCoolant = coolant;
  }
  const uint32_t coolColor = coolValid ? dash::coolantColor(coolant) : 0x606060;
  if (coolColor != shownCoolantColor) {
    lv_obj_set_style_bg_color(coolantBar, lv_color_hex(coolColor), LV_PART_INDICATOR);
    shownCoolantColor = coolColor;
  }

  // Dati secondari (coperti dalle spie accese).
  char secondary[96];
  char batt[16] = "--", out[16] = "--";
  if (fresh(battV)) std::snprintf(batt, sizeof batt, "%.1f V", static_cast<double>(battV.value));
  if (fresh(outV)) std::snprintf(out, sizeof out, "%.0f °C", static_cast<double>(outV.value));
  std::snprintf(secondary, sizeof secondary, "Batteria %s     Esterna %s", batt, out);
  if (strcmp(secondary, shownSecondary) != 0) {
    std::strcpy(shownSecondary, secondary);
    lv_label_set_text(secondaryLabel, shownSecondary);
  }

  // Spie: prova lampade all'avvio, poi solo quelle accese; dati assenti = nessuna spia,
  // ma il riquadro "COLLEGAMENTO ASSENTE" impedisce di scambiarlo per "nessun guasto".
  const uint32_t sinceStartMs = static_cast<uint32_t>((nowUs - startUs) / 1000);
  const bool check = dash::bulbCheck(sinceStartMs);
  const uint32_t lights = fresh(lightsV) ? static_cast<uint32_t>(lightsV.value) : 0;
  const uint32_t warnings = fresh(warnV) ? static_cast<uint32_t>(warnV.value) : 0;
  for (Lamp& l : lamps) {
    const bool on = check || ((l.warning ? warnings : lights) & l.bit) != 0;
    if (on == lv_obj_has_flag(l.obj, LV_OBJ_FLAG_HIDDEN)) {
      if (on) lv_obj_clear_flag(l.obj, LV_OBJ_FLAG_HIDDEN);
      else lv_obj_add_flag(l.obj, LV_OBJ_FLAG_HIDDEN);
    }
  }

  const dash::Alert alert = check ? dash::Alert::kNone : dash::alertFor(linkAlive(nowUs), warnings, coolant, coolValid);
  if (alert != shownAlert) {
    lv_label_set_text_static(alertLabel, alertText(alert));
    if (alert == dash::Alert::kNone) lv_obj_add_flag(alertBox, LV_OBJ_FLAG_HIDDEN);
    else lv_obj_clear_flag(alertBox, LV_OBJ_FLAG_HIDDEN);
    shownAlert = alert;
  }

  const int64_t lastLabel = labels::lastLabelUs();
  const char* status = (lastLabel != 0 && nowUs - lastLabel < 3000000) ? "SEGNALAZIONE REGISTRATA"
                       : rpmV.quality == felink::Quality::kSimulated  ? "DEMO - dati simulati"
                                                                       : "";
  if (status != shownStatus) {
    lv_label_set_text_static(statusLabel, status);
    shownStatus = status;
  }
}

}  // namespace dashboard
