#pragma once
#include <stdint.h>
#include <stddef.h>
namespace logger {
constexpr int kSda = 21, kScl = 22;
constexpr int kSck = 18, kMiso = 19, kMosi = 23, kSdCs = 27;
constexpr uint8_t kRtcAddress = 0x68;
constexpr uint32_t kSampleMs = 1000, kStatusMs = 5000, kRetryMs = 10000;
constexpr uint32_t kSpiHz = 1000000; // Conservative bench starting point; not validated.
constexpr int kStopPin = 32; // Normally-open STOP to GND, internal pull-up.
constexpr int kKwpRx = 16, kKwpTx = 17, kVanRx = 34;
constexpr int kUnusedCanCs = 26; // Keep the previous MCP2515 test CS inactive.
constexpr uint32_t kStopDebounceMs = 35, kFlushMs = 1000;
constexpr uint32_t kSegmentBytes = 64UL * 1024UL * 1024UL;
constexpr uint8_t kOledAddress = 0x3c;
constexpr size_t kQueueDepth = 256;
constexpr char kVersion[] = "0.3.0";
} // namespace logger

#ifndef LOGGER_ENABLE_KWP
#define LOGGER_ENABLE_KWP 0
#endif
#ifndef LOGGER_ENABLE_VAN
#define LOGGER_ENABLE_VAN 0
#endif
#ifndef LOGGER_VAN_BODY
#define LOGGER_VAN_BODY 0
#endif
#ifndef LOGGER_VAN_INVERT
#define LOGGER_VAN_INVERT 0
#endif
