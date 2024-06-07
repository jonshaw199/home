/*
 * SPDX-FileCopyrightText: 2022-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include "FastLED.h"
#include "Arduino.h"
#include "light_handler.hpp"
#include "mqtt_client.hpp"

static const char *TAG = "app_main";

extern "C" void app_main(void)
{
    initArduino();

    Light *test = new Light(3);
    FastLED.addLeds<WS2811, 16, RGB>(&test->leds[0], test->leds.size());
    LightHandler({{"test", test}}).init();

    MQTTClient mqtt_client = MQTTClient();
    mqtt_client.init();
}
