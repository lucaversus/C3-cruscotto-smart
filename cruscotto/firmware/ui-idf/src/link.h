// Collegamento UART con il front-end (protocollo fe_link v1, D-029).
#pragma once
#include <stdint.h>

struct LinkStats {
  uint32_t frames = 0;        // trame valide ricevute
  uint32_t errors = 0;        // trame scartate (CRC/COBS)
  uint32_t lostSeq = 0;       // trame mancanti secondo la sequenza
  int64_t lastFrameUs = 0;    // tempo locale dell'ultima trama valida
  bool simulated = false;     // sorgente simulata in loopback interno
};

// Avvia UART1 (IO12 TX, IO11 RX) e il compito di ricezione sul core 0.
// Con simulate=true la UART è in loopback interno e un compito genera dati simulati.
void linkStart(bool simulate);
LinkStats linkStats();
bool linkAlive(int64_t nowUs);  // trama valida negli ultimi 3 s
