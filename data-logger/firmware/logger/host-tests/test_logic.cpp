// Test eseguibili sul PC della logica condivisa con il firmware (D-023).
// Stessi header di produzione, nessun Arduino/ESP-IDF: verificano algoritmi,
// non temporizzazioni UART/RMT, SD o hardware. Compilati da `python tools/dev.py check`.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include "logger_logic.h"

namespace {
int failures = 0, checks = 0;
#define CHECK(cond) do { ++checks; if (!(cond)) { ++failures; \
  std::printf("FAIL %s:%d %s\n", __FILE__, __LINE__, #cond); } } while (0)

// --- VAN: encoder di riferimento (enhanced Manchester, 10 time slot per byte) ---
struct Pulse { bool level; uint32_t us; };
std::vector<Pulse> encodeVan(const std::vector<uint8_t> &bytes, unsigned quantum) {
  std::vector<bool> slots;
  for (uint8_t b : bytes) {
    for (int nibble = 1; nibble >= 0; --nibble) {
      bool last = false;
      for (int i = 3; i >= 0; --i) { last = (b >> (nibble * 4 + i)) & 1; slots.push_back(last); }
      slots.push_back(!last); // bit Manchester: complemento dell'ultimo bit del nibble
    }
  }
  std::vector<Pulse> out;
  for (bool s : slots) {
    if (!out.empty() && out.back().level == s) out.back().us += quantum;
    else out.push_back({s, quantum});
  }
  return out;
}
std::vector<uint8_t> vanFrame(const std::vector<uint8_t> &body) {
  std::vector<uint8_t> f{0x0e}; // primo byte: SOF, escluso dal CRC come nel firmware
  f.insert(f.end(), body.begin(), body.end());
  const uint16_t crc = logger::vanCrc(f.data() + 1, f.size() - 1);
  f.push_back(crc >> 8); f.push_back(crc & 0xff);
  return f;
}
logger::VanDecoder decode(const std::vector<Pulse> &pulses, unsigned quantum, bool invert, int jitter = 0) {
  logger::VanDecoder d;
  for (const Pulse &p : pulses) d.pulse(p.level != invert, p.us + jitter, quantum, invert);
  return d;
}

void testVanRoundTrip() {
  std::srand(1234);
  for (unsigned quantum : {8u, 16u}) {
    for (int n = 0; n < 500; ++n) {
      std::vector<uint8_t> body(2 + std::rand() % 28);
      for (auto &b : body) b = std::rand() & 0xff;
      const auto frame = vanFrame(body);
      for (bool invert : {false, true}) {
        const auto d = decode(encodeVan(frame, quantum), quantum, invert);
        CHECK(!d.timingError && !d.overflow);
        CHECK(d.length == frame.size() && !std::memcmp(d.data, frame.data(), frame.size()));
        CHECK(logger::vanCrcOk(d.data, d.length));
      }
    }
  }
}
// CRC-15 VAN di riferimento, scritto in modo indipendente dal firmware:
// polinomio x^15+x^11+x^10+x^9+x^8+x^7+x^4+x^3+x^2+1, valore iniziale e XOR
// finale 0x7FFF, risultato trasmesso sui 15 bit alti di due byte (LSB a zero).
uint16_t referenceVanCrc(const uint8_t *data, size_t length) {
  const int exponents[] = {11, 10, 9, 8, 7, 4, 3, 2, 0};
  uint32_t poly = 0;
  for (int e : exponents) poly |= 1u << e;
  uint32_t reg = 0x7fff;
  for (size_t i = 0; i < length; ++i)
    for (int bit = 7; bit >= 0; --bit) {
      const bool in = (data[i] >> bit) & 1, top = (reg >> 14) & 1;
      reg = (reg << 1) & 0x7fff;
      if (in != top) reg ^= poly;
    }
  return static_cast<uint16_t>(((reg ^ 0x7fff) & 0x7fff) << 1);
}
void testVanCrcMatchesReference() {
  std::srand(42);
  for (int n = 0; n < 2000; ++n) {
    std::vector<uint8_t> body(1 + std::rand() % 32);
    for (auto &b : body) b = std::rand() & 0xff;
    CHECK(logger::vanCrc(body.data(), body.size()) == referenceVanCrc(body.data(), body.size()));
  }
}
void testVanCrcDetectsSingleBitErrors() {
  const auto frame = vanFrame({0x8c, 0x4c, 0x12, 0x34, 0x56});
  CHECK(logger::vanCrcOk(frame.data(), frame.size()));
  for (size_t byte = 1; byte < frame.size(); ++byte)
    for (int bit = 0; bit < 8; ++bit) {
      auto bad = frame; bad[byte] ^= 1u << bit;
      CHECK(!logger::vanCrcOk(bad.data(), bad.size()));
    }
}
void testVanTimingTolerance() {
  const auto frame = vanFrame({0x52, 0x40, 0xaa});
  // Scarto di 2 us su time slot da 8 us: accettato (<= quantum/3).
  auto ok = decode(encodeVan(frame, 8), 8, false, 2);
  CHECK(!ok.timingError && logger::vanCrcOk(ok.data, ok.length));
  // Scarto di 4 us: mezzo time slot, deve essere segnalato.
  auto bad = decode(encodeVan(frame, 8), 8, false, 4);
  CHECK(bad.timingError);
}

// --- KWP ---
std::vector<uint8_t> kwpFrame(uint8_t target, uint8_t source, const std::vector<uint8_t> &payload) {
  std::vector<uint8_t> f{static_cast<uint8_t>(0x80 | payload.size()), target, source};
  f.insert(f.end(), payload.begin(), payload.end());
  f.push_back(logger::checksum(f.data(), f.size()));
  return f;
}
void testKwpIncrementalParse() {
  const auto f = kwpFrame(0xf1, 0x10, {0x41, 0x0c, 0x1a, 0xf8});
  for (size_t n = 1; n < f.size(); ++n) CHECK(!logger::parseKwp(f.data(), n).complete);
  const auto p = logger::parseKwp(f.data(), f.size());
  CHECK(p.complete && p.valid && p.target == 0xf1 && p.source == 0x10 && p.length == 4 && p.offset == 3);
  auto bad = f; bad[4] ^= 0x01;
  CHECK(!logger::parseKwp(bad.data(), bad.size()).valid);
  // Lunghezze 1..63 nell'header, tutte accettate se il checksum torna.
  for (unsigned len = 1; len < 64; ++len) {
    const auto g = kwpFrame(0xf1, 0x33, std::vector<uint8_t>(len, 0x5a));
    const auto q = logger::parseKwp(g.data(), g.size());
    CHECK(q.valid && q.length == len);
  }
}
void testPidBitmapRoundTrip() {
  std::srand(99);
  for (int n = 0; n < 200; ++n) {
    for (unsigned block = 0; block <= 0xe0; block += 32) {
      uint8_t bitmap[4] = {};
      bool expected[33] = {};
      for (unsigned i = 1; i <= 32; ++i) {
        expected[i] = std::rand() & 1;
        if (expected[i]) bitmap[(i - 1) / 8] |= 0x80 >> ((i - 1) % 8);
      }
      for (unsigned i = 1; i <= 32 && block + i < 256; ++i)
        CHECK(logger::pidSupported(bitmap, block, block + i) == expected[i]);
    }
  }
}

// --- Pianificazione PID 0.3.1: replica il ciclo di kwpTask ---
void testPidScheduleFairness() {
  bool supported[256] = {};
  const unsigned live[] = {0x04, 0x05, 0x0c, 0x0d, 0x0f, 0x11, 0x42};
  for (unsigned p : live) supported[p] = true;
  supported[0x20] = supported[0x40] = true; // bitmap: mai interrogati
  unsigned count[256] = {}, slowCursor = 0;
  const unsigned rounds = 400;
  for (unsigned r = 0; r < rounds; ++r) {
    for (uint8_t pid : logger::kPriorityPids) if (logger::isLivePid(supported, pid)) ++count[pid];
    const unsigned slow = logger::nextSlowPid(supported, slowCursor);
    if (slow) { slowCursor = slow; ++count[slow]; }
  }
  CHECK(count[0x04] == rounds && count[0x0c] == rounds && count[0x0d] == rounds);
  CHECK(count[0x20] == 0 && count[0x40] == 0);
  // Quattro PID lenti a rotazione: 100 letture ciascuno su 400 giri.
  for (unsigned p : {0x05u, 0x0fu, 0x11u, 0x42u}) CHECK(count[p] == rounds / 4);
  bool edge[256] = {};
  edge[0x05] = edge[0xff] = true;
  CHECK(logger::nextSlowPid(edge, 0x05) == 0xff && logger::nextSlowPid(edge, 0xff) == 0x05);
  bool none[256] = {};
  CHECK(logger::nextSlowPid(none, 0) == 0);
}

// --- STOP: nessuna sequenza di rimbalzi sblocca un arresto già memorizzato ---
void testStopButtonRandomBounce() {
  std::srand(7);
  for (int run = 0; run < 2000; ++run) {
    logger::StopButton b;
    uint32_t now = static_cast<uint32_t>(std::rand()) * 7919u;
    bool latched = false, pressedSince = false;
    uint32_t pressedAt = 0;
    for (int step = 0; step < 200; ++step) {
      const bool pressed = std::rand() % 3 == 0;
      now += 1 + std::rand() % 20;
      if (pressed && !pressedSince) { pressedSince = true; pressedAt = now; }
      if (!pressed) pressedSince = false;
      const bool result = b.update(pressed, now);
      if (latched) CHECK(result);
      if (pressedSince && now - pressedAt >= 35) CHECK(result);
      if (!latched && (!pressedSince || now - pressedAt < 35)) CHECK(!result);
      latched = result;
    }
  }
}

// --- Calendario: parseUtc e giorno della settimana contro la libreria C ---
void testCalendarAgainstLibc() {
  for (long day = 0; day < 36525; day += 7) { // 2000..2099, un giorno a settimana
    std::time_t t = 946684800 + day * 86400 + (day % 86400);
    std::tm tm{};
    gmtime_r(&t, &tm);
    char text[32];
    std::strftime(text, sizeof(text), "%Y-%m-%dT%H:%M:%SZ", &tm);
    logger::Calendar c{};
    CHECK(logger::parseUtc(text, c));
    CHECK(c.year == tm.tm_year + 1900 && c.month == tm.tm_mon + 1 && c.day == tm.tm_mday);
    CHECK(c.hour == tm.tm_hour && c.minute == tm.tm_min && c.second == tm.tm_sec);
    CHECK(logger::weekdaySunday1(c) == tm.tm_wday + 1);
  }
}
void testSha256Text() {
  const char good[] = "00ff10A0b1c2d3e4f5061728394a5b6c7d8e9fa0b1c2d3e4f5061728394a5b6c  c3_logger.bin\n";
  uint8_t out[32] = {};
  CHECK(logger::parseSha256Hex(good, sizeof(good) - 1, out));
  CHECK(out[0] == 0x00 && out[1] == 0xff && out[3] == 0xa0 && out[31] == 0x6c);
  CHECK(logger::parseSha256Hex(good, 64, out));
  CHECK(!logger::parseSha256Hex(good, 63, out));                 // troppo corto
  char bad[sizeof(good)];
  std::memcpy(bad, good, sizeof(good));
  bad[10] = 'g';
  CHECK(!logger::parseSha256Hex(bad, sizeof(bad) - 1, out));      // cifra non valida
  bad[10] = good[10];
  bad[64] = 'x';
  CHECK(!logger::parseSha256Hex(bad, sizeof(bad) - 1, out));      // impronta più lunga di 64
}
} // namespace

int main() {
  testVanRoundTrip();
  testVanCrcMatchesReference();
  testVanCrcDetectsSingleBitErrors();
  testVanTimingTolerance();
  testKwpIncrementalParse();
  testPidBitmapRoundTrip();
  testPidScheduleFairness();
  testStopButtonRandomBounce();
  testCalendarAgainstLibc();
  testSha256Text();
  std::printf("host_tests checks=%d failures=%d\n", checks, failures);
  return failures ? 1 : 0;
}
