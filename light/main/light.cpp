#include "light.hpp"

#include "esp_log.h"
#include "freertos/FreeRTOS.h"

static const char *TAG = "light";

void turn_off(Light *light) {
  fill_solid(&light->leds[0], light->leds.size(), CRGB::Black);
}

void beatwave(Light *light) {
  uint8_t wave = beatsin8(light->get_bpm());

  for (size_t i = 0, size = light->leds.size(); i != size; ++i) {
    light->leds.at(i) = ColorFromPalette(light->get_palette(), i + wave, light->get_brightness(), light->get_blend_type());
  }
}

Light::Light(int led_cnt) {
  leds = std::vector<CRGB>(led_cnt);
}

void Light::do_effect() {
  effect(this);
}

const CRGBPalette16& Light::get_palette() {
  return palette;
}

void Light::set_palette(const CRGBPalette16& p) {
  palette = p;
}

accum88 Light::get_bpm() {
  return bpm;
}

void Light::set_bpm(accum88 b) {
  bpm = b;
}

uint8_t Light::get_brightness() {
  return brightness;
}

void Light::set_brightness(uint8_t b) {
  brightness = b;
}

TBlendType Light::get_blend_type() {
  return blend_type;
}

void Light::set_blend_type(TBlendType b) {
  blend_type = b;
}

static void light_task(void* arg) {
  Light *light = static_cast<Light*>(arg);

  while (1) {
    light->do_effect();
    vTaskDelay(1000);
  }
}

LightHandler::LightHandler(const light_map& lights) : lights(lights) {}

void LightHandler::init() {
  for (light_map::iterator it = lights.begin(); it != lights.end(); it++) {
    xTaskCreate(light_task, ("light_task_" + it->first).c_str(), 2048, (void*)it->second, 1, NULL);
  }
}
