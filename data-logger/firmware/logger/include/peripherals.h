#pragma once
#include <Arduino.h>
#include "calendar.h"
struct RtcSnapshot {
  char calendar[32] = {};
  const char *state = "unavailable";
  int64_t readMonoUs = 0;
};
extern RtcSnapshot rtc;
void beginPeripherals();
void pollRtc();
bool setRtcUtc(const char *iso);
bool selectOled(const char *model);
void drawStatus(const char *title, const char *storage, uint64_t rows, uint32_t dropped);
