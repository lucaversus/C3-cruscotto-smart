#pragma once
#include <stddef.h>
#include <stdint.h>
#include "calendar.h"

namespace logger {
constexpr uint8_t encodeBcd(unsigned value) { return (value / 10) * 16 + value % 10; }
constexpr bool parseUtc(const char *text, Calendar &out) {
  for (unsigned i = 0; i < 20; ++i) {
    if (!text[i]) return false;
    const char separator = i == 4 || i == 7 ? '-' : i == 10 ? 'T' : i == 13 || i == 16 ? ':' : i == 19 ? 'Z' : 0;
    if (separator ? text[i] != separator : text[i] < '0' || text[i] > '9') return false;
  }
  if (text[20]) return false;
  unsigned fields[6] = {};
  const unsigned offsets[] = {0, 5, 8, 11, 14, 17};
  for (unsigned field = 0; field < 6; ++field)
    for (unsigned i = 0; i < (field ? 2U : 4U); ++i) fields[field] = fields[field] * 10 + text[offsets[field] + i] - '0';
  if (fields[0] < 2000 || fields[0] > 2099) return false;
  const uint8_t raw[] = {encodeBcd(fields[5]), encodeBcd(fields[4]), encodeBcd(fields[3]), 1,
                        encodeBcd(fields[2]), encodeBcd(fields[1]), encodeBcd(fields[0] - 2000)};
  return decodeCalendar(raw, out);
}
constexpr uint8_t weekdaySunday1(const Calendar &c) {
  unsigned days = 6; // 2000-01-01 was Saturday, Sunday=1.
  for (unsigned year = 2000; year < c.year; ++year) days += 365 + (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0));
  const unsigned months[] = {31,28,31,30,31,30,31,31,30,31,30,31};
  for (unsigned month = 1; month < c.month; ++month) days += months[month - 1] + (month == 2 && c.year % 4 == 0 && (c.year % 100 != 0 || c.year % 400 == 0));
  return (days + c.day - 1) % 7 + 1;
}
// A latched STOP cannot restart acquisition on release, bounce or a second press.
struct StopButton {
  bool lastRaw = false, latched = false;
  uint32_t changedAt = 0;
  constexpr bool update(bool pressed, uint32_t now) {
    if (pressed != lastRaw) { lastRaw = pressed; changedAt = now; }
    if (pressed && elapsed(now, changedAt, 35)) latched = true;
    return latched;
  }
};

enum class SaveState { Waiting, Recording, Stopping, Saved, Error, NoSession };
struct SaveGate {
  SaveState state = SaveState::Waiting;
  constexpr void opened() { if (state == SaveState::Waiting) state = SaveState::Recording; }
  constexpr void stop() {
    if (state == SaveState::Waiting) state = SaveState::NoSession;
    else if (state == SaveState::Recording) state = SaveState::Stopping;
  }
  constexpr void fail() { state = SaveState::Error; }
  constexpr bool finish(bool sourcesStopped, bool empty, bool synced, bool closed, bool verified) {
    if (state != SaveState::Stopping || !sourcesStopped || !empty) return false;
    state = synced && closed && verified ? SaveState::Saved : SaveState::Error;
    return state == SaveState::Saved;
  }
};

struct KwpFrame {
  bool complete = false, valid = false;
  uint8_t target = 0, source = 0;
  size_t offset = 0, length = 0, total = 0;
};
constexpr uint8_t checksum(const uint8_t *data, size_t length) {
  uint8_t result = 0;
  for (size_t i = 0; i < length; ++i) result = static_cast<uint8_t>(result + data[i]);
  return result;
}
// ISO 14230 addressed headers. Unsupported unaddressed formats are retained as raw data.
constexpr KwpFrame parseKwp(const uint8_t *data, size_t count) {
  KwpFrame f{};
  if (count < 3 || !(data[0] & 0x80)) return f;
  f.target = data[1]; f.source = data[2]; f.offset = 3;
  f.length = data[0] & 0x3f;
  if (!f.length) {
    if (count < 4) return f;
    f.length = data[3]; f.offset = 4;
  }
  if (!f.length) return f;
  f.total = f.offset + f.length + 1;
  f.complete = count >= f.total;
  f.valid = f.complete && count == f.total && checksum(data, f.total - 1) == data[f.total - 1];
  return f;
}
constexpr bool pidSupported(const uint8_t *bitmap, uint8_t block, uint8_t pid) {
  if (pid <= block || static_cast<unsigned>(pid) > static_cast<unsigned>(block) + 32) return false;
  const uint8_t bit = pid - block - 1;
  return (bitmap[bit / 8] & (0x80 >> (bit % 8))) != 0;
}

// KWP polling plan: priority PIDs every round, then one other supported PID
// (rotating), so dynamic values are sampled often and slow ones still appear.
constexpr uint8_t kPriorityPids[] = {0x0c, 0x0d, 0x04, 0x0b, 0x10, 0x23};
constexpr bool isPriorityPid(unsigned pid) {
  for (uint8_t p : kPriorityPids) if (p == pid) return true;
  return false;
}
constexpr bool isLivePid(const bool *supported, unsigned pid) {
  return pid > 0 && pid < 256 && pid % 32 != 0 && supported[pid];
}
// Next non-priority live PID after cursor (wrapping), or 0 when none exists.
constexpr unsigned nextSlowPid(const bool *supported, unsigned cursor) {
  for (unsigned step = 1; step <= 255; ++step) {
    const unsigned pid = (cursor + step - 1) % 255 + 1;
    if (isLivePid(supported, pid) && !isPriorityPid(pid)) return pid;
  }
  return 0;
}

// CRC and enhanced-Manchester extraction adapted from Peter Pinter/haxplore's
// MIT-licensed esp32_rmt_van_rx, revision d64064f. See THIRD_PARTY.md.
constexpr uint16_t vanCrc(const uint8_t *data, size_t length) {
  uint16_t crc = 0x7fff;
  for (size_t i = 0; i < length; ++i) {
    uint8_t byte = data[i];
    for (unsigned j = 0; j < 8; ++j) {
      const bool bit = ((crc & 0x4000) != 0) != ((byte & 0x80) != 0);
      byte = static_cast<uint8_t>(byte << 1);
      crc = static_cast<uint16_t>(((crc << 1) & 0x7fff) ^ (bit ? 0x0f9d : 0));
    }
  }
  return static_cast<uint16_t>((crc ^ 0x7fff) << 1);
}
constexpr bool vanCrcOk(const uint8_t *frame, size_t n) {
  return n >= 5 && vanCrc(frame + 1, n - 3) ==
         static_cast<uint16_t>((frame[n - 2] << 8) | frame[n - 1]);
}
struct VanDecoder {
  uint8_t data[64] = {};
  size_t length = 0;
  unsigned bit = 0;
  uint8_t byte = 0;
  bool overflow = false, timingError = false;
  constexpr void pulse(bool level, uint32_t duration, unsigned quantum, bool invert) {
    if (!duration || overflow) return;
    if (quantum != 8 && quantum != 16) { timingError = true; return; }
    unsigned slices = (duration + quantum / 2) / quantum;
    if (!slices || slices > 20) { timingError = true; return; }
    const unsigned rounded = slices * quantum;
    const unsigned error = duration > rounded ? duration - rounded : rounded - duration;
    if (error > quantum / 3) timingError = true;
    level = level != invert;
    for (unsigned i = 0; i < slices; ++i) {
      if ((bit + 1) % 5 != 0) byte = static_cast<uint8_t>((byte << 1) | (level ? 1 : 0));
      if (++bit == 10) {
        if (length == sizeof(data)) { overflow = true; return; }
        data[length++] = byte; byte = 0; bit = 0;
      }
    }
  }
};
} // namespace logger
