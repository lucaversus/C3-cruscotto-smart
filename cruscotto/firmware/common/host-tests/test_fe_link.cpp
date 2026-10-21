// Test host del protocollo front-end <-> S3 (fe_link.h). Eseguiti da `python tools/dev.py check`.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>

#include "fe_link.h"

namespace {
int failures = 0;

void check(bool ok, const char* what) {
  if (!ok) {
    std::printf("FAIL: %s\n", what);
    ++failures;
  }
}

bool sameBytes(const uint8_t* a, size_t n, const uint8_t* b, size_t m) { return n == m && std::memcmp(a, b, n) == 0; }

void testCrc() {
  const char* text = "123456789";
  check(felink::crc16(reinterpret_cast<const uint8_t*>(text), 9) == 0x29B1, "CRC-16/CCITT-FALSE check value");
}

void testCobsVectors() {
  uint8_t out[16];
  const uint8_t a[] = {0x00};
  const uint8_t ea[] = {0x01, 0x01};
  check(sameBytes(out, felink::cobsEncode(a, 1, out), ea, 2), "COBS 00");
  const uint8_t b[] = {0x11, 0x22, 0x00, 0x33};
  const uint8_t eb[] = {0x03, 0x11, 0x22, 0x02, 0x33};
  check(sameBytes(out, felink::cobsEncode(b, 4, out), eb, 5), "COBS 11 22 00 33");
  uint8_t dec[16];
  check(sameBytes(dec, felink::cobsDecode(eb, 5, dec), b, 4), "COBS decode");
  const uint8_t bad[] = {0x05, 0x11};
  check(felink::cobsDecode(bad, 2, dec) == 0, "COBS truncated rejected");
}

void testCobsLongRun() {
  uint8_t in[600], enc[700], dec[700];
  for (size_t i = 0; i < sizeof in; ++i) in[i] = static_cast<uint8_t>(i % 7 == 3 ? 0 : (i % 251) + 1);
  for (size_t len : {size_t(253), size_t(254), size_t(255), size_t(600)}) {
    uint8_t run[600];
    std::memset(run, 0x5A, len);
    const size_t e = felink::cobsEncode(run, len, enc);
    bool noZero = true;
    for (size_t i = 0; i < e; ++i) noZero = noZero && enc[i] != 0;
    check(noZero, "COBS long run has no zero");
    check(sameBytes(dec, felink::cobsDecode(enc, e, dec), run, len), "COBS long run round trip");
  }
  const size_t e = felink::cobsEncode(in, sizeof in, enc);
  check(sameBytes(dec, felink::cobsDecode(enc, e, dec), in, sizeof in), "COBS mixed round trip");
}

void testFrameRoundTrip() {
  felink::Frame f;
  f.type = felink::Type::kSignals;
  f.seq = 42;
  f.timeUs = 0x01020304;
  check(felink::addSignal(f, felink::sig::kRpm, felink::Quality::kSimulated, 2350.0f), "add rpm");
  check(felink::addSignal(f, felink::sig::obdPid(0x0B), felink::Quality::kValid, 101.5f), "add MAP");
  check(felink::addSignal(f, felink::sig::kBatteryV, felink::Quality::kUnverified, 0.0f), "add zero value");
  uint8_t wire[felink::kMaxEncoded];
  const size_t n = felink::encode(f, wire);
  check(n > 0 && wire[n - 1] == 0, "frame ends with delimiter");
  for (size_t i = 0; i + 1 < n; ++i) check(wire[i] != 0, "no zero inside frame");

  felink::Decoder d;
  felink::Frame got;
  bool ready = false;
  for (size_t i = 0; i < n; ++i) ready = d.push(wire[i], got);
  check(ready, "frame decoded");
  check(got.type == felink::Type::kSignals && got.seq == 42 && got.timeUs == 0x01020304, "header fields");
  felink::Signal s{};
  check(felink::getSignal(got, 0, s) && s.id == felink::sig::kRpm && s.quality == felink::Quality::kSimulated &&
            s.value == 2350.0f, "signal 0");
  check(felink::getSignal(got, 1, s) && s.id == 0x010B && s.value == 101.5f, "signal 1");
  check(felink::getSignal(got, 2, s) && s.value == 0.0f, "signal 2");
  check(!felink::getSignal(got, 3, s), "no signal 3");
}

void testCorruptionAndResync() {
  felink::Frame f;
  f.type = felink::Type::kEvent;
  f.seq = 7;
  f.body[0] = 0x34;
  f.body[1] = 0x12;
  f.bodyLen = 2;
  uint8_t wire[felink::kMaxEncoded];
  const size_t n = felink::encode(f, wire);

  felink::Decoder d;
  felink::Frame got;
  // Rumore iniziale senza delimitatore, poi una trama corrotta, poi una buona.
  const uint8_t noise[] = {0x13, 0x77, 0x00};
  for (uint8_t b : noise) check(!d.push(b, got), "noise rejected");
  uint8_t bad[felink::kMaxEncoded];
  std::memcpy(bad, wire, n);
  bad[2] ^= 0x40;
  bool ready = false;
  for (size_t i = 0; i < n; ++i) ready = d.push(bad[i], got);
  check(!ready, "corrupted frame rejected");
  for (size_t i = 0; i < n; ++i) ready = d.push(wire[i], got);
  check(ready && got.type == felink::Type::kEvent && got.bodyLen == 2 && got.body[0] == 0x34, "resync on next frame");
  check(d.errors() == 2, "error counter");
}

void testBodyLimit() {
  felink::Frame f;
  f.type = felink::Type::kSignals;
  int added = 0;
  while (felink::addSignal(f, 1, felink::Quality::kValid, 1.0f)) ++added;
  check(added == static_cast<int>((felink::kMaxBody - 1) / 7), "signals per frame");
  uint8_t wire[felink::kMaxEncoded];
  check(felink::encode(f, wire) <= felink::kMaxEncoded, "max frame fits buffer");
  f.bodyLen = felink::kMaxBody + 1;
  check(felink::encode(f, wire) == 0, "oversized body rejected");
}
}  // namespace

int main() {
  testCrc();
  testCobsVectors();
  testCobsLongRun();
  testFrameRoundTrip();
  testCorruptionAndResync();
  testBodyLimit();
  if (failures) return EXIT_FAILURE;
  std::printf("fe_link: tutti i test superati\n");
  return EXIT_SUCCESS;
}
