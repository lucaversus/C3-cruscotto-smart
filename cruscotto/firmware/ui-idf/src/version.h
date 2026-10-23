// Versione del firmware S3: report seriale e schermo (accanto alla scritta DEMO).
#pragma once

namespace fw {
// Regola: ogni firmware modificato che si carica ha un numero nuovo (utente 23/10/2026).
// Funzioni nuove: secondo numero (0.8.0 → 0.9.0); sole correzioni: terzo (0.8.0 → 0.8.1).
// 0.7.0 luminosità automatica e comandi seriali; 0.8.0 rotazione della scatola nera, pagine
// Tecnica e Diagnostica, pulsante BOOT per il cambio pagina; 0.9.0 collegamento reale con il
// front-end su UART, simulatore interno solo se il front-end non risponde.
#define FW_VERSION_TEXT "0.9.0"  // anche come testo letterale, da concatenare
constexpr char kVersion[] = FW_VERSION_TEXT;
}  // namespace fw
