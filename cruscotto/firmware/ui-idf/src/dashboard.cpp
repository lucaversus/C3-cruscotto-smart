// Pagina 1 "Dashboard" (D-041, interfaccia-requisiti rev B). Schermata da viaggio senza
// scritte, solo icone e numeri (utente 23/10/2026). Barra dei giri a tutta larghezza con
// numeri x1000 all'interno e inizio smussato fino a 1000 giri; acqua in verticale a
// sinistra e carburante a destra; velocità grande al centro; spie a icona che compaiono solo
// se accese sopra la fascia dei dati secondari, prova lampade all'avvio, riquadro grande con
// icona per gli avvisi. Legge solo l'archivio dei segnali.
#include "dashboard.h"

#include <cstdio>
#include <cstring>
#include <initializer_list>

#include "dash_logic.h"
#include "fe_link.h"
#include "icons.h"
#include "labels.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"

LV_FONT_DECLARE(font_speed);  // Montserrat ingrossato e arrotondato, solo cifre (tools/genera-font-velocita.py)

namespace dashboard {
namespace {
constexpr int kRpmX = 20, kRpmY = 12, kRpmW = 760, kRpmH = 64;
constexpr int kSideY = 160, kSideW = 48, kSideH = 260;  // barre verticali acqua e carburante
constexpr int kSideIcon = 36, kSideIconY = kSideH - kSideIcon - 8;  // icona dentro la barra, in basso
constexpr int kTurnSize = 64;                           // frecce più grandi delle altre spie
constexpr int kLampStep = 64;                           // passo delle spie (icone 44 px)

struct Lamp {
  uint32_t bit;
  bool warning;  // true: campo spie 0x0008, false: campo luci 0x0007
  const lv_img_dsc_t* icon;
  uint32_t color;
  int col, row;  // posto fisso: col -1/-2 = frecce ai lati; righe 0-1 sotto la barra dei giri
  lv_obj_t* obj;
};

// Spie dinamiche a icona: nascoste se spente. Riga 0 sicurezza e ritenuta, riga 1 motore,
// luci e avvisi minori.
Lamp lamps[] = {
    {dash::kTurnLeft, false, &icon_turn_left_64, 0x00E040, -1, 0, nullptr},
    {dash::kTurnRight, false, &icon_turn_right_64, 0x00E040, -2, 0, nullptr},
    {dash::kBrake, true, &icon_brake_44, 0xFF2020, 0, 0, nullptr},
    {dash::kOilPressure, true, &icon_oil_44, 0xFF2020, 1, 0, nullptr},
    {dash::kCoolantHot, true, &icon_coolant_44, 0xFF2020, 2, 0, nullptr},
    {dash::kCharge, true, &icon_battery_44, 0xFF2020, 3, 0, nullptr},
    {dash::kParkBrake, true, &icon_park_brake_44, 0xFF2020, 4, 0, nullptr},
    {dash::kAirbag, true, &icon_airbag_44, 0xFF2020, 5, 0, nullptr},
    {dash::kSeatBelt, true, &icon_seat_belt_44, 0xFF2020, 6, 0, nullptr},
    {dash::kEngine, true, &icon_engine_44, 0xFFB000, 0, 1, nullptr},
    {dash::kGlowPlugs, true, &icon_glow_plugs_44, 0xFFB000, 1, 1, nullptr},
    {dash::kAbs, true, &icon_abs_44, 0xFFB000, 2, 1, nullptr},
    {dash::kHighBeam, false, &icon_high_beam_44, 0x2060FF, 3, 1, nullptr},
    {dash::kFrontFog, false, &icon_front_fog_44, 0x00E040, 4, 1, nullptr},
    {dash::kRearFog, false, &icon_rear_fog_44, 0xFFB000, 5, 1, nullptr},
    {dash::kDoorOpen, true, &icon_door_open_44, 0xFFB000, 6, 1, nullptr},
    {dash::kFuelLow, true, &icon_fuel_44, 0xFFB000, 7, 1, nullptr},
};
constexpr int kRowCount[2] = {7, 8};

lv_obj_t* rpmBar = nullptr;
lv_obj_t* speedLabel = nullptr;
lv_obj_t* coolantBar = nullptr;
lv_obj_t* coolantLabel = nullptr;
lv_obj_t* fuelBar = nullptr;
lv_obj_t* fuelLabel = nullptr;

// Icona dentro una barra verticale: due copie ritagliate al livello, scura sulla parte
// riempita e chiara su quella vuota, così resta leggibile mentre il livello sale.
struct SideIcon {
  lv_obj_t* light = nullptr;  // contenitore della parte vuota (sopra il livello)
  lv_obj_t* dark = nullptr;   // contenitore della parte riempita (sotto il livello)
  lv_obj_t* darkIcon = nullptr;
  int boundary = -1;          // riga del livello, dall'alto della barra
};
SideIcon coolantIcon, fuelIcon;
lv_obj_t* battLabel = nullptr;
lv_obj_t* outLabel = nullptr;
lv_obj_t* alertBox = nullptr;
lv_obj_t* alertIcon = nullptr;
lv_obj_t* statusLabel = nullptr;
int64_t startUs = 0, speedShownUs = 0;
int shownSpeed = -2, shownCoolant = -2, shownFuel = -2;
uint32_t shownRpmColor = 1, shownCoolantColor = 1, shownFuelColor = 1;
dash::Alert shownAlert = dash::Alert::kNone;
const char* shownStatus = nullptr;
char shownBatt[16] = "", shownOut[16] = "";

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

// Icona del riquadro di avviso.
const lv_img_dsc_t* alertIconFor(dash::Alert a) {
  switch (a) {
    case dash::Alert::kLinkLost: return &icon_link_lost_110;
    case dash::Alert::kOilPressure: return &icon_oil_110;
    case dash::Alert::kBrake: return &icon_brake_110;
    case dash::Alert::kCoolantHot: return &icon_coolant_110;
    case dash::Alert::kCharge: return &icon_battery_110;
    default: return &icon_link_lost_110;
  }
}

lv_obj_t* icon(lv_obj_t* parent, const lv_img_dsc_t* src, uint32_t color) {
  lv_obj_t* i = lv_img_create(parent);
  lv_img_set_src(i, src);
  lv_obj_set_style_img_recolor(i, lv_color_hex(color), 0);
  lv_obj_set_style_img_recolor_opa(i, LV_OPA_COVER, 0);
  return i;
}

void setText(lv_obj_t* l, const char* text, char* shown, size_t size) {
  if (strcmp(text, shown) == 0) return;
  std::snprintf(shown, size, "%s", text);
  lv_label_set_text_static(l, shown);
}

// Sposta il taglio tra icona chiara e scura alla riga del livello (fill = 0..kSideH).
void setSideLevel(SideIcon& si, int fill) {
  const int boundary = kSideH - (fill < 0 ? 0 : fill > kSideH ? kSideH : fill);
  if (boundary == si.boundary) return;
  si.boundary = boundary;
  lv_obj_set_pos(si.light, 0, 0);
  lv_obj_set_size(si.light, kSideW, boundary);
  lv_obj_set_pos(si.dark, 0, boundary);
  lv_obj_set_size(si.dark, kSideW, kSideH - boundary);
  lv_obj_set_pos(si.darkIcon, (kSideW - kSideIcon) / 2, kSideIconY - boundary);
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
    lv_obj_t* num = label(rpmBar, &lv_font_montserrat_48, 0xFFFFFF);
    lv_label_set_text_fmt(num, "%d", k);
    lv_obj_update_layout(num);
    const int w = lv_obj_get_width(num);
    lv_obj_set_pos(num, k == dash::kRpmMax / 1000 ? kRpmW - w - 12 : x - w / 2, (kRpmH - lv_obj_get_height(num)) / 2);
  }
  lv_obj_t* bevel = lv_obj_create(screen);
  lv_obj_remove_style_all(bevel);
  lv_obj_set_pos(bevel, kRpmX, kRpmY);
  lv_obj_set_size(bevel, kRpmW * 1000 / dash::kRpmMax, kRpmH);
  lv_obj_clear_flag(bevel, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_add_event_cb(bevel, rpmBevelEvent, LV_EVENT_DRAW_MAIN, nullptr);

  // Fascia dei dati secondari (icona e valore): le spie vi compaiono sopra quando accese.
  lv_obj_t* strip = lv_obj_create(screen);
  lv_obj_remove_style_all(strip);
  lv_obj_set_size(strip, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
  lv_obj_set_flex_flow(strip, LV_FLEX_FLOW_ROW);
  lv_obj_set_flex_align(strip, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER, LV_FLEX_ALIGN_CENTER);
  lv_obj_set_style_pad_column(strip, 10, 0);
  icon(strip, &icon_battery_28, 0x909090);
  battLabel = label(strip, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_t* gap = lv_obj_create(strip);
  lv_obj_remove_style_all(gap);
  lv_obj_set_size(gap, 40, 1);
  icon(strip, &icon_outside_28, 0x909090);
  outLabel = label(strip, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_align(strip, LV_ALIGN_TOP_MID, 0, 96);

  // Velocità al centro.
  speedLabel = label(screen, &font_speed, 0xFFFFFF);
  lv_obj_align(speedLabel, LV_ALIGN_TOP_MID, 0, 165);  // larghezza sul contenuto: ridisegno minimo

  // Acqua a sinistra e carburante a destra, barre verticali colorate per intero.
  struct Side {
    lv_obj_t** barObj; lv_obj_t** value; SideIcon* sideIcon; const lv_img_dsc_t* sign; int min, max; bool left;
  };
  const Side sides[] = {{&coolantBar, &coolantLabel, &coolantIcon, &icon_coolant_36, 40, 130, true},
                        {&fuelBar, &fuelLabel, &fuelIcon, &icon_fuel_36, 0, 100, false}};
  for (const Side& s : sides) {
    *s.barObj = bar(screen, kSideW, kSideH, s.min, s.max);
    lv_obj_align(*s.barObj, s.left ? LV_ALIGN_TOP_LEFT : LV_ALIGN_TOP_RIGHT, s.left ? 20 : -20, kSideY);
    for (lv_obj_t** part : {&s.sideIcon->light, &s.sideIcon->dark}) {
      *part = lv_obj_create(*s.barObj);
      lv_obj_remove_style_all(*part);
      lv_obj_clear_flag(*part, LV_OBJ_FLAG_SCROLLABLE);
      lv_obj_t* img = icon(*part, s.sign, part == &s.sideIcon->light ? 0xA0A0A0 : 0x000000);
      lv_obj_set_pos(img, (kSideW - kSideIcon) / 2, kSideIconY);
      if (part == &s.sideIcon->dark) s.sideIcon->darkIcon = img;
    }
    *s.value = label(screen, &lv_font_montserrat_28, 0xFFFFFF);
    lv_obj_set_width(*s.value, 110);
    lv_obj_set_style_text_align(*s.value, s.left ? LV_TEXT_ALIGN_LEFT : LV_TEXT_ALIGN_RIGHT, 0);
    lv_obj_align_to(*s.value, *s.barObj, s.left ? LV_ALIGN_OUT_BOTTOM_LEFT : LV_ALIGN_OUT_BOTTOM_RIGHT, 0, 8);
  }

  statusLabel = label(screen, &lv_font_montserrat_14, 0xFFB000);
  lv_obj_align(statusLabel, LV_ALIGN_BOTTOM_MID, 0, -10);

  // Riquadro degli avvisi, in primo piano tra le barre verticali.
  alertBox = lv_obj_create(screen);
  lv_obj_set_size(alertBox, 300, 170);
  lv_obj_align(alertBox, LV_ALIGN_CENTER, 0, 40);
  lv_obj_clear_flag(alertBox, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_border_width(alertBox, 6, 0);
  lv_obj_set_style_radius(alertBox, 12, 0);
  alertIcon = icon(alertBox, &icon_link_lost_110, 0xFFFFFF);
  lv_obj_center(alertIcon);
  lv_obj_add_flag(alertBox, LV_OBJ_FLAG_HIDDEN);

  // Spie: create per ultime, quindi disegnate sopra a tutto (anche al riquadro).
  for (Lamp& l : lamps) {
    l.obj = icon(screen, l.icon, l.color);
    lv_obj_set_style_bg_color(l.obj, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(l.obj, LV_OPA_COVER, 0);
    const int y = 88 + l.row * 54;
    if (l.col == -1) lv_obj_set_pos(l.obj, 20, y - (kTurnSize - 44) / 2);
    else if (l.col == -2) lv_obj_align(l.obj, LV_ALIGN_TOP_RIGHT, -20, y - (kTurnSize - 44) / 2);
    else lv_obj_set_pos(l.obj, 400 - kRowCount[l.row] * kLampStep / 2 + l.col * kLampStep + (kLampStep - 44) / 2, y);
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
    setSideLevel(coolantIcon, coolant < 40 ? 0 : (coolant - 40) * kSideH / (130 - 40));
    if (coolant < 0) lv_label_set_text_static(coolantLabel, "--");
    else lv_label_set_text_fmt(coolantLabel, "%d°", coolant);
    shownCoolant = coolant;
  }
  setColor(coolantBar, coolValid ? dash::coolantColor(coolant) : 0x606060, shownCoolantColor);

  const int fuel = fresh(fuelV) ? static_cast<int>(fuelV.value + 0.5f) : -1;
  if (fuel != shownFuel) {
    lv_bar_set_value(fuelBar, fuel < 0 ? 0 : fuel, LV_ANIM_OFF);
    setSideLevel(fuelIcon, fuel < 0 ? 0 : fuel * kSideH / 100);
    if (fuel < 0) lv_label_set_text_static(fuelLabel, "--");
    else lv_label_set_text_fmt(fuelLabel, "%d%%", fuel);
    shownFuel = fuel;
  }
  setColor(fuelBar, fuel < 0 ? 0x606060 : dash::fuelColor(fuel), shownFuelColor);

  // Dati secondari (coperti dalle spie accese).
  char text[16] = "--";
  if (fresh(battV)) std::snprintf(text, sizeof text, "%.1f V", static_cast<double>(battV.value));
  setText(battLabel, text, shownBatt, sizeof shownBatt);
  std::snprintf(text, sizeof text, "--");
  if (fresh(outV)) std::snprintf(text, sizeof text, "%.0f°", static_cast<double>(outV.value));
  setText(outLabel, text, shownOut, sizeof shownOut);

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
    if (alert == dash::Alert::kNone) {
      lv_obj_add_flag(alertBox, LV_OBJ_FLAG_HIDDEN);
    } else {
      // Collegamento assente in ambra (mancano i dati), guasti del veicolo in rosso.
      const bool link = alert == dash::Alert::kLinkLost;
      const uint32_t color = link ? 0xFFB000 : 0xFF2020;
      lv_img_set_src(alertIcon, alertIconFor(alert));
      lv_obj_set_style_img_recolor(alertIcon, lv_color_hex(color), 0);
      lv_obj_set_style_border_color(alertBox, lv_color_hex(color), 0);
      lv_obj_set_style_bg_color(alertBox, lv_color_hex(link ? 0x302000 : 0x400000), 0);
      lv_obj_clear_flag(alertBox, LV_OBJ_FLAG_HIDDEN);
    }
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
