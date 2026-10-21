// Archivio degli ultimi valori ricevuti dal front-end (D-037). Scritto dal compito di
// collegamento, letto dall'interfaccia: accesso protetto da mutex, nessuna chiamata LVGL.
#pragma once
#include <stdint.h>

#include "fe_link.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

struct SignalValue {
  float value = 0.0f;
  felink::Quality quality = felink::Quality::kStale;
  int64_t receivedUs = 0;  // tempo locale S3 di ricezione, 0 = mai ricevuto
  bool valid() const { return receivedUs != 0; }
};

class SignalStore {
 public:
  static constexpr int kSlots = 64;

  SignalStore() { mutex_ = xSemaphoreCreateMutex(); }

  void put(uint16_t id, felink::Quality q, float v, int64_t nowUs) {
    xSemaphoreTake(mutex_, portMAX_DELAY);
    Slot* s = find(id, true);
    if (s) s->v = SignalValue{v, q, nowUs};
    xSemaphoreGive(mutex_);
  }

  // Valore con qualità declassata a "non aggiornato" se più vecchio di maxAgeUs.
  SignalValue get(uint16_t id, int64_t nowUs, int64_t maxAgeUs) {
    xSemaphoreTake(mutex_, portMAX_DELAY);
    Slot* s = find(id, false);
    SignalValue out = s ? s->v : SignalValue{};
    xSemaphoreGive(mutex_);
    if (out.valid() && nowUs - out.receivedUs > maxAgeUs) out.quality = felink::Quality::kStale;
    return out;
  }

 private:
  struct Slot {
    uint16_t id = 0;
    bool used = false;
    SignalValue v;
  };
  Slot* find(uint16_t id, bool create) {
    for (Slot& s : slots_) if (s.used && s.id == id) return &s;
    if (!create) return nullptr;
    for (Slot& s : slots_) if (!s.used) { s.used = true; s.id = id; return &s; }
    return nullptr;  // archivio pieno: il valore viene ignorato
  }
  Slot slots_[kSlots];
  SemaphoreHandle_t mutex_;
};

SignalStore& signalStore();
