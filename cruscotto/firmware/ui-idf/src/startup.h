// Sequenza d'avvio in stile "Matrix" con controllo di sistema e via libera GO.
// Da chiamare solo dal compito dell'interfaccia (LVGL).
#pragma once
#include <stdint.h>

#include "lvgl.h"

namespace startup {
void build();                                  // crea la propria schermata e la rende attiva
bool update(int64_t nowUs, lv_obj_t* next);    // false quando ha mostrato la schermata next
}  // namespace startup
