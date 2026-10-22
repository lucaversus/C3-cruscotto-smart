// Logica pura della dashboard (D-041, interfaccia-requisiti rev B): colori delle barre,
// soglie degli avvisi e spie. Nessuna dipendenza da LVGL: provata sul PC (host-tests).
#pragma once
#include <stdint.h>

namespace dash {

// Giri (scelta dell'utente 23/10/2026): verde fino a 2500, sfumatura fino ad arancione pieno
// a 3000, arancione fino a 3500, da 3500 rosso acceso senza sfumatura. Riferimento motore
// DV4TD 8HZ: 50 kW a 4000 giri/min. Limitatore non trovato: fondo scala 5000 da verificare.
constexpr int kRpmMax = 5000;
constexpr int kRpmGreenMax = 2500;
constexpr int kRpmOrangeFull = 3000;
constexpr int kRpmRed = 3500;
// Temperatura acqua: soglie PROPOSTE, nessun dato del costruttore trovato (termostato,
// ventola, allarme): da fissare con le temperature registrate dal logger (OBD PID 0x05).
constexpr int kCoolantWhiteMax = 50;
constexpr int kCoolantAzureFrom = 75;
constexpr int kCoolantAzureTo = 100;
constexpr int kCoolantRedFull = 110;
constexpr int kCoolantAlarm = 110;  // riquadro di avviso da questo valore

constexpr uint32_t kGreen = 0x00C040, kOrange = 0xFF8000, kRed = 0xFF1010, kWhite = 0xFFFFFF, kAzure = 0x00C0FF;

constexpr uint32_t channel(uint32_t c, int shift) { return (c >> shift) & 0xFF; }

// Miscela lineare a..b con peso 0..256 (256 = tutto b).
constexpr uint32_t mix(uint32_t a, uint32_t b, int w) {
  return (((channel(a, 16) * (256 - w) + channel(b, 16) * w) >> 8) << 16) |
         (((channel(a, 8) * (256 - w) + channel(b, 8) * w) >> 8) << 8) |
         ((channel(a, 0) * (256 - w) + channel(b, 0) * w) >> 8);
}

constexpr int weight(int v, int from, int to) {
  return v <= from ? 0 : v >= to ? 256 : (v - from) * 256 / (to - from);
}

// Colore dell'intera barra dei giri.
constexpr uint32_t rpmColor(int rpm) {
  return rpm >= kRpmRed ? kRed : mix(kGreen, kOrange, weight(rpm, kRpmGreenMax, kRpmOrangeFull));
}

// Colore dell'intera barra della temperatura acqua.
constexpr uint32_t coolantColor(int c) {
  return c <= kCoolantWhiteMax ? kWhite
         : c < kCoolantAzureFrom ? mix(kWhite, kAzure, weight(c, kCoolantWhiteMax, kCoolantAzureFrom))
         : c <= kCoolantAzureTo  ? kAzure
                                 : mix(kAzure, kRed, weight(c, kCoolantAzureTo, kCoolantRedFull));
}

// Campi di bit dei segnali 0x0007 (luci) e 0x0008 (spie), definiti dal protocollo fe_link:
// il front-end li ricava dai messaggi VAN (4FC, 524, 564) quando saranno verificati.
enum Light : uint32_t { kTurnLeft = 1u << 0, kTurnRight = 1u << 1, kLowBeam = 1u << 2, kHighBeam = 1u << 3,
                        kFrontFog = 1u << 4, kRearFog = 1u << 5, kSideLights = 1u << 6 };
enum Warning : uint32_t { kBrake = 1u << 0, kOilPressure = 1u << 1, kCoolantHot = 1u << 2, kCharge = 1u << 3,
                          kGlowPlugs = 1u << 4, kEngine = 1u << 5, kAbs = 1u << 6, kAirbag = 1u << 7,
                          kSeatBelt = 1u << 8, kFuelLow = 1u << 9, kDoorOpen = 1u << 10, kParkBrake = 1u << 11 };
// Spie di sicurezza: sempre visibili quando accese, anche con il riquadro di avviso.
constexpr uint32_t kSafetyWarnings = kBrake | kOilPressure | kCoolantHot | kCharge;

// Carburante: barra bianca, ambra in riserva (soglia PROPOSTA, da tarare con il dato VAN).
constexpr int kFuelReserve = 10;
constexpr uint32_t kFuelNormal = 0xE0E0E0, kAmber = 0xFFB000;
constexpr uint32_t fuelColor(int pct) { return pct <= kFuelReserve ? kAmber : kFuelNormal; }
static_assert(fuelColor(50) == kFuelNormal && fuelColor(kFuelReserve) == kAmber, "carburante");

// Prova lampade: tutte le spie accese per i primi kBulbCheckMs dall'avvio dell'interfaccia.
constexpr uint32_t kBulbCheckMs = 3000;
constexpr bool bulbCheck(uint32_t sinceStartMs) { return sinceStartMs < kBulbCheckMs; }

// Motivo del riquadro di avviso, in ordine di priorità.
enum class Alert : uint8_t { kNone, kLinkLost, kOilPressure, kBrake, kCoolantHot, kCharge };

constexpr Alert alertFor(bool linkAlive, uint32_t warnings, int coolantC, bool coolantValid) {
  return !linkAlive                                                ? Alert::kLinkLost
         : (warnings & kOilPressure)                               ? Alert::kOilPressure
         : (warnings & kBrake)                                     ? Alert::kBrake
         : ((warnings & kCoolantHot) || (coolantValid && coolantC >= kCoolantAlarm)) ? Alert::kCoolantHot
         : (warnings & kCharge)                                    ? Alert::kCharge
                                                                   : Alert::kNone;
}

static_assert(rpmColor(0) == kGreen && rpmColor(kRpmGreenMax) == kGreen, "verde fino a 2500");
static_assert(rpmColor(kRpmOrangeFull) == kOrange && rpmColor(kRpmRed - 1) == kOrange, "arancione 3000-3499");
static_assert(rpmColor(kRpmRed) == kRed && rpmColor(kRpmMax) == kRed, "rosso da 3500 senza sfumatura");
static_assert(coolantColor(20) == kWhite && coolantColor(90) == kAzure && coolantColor(120) == kRed, "acqua");
static_assert(alertFor(false, 0, 90, true) == Alert::kLinkLost, "collegamento assente prima di tutto");
static_assert(alertFor(true, 0, kCoolantAlarm, true) == Alert::kCoolantHot, "acqua alta");
static_assert(alertFor(true, 0, kCoolantAlarm, false) == Alert::kNone, "dato non valido: nessun allarme acqua");

}  // namespace dash
