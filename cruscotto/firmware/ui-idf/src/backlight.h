// Retroilluminazione del pannello in PWM su GPIO2 (LEDC): luminosità ridotta con gli
// anabbaglianti accesi e protezione termica dal sensore NTC del display (richiesta utente
// 23/10/2026). Soglie in dash_logic.h.
#pragma once
#include <stdint.h>

namespace backlight {
void start();                // PWM a duty 0: pannello spento finché il primo fotogramma non è pronto
void update(int64_t nowUs);  // obiettivo dai segnali, variazione graduale (~1 s per tutta la scala)
int percent();               // luminosità attuale, per il report seriale
// Debug a banco (comandi seriali): livello fisso (-1 = automatico) e frequenza PWM.
void setManual(int pct);
bool setFrequency(uint32_t hz);
uint32_t frequency();         // frequenza PWM attuale, per la riga di servizio
}  // namespace backlight
