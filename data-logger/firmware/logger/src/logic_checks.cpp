// Behavioural regression checks evaluated by the compiler against production code.
#include "logger_logic.h"
namespace {
constexpr bool stopBounceAndLatch() {
  logger::StopButton b;
  if (b.update(true, 100) || b.update(false, 110) || b.update(true, 120) || b.update(true, 154)) return false;
  return b.update(true, 155) && b.update(false, 156) && b.update(false, 9999);
}
constexpr bool stopAtBoot() {
  logger::StopButton b;
  return !b.update(true, 0) && !b.update(true, 34) && b.update(true, 35);
}
constexpr bool stopWrap() {
  logger::StopButton b;
  return !b.update(true, 0xfffffff0) && !b.update(true, 0x12) && b.update(true, 0x13);
}
constexpr bool saveFailuresNeverSucceed() {
  for (unsigned mask = 0; mask < 32; ++mask) {
    logger::SaveGate s; s.opened(); s.stop();
    const bool saved = s.finish(mask & 1, mask & 2, mask & 4, mask & 8, mask & 16);
    if (saved != (mask == 31)) return false;
  }
  return true;
}
constexpr bool noRestartAfterStop() {
  logger::SaveGate s; s.opened(); s.stop(); s.finish(true, true, true, true, true);
  s.opened(); s.stop(); return s.state == logger::SaveState::Saved;
}
constexpr bool emptyStop() {
  logger::SaveGate s; s.stop(); s.opened(); return s.state == logger::SaveState::NoSession;
}
constexpr bool errorIsSticky() {
  logger::SaveGate s; s.opened(); s.fail(); s.stop(); s.opened();
  return !s.finish(true, true, true, true, true) && s.state == logger::SaveState::Error;
}
constexpr uint8_t initReply[] = {0x83, 0xf1, 0x10, 0xc1, 0xe9, 0x8f, 0xbd};
constexpr uint8_t badReply[] = {0x83, 0xf1, 0x10, 0xc1, 0xe9, 0x8f, 0xbe};
constexpr uint8_t extended[] = {0x80, 0xf1, 0x10, 0x02, 0x41, 0x05, 0xc9};
constexpr uint8_t zeroLength[] = {0x80, 0xf1, 0x10, 0};
constexpr uint8_t noAddresses[] = {0x03, 0x41, 0x05, 0x40, 0x89};
constexpr uint8_t bitmap[] = {0x80, 0, 0, 1};
constexpr bool dateCommand(const char *text) { logger::Calendar c{}; return logger::parseUtc(text, c); }
constexpr bool correctWeekday() {
  logger::Calendar c{}; return logger::parseUtc("2026-10-19T21:00:00Z", c) && logger::weekdaySunday1(c) == 2;
}
constexpr bool vanByte() {
  logger::VanDecoder d;
  const bool pulses[] = {1,0,1,0,1,0,1,0,1,0}; // 0xA5 plus the two Manchester bits.
  for (bool bit : pulses) d.pulse(bit, 8, 8, false);
  return d.length == 1 && d.data[0] == 0xa5 && !d.overflow && !d.timingError;
}
constexpr bool vanInverse() {
  logger::VanDecoder d; d.pulse(false, 32, 8, true); d.pulse(true, 8, 8, true);
  d.pulse(false, 32, 8, true); d.pulse(true, 8, 8, true);
  return d.length == 1 && d.data[0] == 0xff;
}
constexpr bool vanBounded() {
  logger::VanDecoder d;
  for (unsigned i = 0; i < 65; ++i) d.pulse(false, 80, 8, false);
  return d.length == 64 && d.overflow;
}
constexpr bool badPulse() { logger::VanDecoder d; d.pulse(true, 65535, 8, false); return d.timingError && d.length == 0; }
constexpr bool slowRotationSkipsPriority() {
  bool s[256] = {}; s[0x05] = s[0x0c] = s[0x20] = s[0x2f] = true;
  return logger::nextSlowPid(s, 0) == 0x05 && logger::nextSlowPid(s, 0x05) == 0x2f &&
         logger::nextSlowPid(s, 0x2f) == 0x05 && logger::nextSlowPid(s, 255) == 0x05;
}
constexpr bool noSlowPid() {
  bool s[256] = {}; s[0x0c] = s[0x0d] = s[0x40] = true;
  return logger::nextSlowPid(s, 0) == 0 && logger::isLivePid(s, 0x0c) && !logger::isLivePid(s, 0x40);
}
static_assert(slowRotationSkipsPriority(), "Slow PID rotation wrong");
static_assert(noSlowPid(), "Bitmap or priority PID treated as slow PID");
static_assert(stopBounceAndLatch(), "STOP debounce/release restarted acquisition");
static_assert(stopAtBoot(), "Held STOP at boot must latch");
static_assert(stopWrap(), "STOP millis wraparound failed");
static_assert(saveFailuresNeverSucceed(), "False SALVATO under a failing save gate");
static_assert(noRestartAfterStop(), "STOP must stay stopped until reboot");
static_assert(emptyStop(), "No file cannot be reported saved");
static_assert(errorIsSticky(), "Write error cannot become success");
static_assert(logger::parseKwp(initReply, sizeof(initReply)).valid, "Valid KWP checksum rejected");
static_assert(logger::parseKwp(initReply, sizeof(initReply)).source == 0x10, "ECU source not decoded");
static_assert(!logger::parseKwp(badReply, sizeof(badReply)).valid, "Bad KWP checksum accepted");
static_assert(!logger::parseKwp(initReply, sizeof(initReply) - 1).complete, "Truncated KWP accepted");
static_assert(logger::parseKwp(extended, sizeof(extended)).valid, "Extended-length header rejected");
static_assert(!logger::parseKwp(zeroLength, sizeof(zeroLength)).valid, "Empty KWP payload accepted");
static_assert(!logger::parseKwp(noAddresses, sizeof(noAddresses)).valid, "Unsupported header silently decoded");
static_assert(logger::pidSupported(bitmap, 0, 1), "First PID bit mapping wrong");
static_assert(logger::pidSupported(bitmap, 0, 32), "PID continuation bit wrong");
static_assert(!logger::pidSupported(bitmap, 0, 2), "Unsupported PID accepted");
static_assert(!logger::pidSupported(bitmap, 0, 0), "PID block boundary underflow");
static_assert(!logger::pidSupported(bitmap, 0, 33), "PID outside block accepted");
static_assert(dateCommand("2024-02-29T00:00:00Z"), "Leap UTC rejected");
static_assert(!dateCommand("2025-02-29T00:00:00Z"), "Non-leap UTC accepted");
static_assert(!dateCommand("2026-10-19T24:00:00Z"), "Invalid UTC hour accepted");
static_assert(!dateCommand("2026-10-19T00:00:00+02:00"), "Implicit timezone accepted");
static_assert(!dateCommand("2026-10-19T00:00:00Zextra"), "Trailing time garbage accepted");
static_assert(!dateCommand("2026"), "Short time command accepted");
static_assert(correctWeekday(), "RTC weekday wrong");
static_assert(vanByte(), "Enhanced Manchester extraction wrong");
static_assert(vanInverse(), "VAN input inversion wrong");
static_assert(vanBounded(), "Long VAN packet overflows memory");
static_assert(badPulse(), "RMT duration narrowed or unbounded");
static_assert(!logger::vanCrcOk(initReply, 4), "Short VAN frame accepted");
} // namespace
