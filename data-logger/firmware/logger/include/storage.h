#pragma once
#include <SdFat.h>
#include <SPI.h>
#include "acquisition.h"
class LogStorage {
 public:
  bool begin();
  bool append(const Record &record);
  bool sync();
  bool finish(const char *event);
  void abandon();
  const char *error = "attesa_sd";
  char path[32] = {};
  uint64_t rows = 0;
 private:
  SPIClass spi{VSPI};
  SdFs fs;
  FsFile file;
  uint32_t session = 0, nextName = 1;
  uint64_t bytesWritten = 0;
  size_t used = 0, lastLength = 0;
  char buffer[8192] = {}, lastRow[512] = {};
  bool openNext();
  bool add(const char *text, size_t length);
  bool flushBuffer();
};
