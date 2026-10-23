// Retroilluminazione (vedere backlight.h).
#include "backlight.h"

#include <atomic>

#include "board_8048s050.h"
#include "dash_logic.h"
#include "driver/ledc.h"
#include "fe_link.h"
#include "signal_store.h"

namespace backlight {
namespace {
constexpr ledc_mode_t kMode = LEDC_LOW_SPEED_MODE;
constexpr ledc_channel_t kChannel = LEDC_CHANNEL_0;
constexpr uint32_t kMaxDuty = (1u << 10) - 1;  // 10 bit
std::atomic<int> current{0};
std::atomic<int> manual{-1};
std::atomic<uint32_t> freqHz{5000};
int64_t lastStepUs = 0;

void apply(int pct) {
  ledc_set_duty(kMode, kChannel, kMaxDuty * static_cast<uint32_t>(pct) / 100);
  ledc_update_duty(kMode, kChannel);
  current.store(pct);
}
}  // namespace

void start() {
  ledc_timer_config_t timer = {};
  timer.speed_mode = kMode;
  timer.duty_resolution = LEDC_TIMER_10_BIT;
  timer.timer_num = LEDC_TIMER_0;
  timer.freq_hz = freqHz.load();  // frequenza da verificare a banco: assenza di sfarfallio e ronzio
  timer.clk_cfg = LEDC_AUTO_CLK;
  ledc_timer_config(&timer);
  ledc_channel_config_t channel = {};
  channel.gpio_num = board::kBacklight;
  channel.speed_mode = kMode;
  channel.channel = kChannel;
  channel.timer_sel = LEDC_TIMER_0;
  channel.duty = 0;
  ledc_channel_config(&channel);
}

void update(int64_t nowUs) {
  if (nowUs - lastStepUs < 10000) return;  // un passo dell'1 % ogni 10 ms
  lastStepUs = nowUs;
  SignalStore& store = signalStore();
  const SignalValue lights = store.get(felink::sig::kLightsFlags, nowUs, 1000000);
  const SignalValue ntc = store.get(felink::sig::kNtcDisplayC, nowUs, 5000000);
  auto fresh = [](const SignalValue& v) { return v.valid() && v.quality != felink::Quality::kStale; };
  const bool lowBeam = fresh(lights) && (static_cast<uint32_t>(lights.value) & dash::kLowBeam) != 0;
  const int automatic = dash::backlightTarget(lowBeam, fresh(ntc), static_cast<int>(ntc.value + 0.5f));
  const int target = manual.load() >= 0 ? manual.load() : automatic;
  const int now = current.load();
  if (now != target) apply(now < target ? now + 1 : now - 1);
}

int percent() { return current.load(); }

void setManual(int pct) { manual.store(pct < 0 ? -1 : pct > 100 ? 100 : pct); }

bool setFrequency(uint32_t hz) {
  if (ledc_set_freq(kMode, LEDC_TIMER_0, hz) != ESP_OK) return false;
  freqHz.store(hz);
  return true;
}

uint32_t frequency() { return freqHz.load(); }
}  // namespace backlight
