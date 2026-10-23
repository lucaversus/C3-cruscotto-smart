// Aggiornamento del firmware dalla MicroSD, senza smontare il logger dall'auto
// (richiesta dell'utente 23/10/2026). Ritorno alla versione precedente automatico se la
// nuova si blocca o si riavvia prima della conferma, oppure manuale tenendo premuto STOP
// all'accensione.
#pragma once
#include <stdint.h>

namespace sdupdate {
void rollbackIfRequested();              // STOP tenuto kRollbackHoldMs all'accensione
void installFromCard();                  // cerca kUpdateBin, verifica l'impronta, installa e riavvia
void confirmWhenStable(uint32_t nowMs);  // conferma la versione in prova dopo kConfirmMs
}  // namespace sdupdate
