// Etichette dell'utente (D-037): pressione lunga su un comando al volante (VAN 9C4,
// segnale sig::kStalkButtons) oppure, a banco, sul pulsante BOOT della scheda S3.
#pragma once
#include <stdint.h>

namespace labels {
constexpr int64_t kLongPressUs = 2000000;  // pressione lunga: almeno 2 s

void start();                                        // compito che legge il pulsante BOOT (GPIO0)
void onStalkButtons(float bits, int64_t nowUs);     // dal compito di ricezione
int64_t lastLabelUs();                               // 0 = nessuna etichetta dall'avvio
uint32_t count();
}  // namespace labels
