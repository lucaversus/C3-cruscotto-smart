#pragma once
#include <stdint.h>

namespace logger {
struct Calendar {
  uint16_t year;
  uint8_t month, day, hour, minute, second;
};
constexpr bool decodeBcd(uint8_t raw, uint8_t &out) {
  if ((raw & 15) > 9 || (raw >> 4) > 9) return false;
  out = (raw >> 4) * 10 + (raw & 15);
  return true;
}
// Registers 00h..06h. Reject reserved bits and malformed calendar values.
// Calendar validity alone does not establish correct wall time or timezone.
constexpr bool decodeCalendar(const uint8_t *r, Calendar &out) {
  if ((r[0] & 0x80) || (r[1] & 0x80) || (r[2] & 0x80) ||
      (r[3] & 0xf8) || (r[4] & 0xc0) || (r[5] & 0x60)) return false;
  Calendar c{};
  uint8_t hour = 0, year = 0;
  if (!decodeBcd(r[0], c.second) || c.second > 59 ||
      !decodeBcd(r[1], c.minute) || c.minute > 59 ||
      !decodeBcd(r[4], c.day) || !decodeBcd(r[5] & 0x1f, c.month) ||
      !decodeBcd(r[6], year) || r[3] < 1 || r[3] > 7) return false;
  if (r[2] & 0x40) {
    if (!decodeBcd(r[2] & 0x1f, hour) || hour < 1 || hour > 12) return false;
    c.hour = (hour % 12) + ((r[2] & 0x20) ? 12 : 0);
  } else {
    if (!decodeBcd(r[2], c.hour) || c.hour > 23) return false;
  }
  c.year = 2000 + year + ((r[5] & 0x80) ? 100 : 0);
  if (c.month < 1 || c.month > 12) return false;
  const uint8_t days[] = {31,28,31,30,31,30,31,31,30,31,30,31};
  const bool leap = c.year % 4 == 0 && (c.year % 100 != 0 || c.year % 400 == 0);
  const uint8_t limit = days[c.month - 1] + ((c.month == 2 && leap) ? 1 : 0);
  if (c.day < 1 || c.day > limit) return false;
  out = c;
  return true;
}
constexpr bool elapsed(uint32_t now, uint32_t then, uint32_t interval) {
  return static_cast<uint32_t>(now - then) >= interval;
}
} // namespace logger
