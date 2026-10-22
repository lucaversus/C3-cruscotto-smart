// Protocollo front-end ESP32 <-> ESP32-S3 (D-029), versione 1. Solo C++14, nessuna
// dipendenza: usato dai due firmware e dai test host. Specifica: cruscotto/docs/protocollo-fe-s3.md
//
// Trama sul filo: COBS(payload) seguito da 0x00. Payload:
//   [tipo u8][sequenza u8][tempo_us u32 LE][corpo ...][CRC-16/CCITT-FALSE u16 LE]
// Il CRC copre tipo, sequenza, tempo e corpo.
#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>

namespace felink {

constexpr uint8_t kProtocolVersion = 1;
constexpr size_t kMaxPayload = 250;            // payload prima di COBS, CRC compreso
constexpr size_t kHeaderSize = 6;              // tipo + sequenza + tempo
constexpr size_t kMaxBody = kMaxPayload - kHeaderSize - 2;
constexpr size_t kMaxEncoded = kMaxPayload + kMaxPayload / 254 + 2;  // COBS + delimitatore

enum class Type : uint8_t {
  kHello = 0x01,      // FE->S3: versione protocollo, capacità, versione firmware (testo)
  kHeartbeat = 0x02,  // in entrambe le direzioni: stato e contatori di errore
  kSignals = 0x10,    // FE->S3: n x {id u16, qualità u8, valore float32}
  kRawVan = 0x11,     // FE->S3: {iden u16, flag u8, dati...} frame VAN grezzo
  kRawKwp = 0x12,     // FE->S3: {servizio u8, dati...} risposta KWP grezza
  kEvent = 0x13,      // FE->S3: {codice u16, argomento i32}
  kDtcList = 0x14,    // FE->S3: {n u8, codici u16...} servizio 0x03 (D-035)
  kCommand = 0x30,    // S3->FE: {comando u8, argomento i32}
  kAck = 0x31,        // in entrambe le direzioni: {tipo confermato u8, sequenza u8, esito u8}
};

// Qualità di ogni valore: distingue misurato, non aggiornato, decodifica da verificare
// e simulato (le prove a banco non devono mai sembrare dati dell'auto, D-016).
enum class Quality : uint8_t { kValid = 0, kStale = 1, kUnverified = 2, kSimulated = 3, kError = 4 };

// Registro degli identificativi dei segnali. Gli id OBD sono 0x0100 | PID (servizio 0x01).
namespace sig {
constexpr uint16_t kRpm = 0x0001, kSpeedKmh = 0x0002, kCoolantC = 0x0003, kOutsideC = 0x0004,
                   kFuelPct = 0x0005, kOdometerKm = 0x0006, kLightsFlags = 0x0007,
                   kWarningFlags = 0x0008, kStalkButtons = 0x0009,
                   kBatteryV = 0x0010, kIgnition = 0x0011, kFuelL100 = 0x0012,
                   kAccelX = 0x0020, kAccelY = 0x0021, kAccelZ = 0x0022,
                   kGyroX = 0x0023, kGyroY = 0x0024, kGyroZ = 0x0025, kImuTempC = 0x0026,
                   kNtcDisplayC = 0x0030, kNtcBoardC = 0x0031, kFanPct = 0x0040, kFanRpm = 0x0041;
constexpr uint16_t obdPid(uint8_t pid) { return static_cast<uint16_t>(0x0100u | pid); }
}  // namespace sig

namespace cmd {
constexpr uint8_t kRequestDtc = 0x01, kRequestFreezeFrame = 0x02, kSetRawForwarding = 0x03,
                  kTimeSyncUnixS = 0x04, kEnterFirmwareUpdate = 0x05;
}  // namespace cmd

inline uint16_t crc16(const uint8_t* data, size_t len, uint16_t crc = 0xFFFF) {
  for (size_t i = 0; i < len; ++i) {
    crc ^= static_cast<uint16_t>(data[i]) << 8;
    for (int b = 0; b < 8; ++b) crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021) : static_cast<uint16_t>(crc << 1);
  }
  return crc;
}

// COBS: nessun byte 0x00 nell'uscita; restituisce la lunghezza codificata.
inline size_t cobsEncode(const uint8_t* in, size_t len, uint8_t* out) {
  size_t read = 0, write = 1, code_pos = 0;
  uint8_t code = 1;
  while (read < len) {
    if (in[read] == 0) {
      out[code_pos] = code;
      code = 1;
      code_pos = write++;
      ++read;
    } else {
      out[write++] = in[read++];
      if (++code == 0xFF) {
        out[code_pos] = code;
        code = 1;
        code_pos = write++;
      }
    }
  }
  out[code_pos] = code;
  return write;
}

// Restituisce la lunghezza decodificata, 0 se la sequenza non è COBS valida.
inline size_t cobsDecode(const uint8_t* in, size_t len, uint8_t* out) {
  size_t read = 0, write = 0;
  while (read < len) {
    const uint8_t code = in[read];
    if (code == 0 || read + code > len + 1) return 0;
    ++read;
    for (uint8_t i = 1; i < code; ++i) {
      if (read >= len) return 0;
      out[write++] = in[read++];
    }
    if (code != 0xFF && read != len) out[write++] = 0;
  }
  return write;
}

inline void putU16(uint8_t* p, uint16_t v) { p[0] = static_cast<uint8_t>(v); p[1] = static_cast<uint8_t>(v >> 8); }
inline void putU32(uint8_t* p, uint32_t v) { for (int i = 0; i < 4; ++i) p[i] = static_cast<uint8_t>(v >> (8 * i)); }
inline uint16_t getU16(const uint8_t* p) { return static_cast<uint16_t>(p[0] | (p[1] << 8)); }
inline uint32_t getU32(const uint8_t* p) {
  return static_cast<uint32_t>(p[0]) | (static_cast<uint32_t>(p[1]) << 8) |
         (static_cast<uint32_t>(p[2]) << 16) | (static_cast<uint32_t>(p[3]) << 24);
}

struct Frame {
  Type type = Type::kHeartbeat;
  uint8_t seq = 0;
  uint32_t timeUs = 0;
  uint8_t body[kMaxBody] = {};
  size_t bodyLen = 0;
};

// Codifica una trama completa (COBS + 0x00). Restituisce i byte scritti, 0 se il corpo è troppo lungo.
inline size_t encode(const Frame& f, uint8_t* out) {
  if (f.bodyLen > kMaxBody) return 0;
  uint8_t raw[kMaxPayload];
  raw[0] = static_cast<uint8_t>(f.type);
  raw[1] = f.seq;
  putU32(raw + 2, f.timeUs);
  memcpy(raw + kHeaderSize, f.body, f.bodyLen);
  const size_t n = kHeaderSize + f.bodyLen;
  putU16(raw + n, crc16(raw, n));
  const size_t enc = cobsEncode(raw, n + 2, out);
  out[enc] = 0;
  return enc + 1;
}

// Aggiunge un segnale a una trama kSignals; false se non c'è spazio.
inline bool addSignal(Frame& f, uint16_t id, Quality q, float value) {
  if (f.bodyLen == 0) f.body[f.bodyLen++] = 0;  // contatore in testa
  if (f.bodyLen + 7 > kMaxBody) return false;
  uint8_t* p = f.body + f.bodyLen;
  putU16(p, id);
  p[2] = static_cast<uint8_t>(q);
  uint32_t bits;
  memcpy(&bits, &value, sizeof bits);
  putU32(p + 3, bits);
  f.bodyLen += 7;
  ++f.body[0];
  return true;
}

struct Signal {
  uint16_t id;
  Quality quality;
  float value;
};

// Legge il segnale i-esimo da una trama kSignals già validata.
inline bool getSignal(const Frame& f, uint8_t i, Signal& s) {
  if (f.type != Type::kSignals || f.bodyLen < 1 || i >= f.body[0] || 1 + 7u * (i + 1u) > f.bodyLen) return false;
  const uint8_t* p = f.body + 1 + 7 * i;
  s.id = getU16(p);
  s.quality = static_cast<Quality>(p[2]);
  const uint32_t bits = getU32(p + 3);
  memcpy(&s.value, &bits, sizeof bits);
  return true;
}

// Ricezione byte per byte: restituisce true quando una trama valida è pronta in `frame`.
class Decoder {
 public:
  bool push(uint8_t byte, Frame& frame) {
    if (byte != 0) {
      if (len_ < sizeof buf_) buf_[len_++] = byte; else overflow_ = true;
      return false;
    }
    const bool ok = !overflow_ && len_ > 0 && parse(frame);
    if (!ok && (len_ > 0 || overflow_)) ++errors_;
    len_ = 0;
    overflow_ = false;
    return ok;
  }
  uint32_t errors() const { return errors_; }

 private:
  bool parse(Frame& frame) {
    uint8_t raw[kMaxPayload + 2];
    if (len_ > kMaxEncoded) return false;
    const size_t n = cobsDecode(buf_, len_, raw);
    if (n < kHeaderSize + 2 || n > kMaxPayload) return false;
    if (crc16(raw, n - 2) != getU16(raw + n - 2)) return false;
    frame.type = static_cast<Type>(raw[0]);
    frame.seq = raw[1];
    frame.timeUs = getU32(raw + 2);
    frame.bodyLen = n - kHeaderSize - 2;
    memcpy(frame.body, raw + kHeaderSize, frame.bodyLen);
    return true;
  }
  uint8_t buf_[kMaxEncoded] = {};
  size_t len_ = 0;
  bool overflow_ = false;
  uint32_t errors_ = 0;
};

}  // namespace felink
