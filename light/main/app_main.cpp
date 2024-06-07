/*
 * SPDX-FileCopyrightText: 2022-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <string>
#include <map>

#include "cJSON.h"
#include "esp_log.h"
#include "FastLED.h"
#include "Arduino.h"
#include "light_handler.hpp"
#include "mqtt_client.hpp"

static const char *TAG = "app_main";

typedef void (*message_handler)(std::string msg);

Light test_light = Light(3);
LightHandler light_handler = LightHandler({{"test_light", test_light}});

void handle_base_msg(std::string msg) {}

void handle_effect_msg(std::string msg) {
    cJSON *json = cJSON_Parse(msg.c_str());
    if (json) {
        const cJSON *message = NULL;
        const cJSON *effect = NULL;
        const cJSON *type = NULL;
        message = cJSON_GetObjectItemCaseSensitive(json, "message");
        effect = cJSON_GetObjectItemCaseSensitive(message, "effect");
        type = cJSON_GetObjectItemCaseSensitive(effect, "type");
        if (cJSON_IsNumber(type)) {
            Effect effect = Effect((EffectType)type->valueint);
            light_handler.add_effect(effect);
        }
    } else {
        ESP_LOGW(TAG, "Error parsing json");
    }
}

std::map<std::string, message_handler> message_handlers{
{"light/test_id", handle_base_msg},
{"light/test_id/effect", handle_effect_msg}
};

void receive_message(std::string topic, std::string msg) {
    ESP_LOGI(TAG, "Handle message; topic: %s; message: %s", topic.c_str(), msg.c_str());
    auto found = message_handlers.find(topic);
    if (found == message_handlers.end()) {
        ESP_LOGI(TAG, "Handler doesnt exist for topic: %s", topic.c_str());
    } else {
        found->second(msg);
    }
}

extern "C" void app_main(void)
{
    initArduino();

    FastLED.addLeds<WS2811, 16, RGB>(&test_light.leds[0], test_light.leds.size());
    light_handler.init();

    topic_vector topics;
    for (auto const& entry: message_handlers) topics.push_back(entry.first);
    MQTTClient::init(topics, receive_message);
}
