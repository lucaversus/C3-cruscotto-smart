// Logica pura della sequenza d'avvio (interfaccia-requisiti rev B, "Sequenza di avvio"):
// esito di ogni controllo e via libera GO. Nessuna dipendenza da LVGL: provata sul PC.
#pragma once
#include <stdint.h>

namespace boot {

enum class State : uint8_t { kPending, kOk, kFail, kAbsent };  // kAbsent: modulo non ancora installato
enum class Phase : uint8_t { kChecking, kGo, kFailed };

constexpr uint32_t kStepMs = 350;       // un controllo nuovo sullo schermo ogni kStepMs
constexpr uint32_t kMinMs = 4000;       // durata minima dell'apertura
constexpr uint32_t kWaitMs = 5000;      // attesa massima di un dato prima dell'errore
constexpr uint32_t kGlowMaxMs = 30000;  // preriscaldo più lungo di così: errore
constexpr uint32_t kGoShowMs = 1500;    // GO visibile prima della dashboard
constexpr uint32_t kFailShowMs = 6000;  // elenco degli errori visibile prima della dashboard

// Controllo di un dato del front-end: valido e nell'intervallo atteso.
constexpr State dataCheck(bool fresh, bool inRange, uint32_t elapsedMs) {
  return fresh ? (inRange ? State::kOk : State::kFail) : elapsedMs < kWaitMs ? State::kPending : State::kFail;
}

// Candelette: il GO attende lo spegnimento della spia (dato dell'auto).
constexpr State glowCheck(bool fresh, bool lampOn, uint32_t elapsedMs) {
  return !fresh ? (elapsedMs < kWaitMs ? State::kPending : State::kFail)
         : lampOn ? (elapsedMs < kGlowMaxMs ? State::kPending : State::kFail)
                  : State::kOk;
}

// GO solo quando sono finiti tutti i controlli, nessuno è fallito (le candelette sono uno
// dei controlli) ed è passata la durata minima dell'apertura.
constexpr Phase phase(int pending, int failed, uint32_t elapsedMs) {
  return pending > 0 || elapsedMs < kMinMs ? Phase::kChecking : failed > 0 ? Phase::kFailed : Phase::kGo;
}

static_assert(dataCheck(false, false, 0) == State::kPending && dataCheck(false, false, kWaitMs) == State::kFail, "attesa dato");
static_assert(glowCheck(true, true, 1000) == State::kPending && glowCheck(true, false, 1000) == State::kOk, "candelette");
static_assert(phase(1, 0, 10000) == Phase::kChecking && phase(0, 0, 1000) == Phase::kChecking, "attesa");
static_assert(phase(0, 0, kMinMs) == Phase::kGo && phase(0, 1, kMinMs) == Phase::kFailed, "esito");

}  // namespace boot
