// Riconoscimento della pressione lunga e registrazione dell'etichetta (D-037).
#include "labels.h"

#include <atomic>

#include "blackbox.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace labels {
namespace {
std::atomic<int64_t> last{0};
std::atomic<uint32_t> total{0};
std::atomic<uint32_t> shortPresses{0};

// Rilevatore di pressione lunga: scatta una sola volta per pressione.
struct LongPress {
  int64_t since = 0;
  bool fired = false;
  bool update(bool pressed, int64_t nowUs) {
    if (!pressed) { since = 0; fired = false; return false; }
    if (since == 0) since = nowUs;
    if (!fired && nowUs - since >= kLongPressUs) { fired = true; return true; }
    return false;
  }
};

LongPress stalk, bootButton;

void fire(int64_t nowUs) {
  if (blackbox::trigger(blackbox::Reason::kUserLabel, nowUs)) {
    last.store(nowUs);
    total.fetch_add(1);
  }
}

void bootTask(void*) {
  gpio_reset_pin(GPIO_NUM_0);
  gpio_set_direction(GPIO_NUM_0, GPIO_MODE_INPUT);
  gpio_set_pull_mode(GPIO_NUM_0, GPIO_PULLUP_ONLY);
  while (true) {
    const int64_t now = esp_timer_get_time();
    const bool pressed = gpio_get_level(GPIO_NUM_0) == 0;
    // Pressione breve (rilascio prima dei 2 s, almeno 50 ms): solo debug, prova lampade.
    if (!pressed && bootButton.since != 0 && !bootButton.fired) shortPresses.fetch_add(1);
    if (bootButton.update(pressed, now)) fire(now);
    vTaskDelay(pdMS_TO_TICKS(50));
  }
}
}  // namespace

void start() { xTaskCreatePinnedToCore(bootTask, "labels", 2048, nullptr, 2, nullptr, 0); }

void onStalkButtons(float bits, int64_t nowUs) {
  // Qualsiasi tasto premuto a lungo: la scelta del tasto dedicato si farà sul veicolo.
  if (stalk.update(bits != 0.0f, nowUs)) fire(nowUs);
}

int64_t lastLabelUs() { return last.load(); }
uint32_t count() { return total.load(); }
uint32_t bootShortPresses() { return shortPresses.load(); }
}  // namespace labels
