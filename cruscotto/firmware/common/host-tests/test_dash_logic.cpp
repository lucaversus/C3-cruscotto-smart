// Test sul PC della logica della dashboard (dash_logic.h).
#include <cstdio>
#include <cstdlib>

#include "dash_logic.h"
#include "startup_logic.h"

namespace {
int failures = 0;

void check(bool ok, const char* what) {
  if (!ok) {
    std::printf("FALLITO: %s\n", what);
    ++failures;
  }
}

int red(uint32_t c) { return static_cast<int>((c >> 16) & 0xFF); }
int green(uint32_t c) { return static_cast<int>((c >> 8) & 0xFF); }
}  // namespace

int main() {
  // Sfumatura graduale verde->arancione tra 2500 e 3000: il rosso cresce in modo monotono.
  int lastRed = -1;
  for (int rpm = dash::kRpmGreenMax; rpm <= dash::kRpmOrangeFull; rpm += 50) {
    const uint32_t c = dash::rpmColor(rpm);
    check(red(c) >= lastRed, "giri: sfumatura monotona verde->arancione");
    lastRed = red(c);
  }
  check(dash::rpmColor(2750) != dash::kGreen && dash::rpmColor(2750) != dash::kOrange, "giri: colore intermedio");
  // Da 3500 rosso acceso, senza passaggi intermedi.
  check(dash::rpmColor(3499) == dash::kOrange && dash::rpmColor(3500) == dash::kRed, "giri: salto al rosso");
  check(green(dash::rpmColor(4800)) == green(dash::kRed), "giri: rosso pieno fino al fondo scala");
  check(dash::coolantColor(60) != dash::kWhite && dash::coolantColor(60) != dash::kAzure, "acqua: bianco->azzurro");
  check(dash::coolantColor(105) != dash::kAzure && dash::coolantColor(105) != dash::kRed, "acqua: azzurro->rosso");
  check(dash::coolantColor(dash::kCoolantAzureFrom) == dash::kAzure, "acqua: azzurro dalla zona normale");
  // Priorità degli avvisi.
  check(dash::alertFor(true, dash::kOilPressure | dash::kCharge, 90, true) == dash::Alert::kOilPressure,
        "olio prima della carica");
  check(dash::alertFor(true, dash::kCharge, 90, true) == dash::Alert::kCharge, "carica");
  check(dash::alertFor(true, 0, 90, true) == dash::Alert::kNone, "nessun avviso");
  check(dash::alertFor(true, dash::kGlowPlugs | dash::kFuelLow, 90, true) == dash::Alert::kNone,
        "spie non di sicurezza: nessun riquadro");
  check(dash::fuelColor(11) == dash::kFuelNormal && dash::fuelColor(5) == dash::kAmber, "carburante in riserva");
  // Sequenza d'avvio: GO solo a controlli finiti, nessun errore e candelette spente.
  check(boot::glowCheck(true, true, boot::kGlowMaxMs) == boot::State::kFail, "preriscaldo troppo lungo");
  check(boot::glowCheck(false, false, boot::kWaitMs - 1) == boot::State::kPending, "candelette: attesa dato");
  check(boot::dataCheck(true, false, 0) == boot::State::kFail, "dato fuori intervallo");
  check(boot::phase(0, 0, boot::kMinMs - 1) == boot::Phase::kChecking, "durata minima dell'apertura");
  check(boot::phase(0, 2, boot::kMinMs) == boot::Phase::kFailed, "errori: niente GO");
  // Effetto 3D ed econometro.
  check(dash::light(0x404040) != 0x404040 && red(dash::light(0x404040)) > 0x40, "tinta chiara");
  check(red(dash::shade(0xFF0000)) < 0xFF && red(dash::shade(0xFF0000)) > 0, "tinta scura");
  check(dash::ecoColor(65) != dash::kGreen && dash::ecoColor(65) != 0xFFB000, "econometro: sfumatura");
  // Lampeggio della barra rossa.
  check(dash::rpmBlinkColor(3600, 0) == dash::kRed && dash::rpmBlinkColor(3600, 250) == dash::kRedOff, "lampeggio sopra 3500");
  check(dash::rpmBlinkColor(3400, 250) == dash::kOrange, "arancione fisso");
  // Prova lampade.
  check(dash::bulbCheck(0) && dash::bulbCheck(2999) && !dash::bulbCheck(3000), "prova lampade 3 s");
  if (failures) return EXIT_FAILURE;
  std::printf("test_dash_logic: tutti i controlli superati\n");
  return EXIT_SUCCESS;
}
