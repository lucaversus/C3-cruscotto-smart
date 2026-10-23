// Pagina 1 "Dashboard" (D-041): da chiamare solo dal compito dell'interfaccia (LVGL).
#pragma once
#include <stdint.h>

namespace dashboard {
void build();
void update(int64_t nowUs);  // da chiamare anche quando la pagina non è visibile
bool alertActive();           // riquadro di avviso aperto (per tornare alla dashboard)
}  // namespace dashboard
