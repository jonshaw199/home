#include "light_handler.hpp"

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
