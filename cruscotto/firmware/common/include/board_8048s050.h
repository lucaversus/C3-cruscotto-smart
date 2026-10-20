#pragma once
// Pinout ESP32-8048S050: RGB, PCLK 16 MHz e retroilluminazione verificati (DSP-M001).
// Fonte comunitaria: rzeldent/platformio-espressif32-sunton, esp32-8048S050C.json.
#include <stdint.h>

namespace board {
constexpr int kBacklight = 2;
constexpr int kHsync = 39;
constexpr int kVsync = 41;
constexpr int kDe = 40;
constexpr int kPclk = 42;
// Ordine esp_lcd D0..D15 per RGB565: B0..B4, G0..G5, R0..R4. La fonte chiama
// R0..R4 i GPIO 8/3/46/9/1 ma li elenca come DATA0..4: le barre colore lo verificano.
constexpr int kData[16] = {8, 3, 46, 9, 1,        // B0..B4
                           5, 6, 7, 15, 16, 4,    // G0..G5
                           45, 48, 47, 21, 14};   // R0..R4
constexpr uint16_t kWidth = 800;
constexpr uint16_t kHeight = 480;
constexpr uint32_t kPclkHz = 16000000;
constexpr int kHsyncPulse = 4, kHsyncBack = 8, kHsyncFront = 8;
constexpr int kVsyncPulse = 4, kVsyncBack = 8, kVsyncFront = 8;
// Touch GT911 sulla variante C; atteso assente sulla variante senza touch (D-027).
constexpr int kI2cSda = 19;
constexpr int kI2cScl = 20;
}  // namespace board
