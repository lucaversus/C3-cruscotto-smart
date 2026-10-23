// Scatola nera: memoria circolare in PSRAM e salvataggio degli eventi su LittleFS (D-037).
#include "blackbox.h"

#include <dirent.h>
#include <sys/stat.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "esp_heap_caps.h"
#include "esp_littlefs.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "version.h"

namespace blackbox {
namespace {
constexpr uint32_t kCapacity = 65536;        // ~768 KB in PSRAM, > 60 s ai ritmi previsti
constexpr uint32_t kBeforeMs = 50000, kAfterMs = 10000;
constexpr char kBase[] = "/data";
constexpr char kDir[] = "/data/ev";
constexpr char kVersion[] = "ui-idf " FW_VERSION_TEXT;
// Rotazione: prima di salvare si cancellano gli eventi più vecchi finché resta questo margine
// libero e finché gli eventi sono meno di kMaxEvents (partizione storage da 8,3 MB, condivisa
// in futuro con i messaggi audio, D-028).
constexpr size_t kMarginBytes = 1024 * 1024;
constexpr unsigned kMaxEvents = 30;
constexpr bool mustFree(size_t total, size_t used, size_t needed, unsigned files) {
  return used + needed + kMarginBytes > total || files >= kMaxEvents;
}
static_assert(mustFree(8000000, 7500000, 200000, 1) && !mustFree(8000000, 1000000, 200000, 5) &&
                  mustFree(8000000, 0, 0, kMaxEvents), "rotazione degli eventi");

struct Sample {        // 12 byte, formato del file evento
  uint32_t ms;         // millisecondi dall'avvio dell'S3
  uint16_t id;
  uint8_t quality;
  uint8_t reserved;
  float value;
};
static_assert(sizeof(Sample) == 12, "formato campione");

struct FileHeader {    // 48 byte in testa a ogni file evento, little endian
  char magic[4];       // "C3BB"
  uint16_t format;     // 1
  uint8_t reason;
  uint8_t sampleSize;  // 12
  uint32_t triggerMs;
  uint32_t count;
  char firmware[32];
};
static_assert(sizeof(FileHeader) == 48, "formato intestazione");

Sample* ring = nullptr;
uint32_t head = 0, filled = 0;
SemaphoreHandle_t ringMutex = nullptr;
SemaphoreHandle_t triggerSem = nullptr;
portMUX_TYPE statsLock = portMUX_INITIALIZER_UNLOCKED;
Stats st;
Reason pendingReason = Reason::kManual;
uint32_t pendingMs = 0;
uint32_t nextFile = 1;

// Numero del prossimo file; i file evento vuoti (salvataggi falliti a memoria piena) vengono
// cancellati, così non contano nel limite kMaxEvents.
void scanNextFileNumber() {
  DIR* dir = opendir(kDir);
  if (!dir) return;
  while (dirent* e = readdir(dir)) {
    unsigned n = 0;
    if (sscanf(e->d_name, "evt_%u.bin", &n) != 1) continue;
    if (n >= nextFile) nextFile = n + 1;
    char path[300];
    struct stat info;
    snprintf(path, sizeof path, "%s/%s", kDir, e->d_name);
    if (stat(path, &info) == 0 && info.st_size == 0) remove(path);
  }
  closedir(dir);
}

// Numero del file evento più vecchio e quanti eventi ci sono; 0 se nessuno.
unsigned oldestEvent(unsigned& count) {
  unsigned oldest = 0;
  count = 0;
  DIR* dir = opendir(kDir);
  if (!dir) return 0;
  while (dirent* e = readdir(dir)) {
    unsigned n = 0;
    if (sscanf(e->d_name, "evt_%u.bin", &n) != 1) continue;
    ++count;
    if (oldest == 0 || n < oldest) oldest = n;
  }
  closedir(dir);
  return oldest;
}

// Cancella gli eventi più vecchi finché c'è spazio per il nuovo con il margine.
void makeRoom(size_t needed) {
  while (true) {
    size_t total = 0, used = 0;
    unsigned count = 0;
    const unsigned oldest = oldestEvent(count);
    if (esp_littlefs_info("storage", &total, &used) != ESP_OK || oldest == 0) return;
    if (!mustFree(total, used, needed, count)) return;
    char path[48];
    snprintf(path, sizeof path, "%s/evt_%04u.bin", kDir, oldest);
    if (remove(path) != 0) return;
    printf("blackbox cancellato=%s per fare spazio (eventi=%u, usati=%uKB)\n", path, count - 1,
           static_cast<unsigned>(used / 1024));
    portENTER_CRITICAL(&statsLock);
    ++st.eventsDeleted;
    portEXIT_CRITICAL(&statsLock);
  }
}

void refreshFsInfo() {
  size_t total = 0, used = 0;
  if (esp_littlefs_info("storage", &total, &used) == ESP_OK) {
    portENTER_CRITICAL(&statsLock);
    st.fsTotalKb = total / 1024;
    st.fsUsedKb = used / 1024;
    portEXIT_CRITICAL(&statsLock);
  }
}

bool saveWindow(Reason reason, uint32_t triggerMs) {
  // Copia della finestra sotto mutex in un buffer temporaneo in PSRAM.
  Sample* tmp = static_cast<Sample*>(heap_caps_malloc(kCapacity * sizeof(Sample), MALLOC_CAP_SPIRAM));
  if (!tmp) return false;
  const uint32_t from = triggerMs > kBeforeMs ? triggerMs - kBeforeMs : 0;
  const uint32_t to = triggerMs + kAfterMs;
  uint32_t n = 0;
  xSemaphoreTake(ringMutex, portMAX_DELAY);
  const uint32_t oldest = (head + kCapacity - filled) % kCapacity;
  for (uint32_t i = 0; i < filled; ++i) {
    const Sample& s = ring[(oldest + i) % kCapacity];
    if (s.ms >= from && s.ms <= to) tmp[n++] = s;
  }
  xSemaphoreGive(ringMutex);
  makeRoom(sizeof(FileHeader) + n * sizeof(Sample));

  FileHeader h = {};
  memcpy(h.magic, "C3BB", 4);
  h.format = 1;
  h.reason = static_cast<uint8_t>(reason);
  h.sampleSize = sizeof(Sample);
  h.triggerMs = triggerMs;
  h.count = n;
  strncpy(h.firmware, kVersion, sizeof h.firmware - 1);
  char path[48];
  snprintf(path, sizeof path, "%s/evt_%04u.bin", kDir, static_cast<unsigned>(nextFile));
  FILE* f = fopen(path, "wb");
  bool ok = f != nullptr;
  if (ok) {
    ok = fwrite(&h, sizeof h, 1, f) == 1 && fwrite(tmp, sizeof(Sample), n, f) == n;
    ok = (fclose(f) == 0) && ok;
  }
  heap_caps_free(tmp);
  if (ok) ++nextFile;
  printf("blackbox evento=%u motivo=%u campioni=%u file=%s esito=%s\n", static_cast<unsigned>(nextFile - (ok ? 1 : 0)),
         static_cast<unsigned>(reason), static_cast<unsigned>(n), path, ok ? "OK" : "ERRORE");
  return ok;
}

void saverTask(void*) {
  while (true) {
    xSemaphoreTake(triggerSem, portMAX_DELAY);
    // Attende la parte successiva all'evento, poi salva.
    while (static_cast<uint32_t>(esp_timer_get_time() / 1000) < pendingMs + kAfterMs) vTaskDelay(pdMS_TO_TICKS(200));
    const bool ok = st.fsMounted && saveWindow(pendingReason, pendingMs);
    portENTER_CRITICAL(&statsLock);
    if (ok) ++st.eventsSaved; else ++st.eventsFailed;
    st.pending = false;
    portEXIT_CRITICAL(&statsLock);
    refreshFsInfo();
  }
}
}  // namespace

bool start() {
  ring = static_cast<Sample*>(heap_caps_calloc(kCapacity, sizeof(Sample), MALLOC_CAP_SPIRAM));
  ringMutex = xSemaphoreCreateMutex();
  triggerSem = xSemaphoreCreateBinary();
  if (!ring || !ringMutex || !triggerSem) return false;
  st.capacity = kCapacity;

  esp_vfs_littlefs_conf_t conf = {};
  conf.base_path = kBase;
  conf.partition_label = "storage";
  conf.format_if_mount_failed = true;
  st.fsMounted = esp_vfs_littlefs_register(&conf) == ESP_OK;
  if (st.fsMounted) {
    mkdir(kDir, 0775);
    scanNextFileNumber();
    refreshFsInfo();
  }
  xTaskCreatePinnedToCore(saverTask, "blackbox", 4096, nullptr, 3, nullptr, 0);
  return st.fsMounted;
}

void record(uint16_t id, felink::Quality q, float value, int64_t nowUs) {
  if (!ring) return;
  Sample s;
  s.ms = static_cast<uint32_t>(nowUs / 1000);
  s.id = id;
  s.quality = static_cast<uint8_t>(q);
  s.reserved = 0;
  s.value = value;
  xSemaphoreTake(ringMutex, portMAX_DELAY);
  ring[head] = s;
  head = (head + 1) % kCapacity;
  if (filled < kCapacity) ++filled;
  xSemaphoreGive(ringMutex);
}

bool trigger(Reason reason, int64_t nowUs) {
  portENTER_CRITICAL(&statsLock);
  const bool busy = st.pending;
  if (!busy) {
    st.pending = true;
    pendingReason = reason;
    pendingMs = static_cast<uint32_t>(nowUs / 1000);
  }
  portEXIT_CRITICAL(&statsLock);
  if (!busy) xSemaphoreGive(triggerSem);
  return !busy;
}

Stats stats() {
  Stats copy;
  portENTER_CRITICAL(&statsLock);
  copy = st;
  portEXIT_CRITICAL(&statsLock);
  xSemaphoreTake(ringMutex, portMAX_DELAY);
  copy.filled = filled;
  xSemaphoreGive(ringMutex);
  return copy;
}

}  // namespace blackbox
