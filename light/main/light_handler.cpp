#include "light_handler.hpp"

#include "cJSON.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char* TAG = "light_handler";

static void light_task(void* arg) {
  Light *light = static_cast<Light*>(arg);

  while (1) {
    light->do_effect(esp_timer_get_time());
    FastLED.show();
    vTaskDelay(100);
  }
}

LightHandler::LightHandler(const light_map& lights) : lights(lights) {}

void LightHandler::init() {
  for (light_map::iterator it = lights.begin(); it != lights.end(); it++) {
    xTaskCreate(light_task, ("light_task_" + it->first).c_str(), 4096, (void*)&it->second, 2, NULL);
  }
}

void LightHandler::add_effect(Effect effect) {
    for (light_map::iterator it = lights.begin(); it != lights.end(); it++) {
        it->second.add_effect(effect);
    }
}
