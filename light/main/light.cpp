#include "light.hpp"

#include "esp_log.h"
#include "freertos/FreeRTOS.h"

const char *TAG = "light";

typedef void (*light_effect)(Light &light, Effect &effect);

void turn_off(Light &light, Effect &effect) {
  fill_solid(&light.leds[0], light.leds.size(), CRGB::Black);
}

void beatwave(Light &light, Effect &effect) {
  uint8_t wave = beatsin8(effect.get_bpm());

  for (size_t i = 0, size = light.leds.size(); i != size; ++i) {
      light.leds.at(i) = ColorFromPalette(
          effect.get_palette(),
          i + wave,
          effect.get_brightness(),
          effect.get_blend_type()
      );
  }
}

std::map<EffectType, light_effect> effect_map{
  {TURN_OFF, turn_off},
  {BEATWAVE, beatwave}
};

Light::Light(int led_cnt) {
  leds = std::vector<CRGB>(led_cnt);
}

void Light::add_effect(Effect e) {
  ESP_LOGI(TAG, "Adding effect %d", e.get_type());
  scheduled_effects.insert({e.get_start_time(), e});
}

void Light::do_effect(uint64_t time) {
  for (scheduled_effect_multimap::iterator it = scheduled_effects.begin(); it != scheduled_effects.end();) {
    if (it->first <= time) {
      int64_t end_time = it->first + it->second.get_duration();
      if (time < end_time) {
        auto entry = effect_map.find(it->second.get_type());
        if (entry == effect_map.end()) {
          // not found
          ESP_LOGE(TAG, "EffectType not found: %d", it->second.get_type());
        } else {
          entry->second(*this, it->second);
        }
        ++it;
      } else {
        ESP_LOGI(TAG, "Stopping effect %d", it->second.get_type());
        it = scheduled_effects.erase(it);
      }
    } else {
      break;
    }
  }
}

