// Scatola nera degli eventi ed etichette dell'utente (D-037).
// Memoria circolare in PSRAM con tutti i campioni ricevuti; su evento salva in flash
// (LittleFS, partizione "storage") la finestra da 50 s prima a 10 s dopo l'evento.
#pragma once
#include <stdint.h>

#include "fe_link.h"

namespace blackbox {

enum class Reason : uint8_t { kUserLabel = 1, kDtc = 2, kWarning = 3, kManual = 4 };

struct Stats {
  uint32_t capacity = 0;     // campioni memorizzabili
  uint32_t filled = 0;       // campioni presenti
  uint32_t eventsSaved = 0;  // file evento scritti dall'avvio
  uint32_t eventsFailed = 0;
  uint32_t eventsDeleted = 0;  // eventi più vecchi cancellati per fare spazio
  uint32_t fsTotalKb = 0, fsUsedKb = 0;
  bool fsMounted = false;
  bool pending = false;      // evento in attesa della finestra successiva
};

bool start();  // alloca la memoria circolare, monta LittleFS, avvia il compito di salvataggio
void record(uint16_t id, felink::Quality q, float value, int64_t nowUs);  // dal compito di ricezione
bool trigger(Reason reason, int64_t nowUs);  // false se un evento è già in corso
Stats stats();

}  // namespace blackbox
