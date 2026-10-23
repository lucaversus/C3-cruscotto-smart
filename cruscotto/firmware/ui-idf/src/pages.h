// Pagine 2 "Tecnica" e 3 "Diagnostica" (interfaccia-requisiti rev B). Da chiamare solo dal
// compito dell'interfaccia (LVGL). Ogni pagina ha la propria schermata.
#pragma once
#include <stdint.h>

#include "lvgl.h"

namespace pages {
lv_obj_t* buildTech();          // crea la schermata della pagina 2 (non la mostra)
lv_obj_t* buildDiag();          // crea la schermata della pagina 3 (non la mostra)
void updateTech(int64_t nowUs);
void updateDiag(int64_t nowUs);
}  // namespace pages
