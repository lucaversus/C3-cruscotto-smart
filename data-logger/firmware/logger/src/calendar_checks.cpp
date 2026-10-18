// Executed by the compiler against the actual decoder, no mock implementation.
#include "calendar.h"
namespace {
constexpr bool dateAccepted(uint8_t day, uint8_t month, uint8_t year) {
  const uint8_t raw[] = {0x59, 0x58, 0x23, 1, day, month, year};
  logger::Calendar out{};
  return logger::decodeCalendar(raw, out);
}
constexpr bool hourIs(uint8_t rawHour, uint8_t expected) {
  const uint8_t raw[] = {0, 0, rawHour, 1, 0x18, 0x10, 0x26};
  logger::Calendar out{};
  return logger::decodeCalendar(raw, out) && out.hour == expected;
}
constexpr bool rejectAndPreserve() {
  const uint8_t raw[] = {0x6a, 0, 0, 1, 1, 1, 0x26};
  logger::Calendar out{2026, 1, 1, 1, 1, 1};
  return !logger::decodeCalendar(raw, out) && out.year == 2026 && out.second == 1;
}
constexpr bool centuryDecoded() {
  const uint8_t raw[] = {0, 0, 0, 1, 1, 0x81, 0};
  logger::Calendar out{};
  return logger::decodeCalendar(raw, out) && out.year == 2100;
}
constexpr bool reservedBitRejected() {
  const uint8_t raw[] = {0, 0, 0, 1, 1, 0x21, 0x26};
  logger::Calendar out{};
  return !logger::decodeCalendar(raw, out);
}
static_assert(dateAccepted(0x18, 0x10, 0x26), "Normal calendar rejected");
static_assert(dateAccepted(0x29, 0x02, 0x24), "Leap day 2024 rejected");
static_assert(!dateAccepted(0x29, 0x02, 0x25), "Non-leap day accepted");
static_assert(!dateAccepted(0x29, 0x82, 0x00), "Year 2100 is not leap");
static_assert(!dateAccepted(0x31, 0x04, 0x26), "April 31 accepted");
static_assert(!dateAccepted(0x00, 0x01, 0x26), "Zero day accepted");
static_assert(!dateAccepted(0x01, 0x00, 0x26), "Zero month accepted");
static_assert(hourIs(0x52, 0), "12 AM must decode to 00");
static_assert(hourIs(0x72, 12), "12 PM must decode to 12");
static_assert(hourIs(0x61, 13), "1 PM must decode to 13");
static_assert(hourIs(0x23, 23), "24-hour mode failed");
static_assert(!hourIs(0x24, 24), "Hour 24 accepted");
static_assert(!hourIs(0x40, 0), "12-hour zero accepted");
static_assert(rejectAndPreserve(), "Invalid BCD accepted or output modified");
static_assert(centuryDecoded(), "Century bit ignored");
static_assert(reservedBitRejected(), "Reserved month bit accepted");
static_assert(logger::elapsed(0x10, 0xfffffff0, 32), "Wraparound interval failed");
static_assert(!logger::elapsed(0x0f, 0xfffffff0, 32), "Early wraparound interval");
} // namespace
