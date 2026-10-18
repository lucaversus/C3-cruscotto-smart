#pragma once
#include <stdint.h>
namespace logger {
constexpr int kSda = 21, kScl = 22;
constexpr int kSck = 18, kMiso = 19, kMosi = 23, kSdCs = 27;
constexpr uint8_t kRtcAddress = 0x68;
constexpr uint32_t kSampleMs = 1000, kStatusMs = 5000, kRetryMs = 10000;
constexpr uint32_t kSpiHz = 1000000; // Conservative bench starting point; not validated.
} // namespace logger
