// Pagina 1 "Dashboard" (D-041): da chiamare solo dal compito dell'interfaccia (LVGL).
#pragma once
#include <stdint.h>

namespace dashboard {
void build();
void update(int64_t nowUs);
}  // namespace dashboard
