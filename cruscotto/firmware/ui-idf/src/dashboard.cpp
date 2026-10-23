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

#include "backlight.h"
#include "dash_logic.h"
#include "fe_link.h"
#include "icons.h"
#include "labels.h"
#include "link.h"
#include "lvgl.h"
#include "signal_store.h"
#include "sysstats.h"
#include "version.h"

LV_FONT_DECLARE(font_speed);  // Montserrat ingrossato e arrotondato, solo cifre (tools/genera-font-velocita.py)

namespace dashboard {
namespace {
constexpr int kRpmX = 20, kRpmY = 12, kRpmW = 760, kRpmH = 64;
constexpr int kSideY = 174, kSideW = 76, kSideH = 286;  // barre verticali acqua e carburante
constexpr int kSideValueY = 10;                         // valore dentro la barra, in alto
constexpr int kSideIcon = 42, kSideIconY = kSideH - kSideIcon - 8;  // icona dentro la barra, in basso
constexpr int kTurnSize = 84;                           // frecce più grandi delle altre spie
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
    {dash::kTurnLeft, false, &icon_turn_left_84, 0x00E040, -1, 0, nullptr},
    {dash::kTurnRight, false, &icon_turn_right_84, 0x00E040, -2, 0, nullptr},
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
lv_obj_t* cpuLabel = nullptr;
lv_obj_t* ecoBar = nullptr;
lv_obj_t* coolantBar = nullptr;
lv_obj_t* coolantLabel = nullptr;
lv_obj_t* fuelBar = nullptr;
lv_obj_t* fuelLabel = nullptr;

// Icona dentro una barra verticale: due copie ritagliate al livello, scura sulla parte
// riempita e chiara su quella vuota, così resta leggibile mentre il livello sale.
struct SideIcon {
  lv_obj_t* light = nullptr;  // contenitore della parte vuota (sopra il livello)
  lv_obj_t* lightIcon = nullptr;  // colore della barra: resta riconoscibile a barra vuota
  lv_obj_t* dark = nullptr;   // contenitore della parte riempita (sotto il livello)
  lv_obj_t* darkIcon = nullptr;
  lv_obj_t* darkValue = nullptr;  // valore in nero sulla parte riempita
  int boundary = -1;          // riga del livello, dall'alto della barra
};
SideIcon coolantIcon, fuelIcon;
lv_obj_t* battLabel = nullptr;
lv_obj_t* outLabel = nullptr;
lv_obj_t* cabinLabel = nullptr;
lv_obj_t* alertBox = nullptr;
lv_obj_t* alertIcon = nullptr;
lv_obj_t* statusLabel = nullptr;
int64_t startUs = 0, speedShownUs = 0;
int shownSpeed = -2, shownCoolant = -2, shownFuel = -2;
uint32_t shownRpmColor = 1, shownCoolantColor = 1, shownFuelColor = 1, shownEcoColor = 1;
int shownEco = -1;
dash::Alert shownAlert = dash::Alert::kNone;
const char* shownStatus = nullptr;
char shownBatt[16] = "", shownOut[16] = "", shownCabin[16] = "";

lv_obj_t* label(lv_obj_t* parent, const lv_font_t* font, uint32_t color) {
  lv_obj_t* l = lv_label_create(parent);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, lv_color_hex(color), 0);
  lv_label_set_text_static(l, "");
  return l;
}

// Barra con effetto tridimensionale: canale incavato (scuro in alto, più chiaro in basso,
// bordo sottile) e riempimento a rilievo (luce su un lato, ombra sull'altro).
lv_obj_t* bar(lv_obj_t* parent, int w, int h, int min, int max) {
  lv_obj_t* b = lv_bar_create(parent);
  lv_obj_set_size(b, w, h);
  lv_bar_set_range(b, min, max);
  lv_obj_clear_flag(b, LV_OBJ_FLAG_SCROLLABLE);
  const lv_grad_dir_t dir = w > h ? LV_GRAD_DIR_VER : LV_GRAD_DIR_HOR;
  lv_obj_set_style_radius(b, 8, LV_PART_MAIN);
  lv_obj_set_style_radius(b, 8, LV_PART_INDICATOR);
  lv_obj_set_style_bg_color(b, lv_color_hex(0x0C0C0C), LV_PART_MAIN);
  lv_obj_set_style_bg_grad_color(b, lv_color_hex(0x343434), LV_PART_MAIN);
  lv_obj_set_style_bg_grad_dir(b, dir, LV_PART_MAIN);
  lv_obj_set_style_border_color(b, lv_color_hex(0x4A4A4A), LV_PART_MAIN);
  lv_obj_set_style_border_width(b, 1, LV_PART_MAIN);
  lv_obj_set_style_bg_grad_dir(b, dir, LV_PART_INDICATOR);
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
  lv_obj_set_pos(si.darkValue, 0, kSideValueY - boundary);
}

// Valore scritto nelle due copie (chiara e scura) dentro la barra.
void setSideText(SideIcon& si, lv_obj_t* lightValue, const char* text) {
  lv_label_set_text(lightValue, text);
  lv_label_set_text(si.darkValue, text);
}

// Colore della barra; icona (parte vuota) e valore numerico seguono lo stesso colore.
void setColor(lv_obj_t* b, uint32_t color, uint32_t& shown, lv_obj_t* lightIcon = nullptr, lv_obj_t* value = nullptr) {
  if (color == shown) return;
  lv_obj_set_style_bg_color(b, lv_color_hex(dash::light(color)), LV_PART_INDICATOR);
  lv_obj_set_style_bg_grad_color(b, lv_color_hex(dash::shade(color)), LV_PART_INDICATOR);
  if (lightIcon) lv_obj_set_style_img_recolor(lightIcon, lv_color_hex(color), 0);
  if (value) lv_obj_set_style_text_color(value, lv_color_hex(color), 0);
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

  // Dati secondari (le spie vi compaiono sopra quando accese): sagoma della C3 prima serie al
  // centro sopra la velocità con la temperatura dell'abitacolo dentro e quella esterna
  // accanto; a sinistra la tensione della batteria.
  lv_obj_t* car = icon(screen, &icon_c3_176x88, 0x808080);
  lv_obj_align(car, LV_ALIGN_TOP_MID, 0, 92);
  cabinLabel = label(screen, &lv_font_montserrat_28, 0xFFFFFF);
  lv_obj_set_width(cabinLabel, 100);
  lv_obj_set_style_text_align(cabinLabel, LV_TEXT_ALIGN_CENTER, 0);
  lv_obj_align_to(cabinLabel, car, LV_ALIGN_CENTER, -6, -8);
  outLabel = label(screen, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_set_width(outLabel, 90);
  lv_obj_align_to(outLabel, car, LV_ALIGN_OUT_RIGHT_MID, 10, 0);
  battLabel = label(screen, &lv_font_montserrat_28, 0xB0B0B0);
  lv_obj_set_width(battLabel, 90);
  lv_obj_set_style_text_align(battLabel, LV_TEXT_ALIGN_RIGHT, 0);
  lv_obj_align_to(battLabel, car, LV_ALIGN_OUT_LEFT_MID, -10, 0);
  lv_obj_t* battIcon = icon(screen, &icon_battery_28, 0x808080);
  lv_obj_align_to(battIcon, battLabel, LV_ALIGN_OUT_LEFT_MID, -6, 0);

  // Velocità al centro, senza effetto 3D (richiesta dell'utente 23/10/2026).
  speedLabel = label(screen, &font_speed, 0xFFFFFF);
  lv_obj_align(speedLabel, LV_ALIGN_TOP_MID, 0, 165);  // larghezza sul contenuto: ridisegno minimo

  // Econometro al limite inferiore dello schermo, più corto e più alto.
  ecoBar = bar(screen, 240, 24, 0, dash::kEcoMax * 10);
  lv_obj_align(ecoBar, LV_ALIGN_BOTTOM_MID, 0, -10);

  // Acqua a sinistra e carburante a destra, barre verticali colorate per intero.
  struct Side {
    lv_obj_t** barObj; lv_obj_t** value; SideIcon* sideIcon; const lv_img_dsc_t* sign; int min, max; bool left;
  };
  const Side sides[] = {{&coolantBar, &coolantLabel, &coolantIcon, &icon_coolant_42, 40, 130, true},
                        {&fuelBar, &fuelLabel, &fuelIcon, &icon_fuel_42, 0, 100, false}};
  for (const Side& s : sides) {
    *s.barObj = bar(screen, kSideW, kSideH, s.min, s.max);
    lv_obj_align(*s.barObj, s.left ? LV_ALIGN_TOP_LEFT : LV_ALIGN_TOP_RIGHT, s.left ? 20 : -20, kSideY);
    for (lv_obj_t** part : {&s.sideIcon->light, &s.sideIcon->dark}) {
      *part = lv_obj_create(*s.barObj);
      lv_obj_remove_style_all(*part);
      lv_obj_clear_flag(*part, LV_OBJ_FLAG_SCROLLABLE);
      lv_obj_t* img = icon(*part, s.sign, part == &s.sideIcon->light ? 0xA0A0A0 : 0x000000);
      lv_obj_set_pos(img, (kSideW - kSideIcon) / 2, kSideIconY);
      // Valore con unità dentro la barra, con la stessa inversione di colore dell'icona: del
      // colore della barra sulla parte vuota, nero su quella riempita (anche a barra piena).
      const bool lightPart = part == &s.sideIcon->light;
      lv_obj_t* value = label(*part, &lv_font_montserrat_28, lightPart ? 0xA0A0A0 : 0x000000);
      lv_obj_set_width(value, kSideW);
      lv_obj_set_style_text_align(value, LV_TEXT_ALIGN_CENTER, 0);
      lv_obj_set_pos(value, 0, kSideValueY);
      if (lightPart) {
        s.sideIcon->lightIcon = img;
        *s.value = value;
      } else {
        s.sideIcon->darkIcon = img;
        s.sideIcon->darkValue = value;
      }
    }
  }

  statusLabel = label(screen, &lv_font_montserrat_14, 0xFFB000);
  lv_obj_align(statusLabel, LV_ALIGN_TOP_MID, 0, 392);
  // Carico delle due CPU (dato tecnico provvisorio: andrà nella pagina Diagnostica).
  cpuLabel = label(screen, &lv_font_montserrat_14, 0x808080);
  lv_obj_align(cpuLabel, LV_ALIGN_TOP_MID, 0, 412);

  // Riquadro degli avvisi, in primo piano tra le barre verticali.
  alertBox = lv_obj_create(screen);
  lv_obj_set_size(alertBox, 300, 170);
  lv_obj_align(alertBox, LV_ALIGN_CENTER, 0, 40);
  lv_obj_clear_flag(alertBox, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_style_border_width(alertBox, 6, 0);
  lv_obj_set_style_radius(alertBox, 12, 0);
  lv_obj_set_style_shadow_width(alertBox, 30, 0);  // alone: il riquadro "galleggia" sopra la pagina
  lv_obj_set_style_shadow_spread(alertBox, 4, 0);
  lv_obj_set_style_shadow_color(alertBox, lv_color_hex(0x000000), 0);
  lv_obj_set_style_shadow_opa(alertBox, LV_OPA_COVER, 0);
  alertIcon = icon(alertBox, &icon_link_lost_110, 0xFFFFFF);
  lv_obj_center(alertIcon);
  lv_obj_add_flag(alertBox, LV_OBJ_FLAG_HIDDEN);

  // Spie: create per ultime, quindi disegnate sopra a tutto (anche al riquadro).
  for (Lamp& l : lamps) {
    l.obj = icon(screen, l.icon, l.color);
    lv_obj_set_style_bg_color(l.obj, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(l.obj, LV_OPA_COVER, 0);
    const int y = 88 + l.row * 54;
    if (l.col == -1) lv_obj_set_pos(l.obj, 16, 84);
    else if (l.col == -2) lv_obj_align(l.obj, LV_ALIGN_TOP_RIGHT, -16, 84);
    else lv_obj_set_pos(l.obj, 400 - kRowCount[l.row] * kLampStep / 2 + l.col * kLampStep + (kLampStep - 44) / 2, y);
    lv_obj_add_flag(l.obj, LV_OBJ_FLAG_HIDDEN);
  }
}

void update(int64_t nowUs) {
  if (startUs == 0) startUs = nowUs;
  // Debug a banco: pressione breve di BOOT = nuova prova lampade (RST riavvia con il controllo iniziale).
  static uint32_t shownPresses = labels::bootShortPresses();
  if (labels::bootShortPresses() != shownPresses) {
    shownPresses = labels::bootShortPresses();
    startUs = nowUs;
  }
  SignalStore& store = signalStore();
  const SignalValue rpmV = store.get(felink::sig::kRpm, nowUs, 500000);
  const SignalValue speedV = store.get(felink::sig::kSpeedKmh, nowUs, 1000000);
  const SignalValue coolV = store.get(felink::sig::kCoolantC, nowUs, 3000000);
  const SignalValue fuelV = store.get(felink::sig::kFuelPct, nowUs, 10000000);
  const SignalValue battV = store.get(felink::sig::kBatteryV, nowUs, 3000000);
  const SignalValue ecoV = store.get(felink::sig::kFuelL100, nowUs, 1000000);
  const SignalValue outV = store.get(felink::sig::kOutsideC, nowUs, 10000000);
  const SignalValue cabinV = store.get(felink::sig::kCabinC, nowUs, 10000000);
  const SignalValue lightsV = store.get(felink::sig::kLightsFlags, nowUs, 1000000);
  const SignalValue warnV = store.get(felink::sig::kWarningFlags, nowUs, 1000000);
  auto fresh = [](const SignalValue& v) { return v.valid() && v.quality != felink::Quality::kStale; };

  const int rpm = fresh(rpmV) ? static_cast<int>(rpmV.value + 0.5f) : 0;
  lv_bar_set_value(rpmBar, rpm, LV_ANIM_OFF);
  setColor(rpmBar, dash::rpmBlinkColor(rpm, static_cast<uint32_t>(nowUs / 1000)), shownRpmColor);

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
    char text[16] = "--";
    if (coolant >= 0) std::snprintf(text, sizeof text, "%d°", coolant);
    setSideText(coolantIcon, coolantLabel, text);
    shownCoolant = coolant;
  }
  setColor(coolantBar, coolValid ? dash::coolantColor(coolant) : 0x606060, shownCoolantColor, coolantIcon.lightIcon, coolantLabel);

  const int fuel = fresh(fuelV) ? static_cast<int>(fuelV.value + 0.5f) : -1;
  if (fuel != shownFuel) {
    lv_bar_set_value(fuelBar, fuel < 0 ? 0 : fuel, LV_ANIM_OFF);
    setSideLevel(fuelIcon, fuel < 0 ? 0 : fuel * kSideH / 100);
    char text[16] = "--";
    if (fuel >= 0) std::snprintf(text, sizeof text, "%d%%", fuel);
    setSideText(fuelIcon, fuelLabel, text);
    shownFuel = fuel;
  }
  setColor(fuelBar, fuel < 0 ? 0x606060 : dash::fuelColor(fuel), shownFuelColor, fuelIcon.lightIcon, fuelLabel);

  // Econometro: consumo istantaneo in decimi di l/100 km.
  const int eco = fresh(ecoV) ? static_cast<int>(ecoV.value * 10.0f + 0.5f) : 0;
  if (eco != shownEco) {
    lv_bar_set_value(ecoBar, eco > dash::kEcoMax * 10 ? dash::kEcoMax * 10 : eco, LV_ANIM_OFF);
    shownEco = eco;
  }
  setColor(ecoBar, fresh(ecoV) ? dash::ecoColor(eco) : 0x606060, shownEcoColor);

  // Dati secondari (coperti dalle spie accese).
  char text[16] = "--";
  if (fresh(battV)) std::snprintf(text, sizeof text, "%.1f V", static_cast<double>(battV.value));
  setText(battLabel, text, shownBatt, sizeof shownBatt);
  std::snprintf(text, sizeof text, "--");
  if (fresh(outV)) std::snprintf(text, sizeof text, "%.0f°", static_cast<double>(outV.value));
  setText(outLabel, text, shownOut, sizeof shownOut);
  std::snprintf(text, sizeof text, "--");
  if (fresh(cabinV)) std::snprintf(text, sizeof text, "%.0f°", static_cast<double>(cabinV.value));
  setText(cabinLabel, text, shownCabin, sizeof shownCabin);

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
                       : rpmV.quality == felink::Quality::kSimulated  ? "DEMO - dati simulati - FW " FW_VERSION_TEXT
                                                                       : "";
  if (status != shownStatus) {
    lv_label_set_text_static(statusLabel, status);
    shownStatus = status;
  }
  // Riga di servizio: fluidità, carico delle CPU e luminosità attuale dello schermo.
  static unsigned shownCpu[4] = {101, 101, 0xFFFF, 101};
  const unsigned c0 = sysstats::cpu[0].load(), c1 = sysstats::cpu[1].load(), fps = sysstats::fps.load();
  const unsigned lum = static_cast<unsigned>(backlight::percent());
  static uint32_t shownHz = 0;
  if (c0 != shownCpu[0] || c1 != shownCpu[1] || fps != shownCpu[2] || lum != shownCpu[3] ||
      backlight::frequency() != shownHz) {
    shownHz = backlight::frequency();
    lv_label_set_text_fmt(cpuLabel, "%u FPS   CPU0 %u%%   CPU1 %u%%   LUM %u%% a %u Hz", fps, c0, c1, lum,
                          static_cast<unsigned>(backlight::frequency()));
    shownCpu[0] = c0;
    shownCpu[1] = c1;
    shownCpu[2] = fps;
    shownCpu[3] = lum;
  }
}

}  // namespace dashboard
