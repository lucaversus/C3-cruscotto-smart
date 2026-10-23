// Statistiche di sistema condivise tra il compito principale e l'interfaccia.
#pragma once
#include <atomic>
#include <stdint.h>

namespace sysstats {
inline std::atomic<uint8_t> cpu[2];  // carico % di CPU0 e CPU1 nell'ultimo secondo
}  // namespace sysstats
