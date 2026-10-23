// Versione del firmware S3: report seriale e schermo (accanto alla scritta DEMO).
#pragma once

namespace fw {
#define FW_VERSION_TEXT "0.7.0"  // anche come testo letterale, da concatenare
constexpr char kVersion[] = FW_VERSION_TEXT;  // + luminosità automatica e comandi seriali di debug
}  // namespace fw
