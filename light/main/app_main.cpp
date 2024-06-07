/*
 * SPDX-FileCopyrightText: 2022-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string>

#include "esp_log.h"
#include "FastLED.h"
#include "Arduino.h"
#include "light_handler.hpp"
#include "mqtt_client.hpp"

static const char *TAG = "app_main";

Light *test_light = new Light(3);
LightHandler *light_handler = new LightHandler({{"test_light", test_light}});

void message_handler(std::string msg) {
    ESP_LOGI(TAG, "Handle message: %s", msg.c_str());
}

extern "C" void app_main(void)
{
    initArduino();

    FastLED.addLeds<WS2811, 16, RGB>(&test_light->leds[0], test_light->leds.size());

    MQTTClient::init(message_handler);
}
