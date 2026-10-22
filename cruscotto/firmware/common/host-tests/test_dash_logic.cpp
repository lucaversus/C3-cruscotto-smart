// Test sul PC della logica della dashboard (dash_logic.h).
#include <cstdio>
#include <cstdlib>

#include "dash_logic.h"

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
  // Sfumatura graduale: il rosso cresce e il verde cala in modo monotono oltre la soglia.
  int lastRed = -1, lastGreen = 256;
  for (int rpm = dash::kRpmGreenMax; rpm <= dash::kRpmRedFull; rpm += 50) {
    const uint32_t c = dash::rpmColor(rpm);
    check(red(c) >= lastRed && green(c) <= lastGreen, "giri: sfumatura monotona verde->rosso");
    lastRed = red(c);
    lastGreen = green(c);
  }
  check(dash::rpmColor(3750) != dash::kGreen && dash::rpmColor(3750) != dash::kRed, "giri: colore intermedio");
  check(dash::coolantColor(60) != dash::kWhite && dash::coolantColor(60) != dash::kAzure, "acqua: bianco->azzurro");
  check(dash::coolantColor(105) != dash::kAzure && dash::coolantColor(105) != dash::kRed, "acqua: azzurro->rosso");
  check(dash::coolantColor(dash::kCoolantAzureFrom) == dash::kAzure, "acqua: azzurro dalla zona normale");
  // Priorità degli avvisi.
  check(dash::alertFor(true, dash::kOilPressure | dash::kCharge, 90, true) == dash::Alert::kOilPressure,
        "olio prima della carica");
  check(dash::alertFor(true, dash::kCharge, 90, true) == dash::Alert::kCharge, "carica");
  check(dash::alertFor(true, 0, 90, true) == dash::Alert::kNone, "nessun avviso");
  check(dash::alertFor(true, dash::kTurnLeft, 90, true) == dash::Alert::kNone, "le luci non sono avvisi");
  // Velocità a sette segmenti: zeri iniziali spenti, trattino se dato assente.
  check(dash::speedSegments(0, 0) == dash::kSegments[0] && dash::speedSegments(0, 1) == 0, "velocità 0");
  check(dash::speedSegments(135, 2) == dash::kSegments[1] && dash::speedSegments(135, 1) == dash::kSegments[3],
        "velocità 135");
  check(dash::speedSegments(-1, 0) == dash::kSegmentDash && dash::speedSegments(-1, 2) == 0, "dato assente");
  // Prova lampade.
  check(dash::bulbCheck(0) && dash::bulbCheck(2999) && !dash::bulbCheck(3000), "prova lampade 3 s");
  if (failures) return EXIT_FAILURE;
  std::printf("test_dash_logic: tutti i controlli superati\n");
  return EXIT_SUCCESS;
}
