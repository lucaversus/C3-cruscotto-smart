// Pagina 1 "Dashboard" (D-041, interfaccia-requisiti rev B). Barra dei giri a tutta
// larghezza con numeri x100 all'interno e inizio smussato fino a 1000 giri; acqua in
// verticale a sinistra e carburante a destra; velocità grande al centro; spie che compaiono
// solo se accese sopra la fascia dei dati secondari, prova lampade all'avvio, riquadro
// grande per gli avvisi. Legge solo l'archivio dei segnali.
#include "dashboard.h"

#include <cstdio>
#include <cstring>

#include "dash_logic.h"
#include "fe_link.h"
#include "labels.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"

LV_FONT_DECLARE(font_speed);  // Montserrat Medium 170 px, solo cifre (tools/genera-font-velocita.py)

namespace dashboard {
namespace {
constexpr int kRpmX = 20, kRpmY = 12, kRpmW = 760, kRpmH = 64;
constexpr int kSideY = 150, kSideW = 44, kSideH = 260;  // barre verticali acqua e carburante

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
lv_obj_t* speedLabel = nullptr;
lv_obj_t* coolantBar = nullptr;
lv_obj_t* coolantLabel = nullptr;
lv_obj_t* fuelBar = nullptr;
lv_obj_t* fuelLabel = nullptr;
lv_obj_t* secondaryLabel = nullptr;
lv_obj_t* alertBox = nullptr;
lv_obj_t* alertLabel = nullptr;
lv_obj_t* statusLabel = nullptr;
int64_t startUs = 0, speedShownUs = 0;
int shownSpeed = -2, shownCoolant = -2, shownFuel = -2;
uint32_t shownRpmColor = 1, shownCoolantColor = 1, shownFuelColor = 1;
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
  lv_obj_clear_flag(b, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_radius(b, 6, LV_PART_MAIN);
  lv_obj_set_style_radius(b, 6, LV_PART_INDICATOR);
  lv_obj_set_style_bg_color(b, lv_color_hex(0x262626), LV_PART_MAIN);
  return b;
}

// Smusso della barra dei giri: fino a 1000 giri il bordo superiore scende in diagonale
// quasi fino all'angolo in basso a sinistra (richiesta dell'utente 23/10/2026). Triangolo
// nero disegnato sopra la barra: costa molto meno di una maschera su tutta la barra.
void rpmBevelEvent(lv_event_t* e) {
  if (lv_event_get_code(e) != LV_EVENT_DRAW_MAIN) return;
  lv_area_t a;
  lv_obj_get_coords(lv_event_get_target(e), &a);
  lv_draw_rect_dsc_t dsc;
  lv_draw_rect_dsc_init(&dsc);
  dsc.bg_color = lv_color_black();
  dsc.bg_opa = LV_OPA_COVER;
  const lv_point_t pts[3] = {{static_cast<lv_coord_t>(a.x1 - 1), static_cast<lv_coord_t>(a.y1 - 1)},
                             {static_cast<lv_coord_t>(a.x2), static_cast<lv_coord_t>(a.y1 - 1)},
                             {static_cast<lv_coord_t>(a.x1 - 1), static_cast<lv_coord_t>(a.y2 - 8)}};
  lv_draw_triangle(lv_event_get_draw_ctx(e), &dsc, pts);
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

void setColor(lv_obj_t* b, uint32_t color, uint32_t& shown) {
  if (color == shown) return;
  lv_obj_set_style_bg_color(b, lv_color_hex(color), LV_PART_INDICATOR);
  shown = color;
}
}  // namespace

void build() {
  lv_obj_t* screen = lv_scr_act();
  lv_obj_set_style_bg_color(screen, lv_color_black(), 0);
  lv_obj_clear_flag(screen, LV_OBJ_FLAG_SCROLLABLE);

  // Giri: barra a tutta larghezza; numeri x100 dentro la barra, sopra il colore.
  rpmBar = bar(screen, kRpmW, kRpmH, 0, dash::kRpmMax);
  lv_obj_set_pos(rpmBar, kRpmX, kRpmY);
  for (int k = 1; k <= dash::kRpmMax / 1000; ++k) {
    const int x = kRpmW * k * 1000 / dash::kRpmMax;
    lv_obj_t* tick = lv_obj_create(rpmBar);
    lv_obj_remove_style_all(tick);
    lv_obj_set_style_bg_color(tick, lv_color_hex(0xFFFFFF), 0);
    lv_obj_set_style_bg_opa(tick, LV_OPA_60, 0);
    lv_obj_set_size(tick, 2, 14);
    lv_obj_set_pos(tick, x - 1, kRpmH - 14);
    if (k == dash::kRpmMax / 1000) lv_obj_add_flag(tick, LV_OBJ_FLAG_HIDDEN);
    lv_obj_t* num = label(rpmBar, &lv_font_montserrat_28, 0xFFFFFF);
    lv_label_set_text_fmt(num, "%d", k * 10);
    lv_obj_update_layout(num);
    const int w = lv_obj_get_width(num);
    lv_obj_set_pos(num, k == dash::kRpmMax / 1000 ? kRpmW - w - 10 : x - w / 2, 8);
  }
  lv_obj_t* bevel = lv_obj_create(screen);
  lv_obj_remove_style_all(bevel);
  lv_obj_set_pos(bevel, kRpmX, kRpmY);
  lv_obj_set_size(bevel, kRpmW * 1000 / dash::kRpmMax, kRpmH);
  lv_obj_clear_flag(bevel, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_event_cb(bevel, rpmBevelEvent, LV_EVENT_DRAW_MAIN, nullptr);
  lv_obj_t* rpmUnit = label(screen, &lv_font_montserrat_14, 0x909090);
  lv_label_set_text_static(rpmUnit, "giri/min x100");
  lv_obj_align(rpmUnit, LV_ALIGN_TOP_RIGHT, -20, kRpmY + kRpmH + 2);

  // Fascia dei dati secondari: le spie vi compaiono sopra quando accese.
  secondaryLabel = label(screen, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_align(secondaryLabel, LV_ALIGN_TOP_MID, 0, 104);

  // Velocità al centro.
  speedLabel = label(screen, &font_speed, 0xFFFFFF);
  lv_obj_align(speedLabel, LV_ALIGN_TOP_MID, 0, 150);  // larghezza sul contenuto: ridisegno minimo
  lv_obj_t* speedUnit = label(screen, &lv_font_montserrat_28, 0x909090);
  lv_label_set_text_static(speedUnit, "km/h");
  lv_obj_align(speedUnit, LV_ALIGN_TOP_MID, 0, 345);

  // Acqua a sinistra e carburante a destra, barre verticali colorate per intero.
  struct Side { lv_obj_t** barObj; lv_obj_t** value; const char* name; int min, max; bool left; };
  const Side sides[] = {{&coolantBar, &coolantLabel, "ACQUA", 40, 130, true},
                        {&fuelBar, &fuelLabel, "GASOLIO", 0, 100, false}};
  for (const Side& s : sides) {
    *s.barObj = bar(screen, kSideW, kSideH, s.min, s.max);
    lv_obj_align(*s.barObj, s.left ? LV_ALIGN_TOP_LEFT : LV_ALIGN_TOP_RIGHT, s.left ? 20 : -20, kSideY);
    lv_obj_t* name = label(screen, &lv_font_montserrat_14, 0x909090);
    lv_label_set_text_static(name, s.name);
    lv_obj_align_to(name, *s.barObj, s.left ? LV_ALIGN_OUT_TOP_LEFT : LV_ALIGN_OUT_TOP_RIGHT, 0, -4);
    *s.value = label(screen, &lv_font_montserrat_28, 0xFFFFFF);
    lv_obj_set_width(*s.value, 110);
    lv_obj_set_style_text_align(*s.value, s.left ? LV_TEXT_ALIGN_LEFT : LV_TEXT_ALIGN_RIGHT, 0);
    lv_obj_align_to(*s.value, *s.barObj, s.left ? LV_ALIGN_OUT_BOTTOM_LEFT : LV_ALIGN_OUT_BOTTOM_RIGHT, 0, 8);
  }

  statusLabel = label(screen, &lv_font_montserrat_14, 0xFFB000);
  lv_obj_align(statusLabel, LV_ALIGN_BOTTOM_MID, 0, -10);

  // Riquadro degli avvisi, in primo piano tra le barre verticali.
  alertBox = lv_obj_create(screen);
  lv_obj_set_size(alertBox, 560, 170);
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
  const SignalValue fuelV = store.get(felink::sig::kFuelPct, nowUs, 10000000);
  const SignalValue battV = store.get(felink::sig::kBatteryV, nowUs, 3000000);
  const SignalValue outV = store.get(felink::sig::kOutsideC, nowUs, 10000000);
  const SignalValue lightsV = store.get(felink::sig::kLightsFlags, nowUs, 1000000);
  const SignalValue warnV = store.get(felink::sig::kWarningFlags, nowUs, 1000000);
  auto fresh = [](const SignalValue& v) { return v.valid() && v.quality != felink::Quality::kStale; };

  const int rpm = fresh(rpmV) ? static_cast<int>(rpmV.value + 0.5f) : 0;
  lv_bar_set_value(rpmBar, rpm, LV_ANIM_OFF);
  setColor(rpmBar, dash::rpmColor(rpm), shownRpmColor);

  const int speed = fresh(speedV) ? static_cast<int>(speedV.value + 0.5f) : -1;
  // Velocità aggiornata al massimo 4 volte al secondo: lettura stabile, come i tachimetri
  // digitali, e meno ridisegni del carattere grande.
  if (speed != shownSpeed && nowUs - speedShownUs >= 250000) {
    speedShownUs = nowUs;
    if (speed < 0) lv_label_set_text_static(speedLabel, "-");
    else lv_label_set_text_fmt(speedLabel, "%d", speed);
    shownSpeed = speed;
  }

  const bool coolValid = fresh(coolV);
  const int coolant = coolValid ? static_cast<int>(coolV.value + 0.5f) : -1;
  if (coolant != shownCoolant) {
    lv_bar_set_value(coolantBar, coolant < 40 ? 40 : coolant, LV_ANIM_OFF);
    if (coolant < 0) lv_label_set_text_static(coolantLabel, "--");
    else lv_label_set_text_fmt(coolantLabel, "%d°", coolant);
    shownCoolant = coolant;
  }
  setColor(coolantBar, coolValid ? dash::coolantColor(coolant) : 0x606060, shownCoolantColor);

  const int fuel = fresh(fuelV) ? static_cast<int>(fuelV.value + 0.5f) : -1;
  if (fuel != shownFuel) {
    lv_bar_set_value(fuelBar, fuel < 0 ? 0 : fuel, LV_ANIM_OFF);
    if (fuel < 0) lv_label_set_text_static(fuelLabel, "--");
    else lv_label_set_text_fmt(fuelLabel, "%d%%", fuel);
    shownFuel = fuel;
  }
  setColor(fuelBar, fuel < 0 ? 0x606060 : dash::fuelColor(fuel), shownFuelColor);

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
