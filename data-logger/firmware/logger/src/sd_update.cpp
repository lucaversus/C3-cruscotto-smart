// Aggiornamento del firmware dalla MicroSD (vedere sd_update.h e README del firmware).
// Sulla scheda: /update/c3_logger.bin e /update/c3_logger.sha256 (preparati da
// tools/prepara-aggiornamento-sd.py). Dopo il tentativo il file .bin viene rinominato
// .done (installato) o .bad (scartato), così l'aggiornamento non si ripete a ogni avvio.
#include "sd_update.h"

#include <Arduino.h>
#include <SPI.h>
#include <SdFat.h>
#include <Update.h>
#include <esp_ota_ops.h>
#include <mbedtls/md.h>

#include "config.h"
#include "logger_logic.h"
#include "peripherals.h"

// La conferma della nuova versione la dà il firmware (confirmWhenStable), non il core
// Arduino all'avvio: se la versione nuova si blocca prima, il bootloader torna alla precedente.
extern "C" bool verifyRollbackLater() { return true; }

namespace sdupdate {
namespace {
constexpr size_t kChunk = 4096;
uint8_t chunk[kChunk];

void say(const char *line, const char *oled) {
  Serial.printf("sd_update %s\n", line);
  drawStatus("AGGIORNAMENTO", oled, 0, 0);
}

// Rinomina il file del firmware (.done o .bad), sostituendo un eventuale file precedente.
void retire(SdFs &fs, const char *suffix) {
  char target[48];
  snprintf(target, sizeof(target), "%s.%s", logger::kUpdateBin, suffix);
  if (fs.exists(target)) fs.remove(target);
  if (!fs.rename(logger::kUpdateBin, target)) Serial.println("sd_update rename_failed");
}

bool readExpected(SdFs &fs, uint8_t expected[32]) {
  FsFile file;
  char text[100] = {};
  if (!file.open(&fs, logger::kUpdateSha, O_RDONLY)) return false;
  const int n = file.read(text, sizeof(text) - 1);
  file.close();
  return n > 0 && logger::parseSha256Hex(text, static_cast<size_t>(n), expected);
}

bool hashFile(FsFile &file, uint8_t digest[32]) {
  mbedtls_md_context_t ctx;
  mbedtls_md_init(&ctx);
  bool ok = mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), 0) == 0 && mbedtls_md_starts(&ctx) == 0;
  for (int n; ok && (n = file.read(chunk, kChunk)) > 0;) ok = mbedtls_md_update(&ctx, chunk, n) == 0;
  ok = ok && mbedtls_md_finish(&ctx, digest) == 0;
  mbedtls_md_free(&ctx);
  return ok;
}

bool install(FsFile &file) {
  const size_t size = file.fileSize();
  if (!Update.begin(size)) return false;  // nessuna partizione libera o file troppo grande
  file.rewind();
  for (int n; (n = file.read(chunk, kChunk)) > 0;) {
    if (Update.write(chunk, n) != static_cast<size_t>(n)) { Update.abort(); return false; }
  }
  return Update.end(true);  // verifica l'immagine e la imposta per il prossimo avvio
}
}  // namespace

void rollbackIfRequested() {
  const uint32_t start = millis();
  while (digitalRead(logger::kStopPin) == LOW) {
    if (millis() - start >= logger::kRollbackHoldMs) {
      const esp_partition_t *other = esp_ota_get_next_update_partition(nullptr);
      esp_app_desc_t desc;
      if (other && esp_ota_get_partition_description(other, &desc) == ESP_OK &&
          esp_ota_set_boot_partition(other) == ESP_OK) {
        Serial.printf("sd_update rollback to=%s version=%s\n", other->label, desc.version);
        drawStatus("VERSIONE PRECEDENTE", "RIAVVIO", 0, 0);
        delay(1500);
        ESP.restart();
      }
      Serial.println("sd_update rollback_unavailable");
      return;
    }
    delay(10);
  }
}

void installFromCard() {
  SPIClass spi(VSPI);
  SdFs fs;
  spi.begin(logger::kSck, logger::kMiso, logger::kMosi, logger::kSdCs);
  if (!fs.begin(SdSpiConfig(logger::kSdCs, DEDICATED_SPI, logger::kSpiHz, &spi))) { spi.end(); return; }
  FsFile file;
  if (file.open(&fs, logger::kUpdateBin, O_RDONLY)) {
    uint8_t expected[32], actual[32];
    say("found", "VERIFICA FILE");
    if (!readExpected(fs, expected)) {
      say("sha256_missing_or_invalid", "IMPRONTA ASSENTE");
      file.close();
      retire(fs, "bad");
    } else if (!hashFile(file, actual) || memcmp(expected, actual, sizeof(actual)) != 0) {
      say("sha256_mismatch", "FILE DANNEGGIATO");
      file.close();
      retire(fs, "bad");
    } else {
      say("writing", "NON SPEGNERE");
      const bool ok = install(file);
      file.close();
      retire(fs, ok ? "done" : "bad");
      fs.end();
      spi.end();
      if (ok) {
        say("installed restart", "RIAVVIO");
        delay(1500);
        ESP.restart();
      }
      Serial.printf("sd_update failed error=%s\n", Update.errorString());
      return;
    }
  }
  fs.end();
  spi.end();
}

void confirmWhenStable(uint32_t nowMs) {
  static bool done = false;
  if (done || nowMs < logger::kConfirmMs) return;
  done = true;
  esp_ota_img_states_t state;
  if (esp_ota_get_state_partition(esp_ota_get_running_partition(), &state) == ESP_OK &&
      state == ESP_OTA_IMG_PENDING_VERIFY) {
    Serial.printf("sd_update confirmed=%s\n", esp_err_to_name(esp_ota_mark_app_valid_cancel_rollback()));
  }
}
}  // namespace sdupdate
