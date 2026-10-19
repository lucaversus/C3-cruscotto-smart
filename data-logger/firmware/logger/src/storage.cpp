#include "storage.h"
#include "peripherals.h"
#include <esp_system.h>
#include <esp_timer.h>
#include <inttypes.h>

namespace {
const char *sourceName(Source source) {
  switch (source) {
    case Source::Van: return "van_rx";
    case Source::KwpTx: return "kwp_tx";
    case Source::KwpRx: return "kwp_rx";
    case Source::ObdPid: return "obd_pid";
    default: return "system";
  }
}
constexpr char header[] = "schema_version,session_id,sequence,source,mono_us,rtc_calendar,rtc_state,rtc_read_mono_us,event,frame_id,id,chunk_offset,raw_hex,value,unit,queue_dropped,van_bad,kwp_errors\n";
}
bool LogStorage::begin() {
  spi.begin(logger::kSck, logger::kMiso, logger::kMosi, logger::kSdCs); fs.end();
  if (!fs.begin(SdSpiConfig(logger::kSdCs, DEDICATED_SPI, logger::kSpiHz, &spi))) { error = "mount_failed"; return false; }
  session = esp_random();
  return openNext();
}
bool LogStorage::openNext() {
  for (; nextName <= 999999; ++nextName) {
    snprintf(path, sizeof(path), "/c3_%06lu.csv", static_cast<unsigned long>(nextName));
    if (fs.exists(path)) continue;
    if (!file.open(&fs, path, O_RDWR | O_CREAT | O_EXCL)) { error = "open_failed"; return false; }
    ++nextName; bytesWritten = used = 0;
    if (!add(header, sizeof(header) - 1) || !sync()) { error = "header_failed"; return false; }
    error = "recording"; return true;
  }
  error = "namespace_full"; return false;
}
bool LogStorage::flushBuffer() {
  if (!used) return true;
  if (file.write(buffer, used) != used || file.getWriteError()) { error = "write_failed"; return false; }
  bytesWritten += used; used = 0;
  return true;
}
bool LogStorage::add(const char *text, size_t length) {
  if (!file || length > sizeof(buffer)) return false;
  if (used + length > sizeof(buffer) && !flushBuffer()) return false;
  memcpy(buffer + used, text, length); used += length;
  return true;
}
bool LogStorage::sync() {
  if (!flushBuffer() || !file.sync() || file.getWriteError()) { error = "sync_failed"; return false; }
  return true;
}
bool LogStorage::append(const Record &record) {
  if (bytesWritten + used >= logger::kSegmentBytes && strcmp(record.event, "segment_end") && strcmp(record.event, "stop_footer")) {
    if (!finish("segment_end") || !openNext()) return false;
  }
  char hex[129] = {}, value[24] = {};
  if (record.length > sizeof(record.raw)) { error = "record_overflow"; return false; }
  static const char alphabet[] = "0123456789ABCDEF";
  for (unsigned i = 0; i < record.length; ++i) { hex[i * 2] = alphabet[record.raw[i] >> 4]; hex[i * 2 + 1] = alphabet[record.raw[i] & 15]; }
  if (record.source == Source::ObdPid) snprintf(value, sizeof(value), "%.3f", record.value);
  const int n = snprintf(lastRow, sizeof(lastRow),
    "2,%08" PRIX32 ",%" PRIu64 ",%s,%" PRId64 ",%s,%s,%" PRId64 ",%s,%lu,%lu,%u,%s,%s,%s,%lu,%lu,%lu\n",
    session, rows + 1, sourceName(record.source), record.monoUs, rtc.calendar, rtc.state, rtc.readMonoUs,
    record.event, static_cast<unsigned long>(record.frame), static_cast<unsigned long>(record.id), record.offset,
    hex, value, record.unit, static_cast<unsigned long>(capture.dropped.load()), static_cast<unsigned long>(capture.vanBad.load()), static_cast<unsigned long>(capture.kwpErrors.load()));
  if (n <= 0 || static_cast<size_t>(n) >= sizeof(lastRow)) { error = "row_overflow"; return false; }
  lastLength = n;
  if (!add(lastRow, lastLength)) return false;
  ++rows; return true;
}
bool LogStorage::finish(const char *event) {
  Record footer{}; footer.monoUs = esp_timer_get_time(); footer.event = event;
  if (!append(footer) || !sync()) return false;
  if (!file.close()) { error = "close_failed"; return false; }
  FsFile verify;
  char tail[sizeof(lastRow)] = {};
  bool ok = verify.open(&fs, path, O_RDONLY) && verify.fileSize() == bytesWritten && bytesWritten >= lastLength &&
            verify.seekSet(bytesWritten - lastLength) && verify.read(tail, lastLength) == static_cast<int>(lastLength) && memcmp(tail, lastRow, lastLength) == 0;
  if (verify && !verify.close()) ok = false;
  if (!ok) { error = "verify_failed"; return false; }
  error = "saved"; return true;
}
void LogStorage::abandon() {
  if (file) file.close(); // Best effort after an already-reported error, never SALVATO.
  fs.end();
}
