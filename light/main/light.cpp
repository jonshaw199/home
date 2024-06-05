#include "light.hpp"

#include "esp_log.h"
#include "freertos/FreeRTOS.h"

typedef void (*light_effect)(Light *light, Effect *effect);

void turn_off(Light *light, Effect *effect) {
  fill_solid(&light->leds[0], light->leds.size(), CRGB::Black);
}

void beatwave(Light *light, Effect *effect) {
  uint8_t wave = beatsin8(effect->get_config().get_bpm());

  for (size_t i = 0, size = light->leds.size(); i != size; ++i) {
    EffectConfig config = effect->get_config();
    light->leds.at(i) = ColorFromPalette(config.get_palette(), i + wave, config.get_brightness(), config.get_blend_type());
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
  scheduled_effects.insert({e.get_config().get_start_time(), e});
}

void Light::do_effect() {}

