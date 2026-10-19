#pragma once
#include <atomic>
#include <Arduino.h>
#include "config.h"

enum class Source : uint8_t { Van, KwpTx, KwpRx, ObdPid, System };
struct Record {
  int64_t monoUs = 0;
  Source source = Source::System;
  uint32_t frame = 0, id = 0;
  uint16_t offset = 0;
  uint8_t length = 0;
  uint8_t raw[64] = {};
  float value = 0;
  const char *event = "info";
  const char *unit = "";
};
struct CaptureStatus {
  std::atomic<bool> stop{false}, vanDone{true}, kwpDone{true};
  std::atomic<bool> vanReady{false}, kwpConnected{false};
  std::atomic<uint32_t> dropped{0}, vanFrames{0}, vanBad{0}, kwpFrames{0}, kwpErrors{0};
};
extern CaptureStatus capture;
bool submitRecord(const Record &record);
void systemRecord(const char *event, uint32_t id = 0);
bool startAcquisition();
