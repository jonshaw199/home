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

enum EffectAction {
ADD_EFFECTS,
UPDATE_EFFECTS,
DELETE_EFFECTS
};

Light test_light = Light(3);
LightHandler light_handler = LightHandler({{"test_light", test_light}});

void handle_base_msg(std::string msg) {
    ESP_LOGI(TAG, "Stub handle_base_msg");
}

void add_effects(cJSON *json) {
    const cJSON *message_json = NULL;
    const cJSON *effects_json = NULL;
    const cJSON *effect_json = NULL;

    message_json = cJSON_GetObjectItem(json, "message");
    effects_json = cJSON_GetObjectItem(message_json, "effects");
    cJSON_ArrayForEach(effect_json, effects_json) {
        Effect effect;
        cJSON *type_json = NULL;
        cJSON *id_json = NULL;
        cJSON *light_id_json = NULL;
        cJSON *start_time_json = NULL;
        cJSON *duration_json = NULL;

        type_json = cJSON_GetObjectItem(effect_json, "type");
        if (cJSON_IsNumber(type_json)) effect.set_type((EffectType) type_json->valueint);
        id_json = cJSON_GetObjectItem(effect_json, "id");
        if (cJSON_IsString(id_json)) effect.set_id(id_json->valuestring);
        start_time_json = cJSON_GetObjectItem(effect_json, "start_time");
        if (cJSON_IsNumber(start_time_json)) effect.set_start_time((int64_t) start_time_json->valuedouble);
        duration_json = cJSON_GetObjectItem(effect_json, "duration");
        if (cJSON_IsNumber(duration_json)) effect.set_duration((int64_t) duration_json->valuedouble);

        light_id_json = cJSON_GetObjectItem(effect_json, "light_id");
        std::string light_id = cJSON_IsString(light_id_json) ? light_id_json->valuestring : "";

        light_handler.add_effect(effect, light_id);
    }
}

void delete_effects(cJSON *json) {
    cJSON *msg_json = NULL;
    cJSON *action_json = NULL;
    cJSON *effects_json = NULL;
    cJSON *effect_json = NULL;

    msg_json = cJSON_GetObjectItem(json, "message");
    action_json = cJSON_GetObjectItem(msg_json, "action");
    effects_json = cJSON_GetObjectItem(msg_json, "effects");

    if (!effects_json) light_handler.delete_effect();

    cJSON_ArrayForEach(effect_json, effects_json) {
        cJSON *id_json = NULL;
        cJSON *light_id_json = NULL;

        id_json = cJSON_GetObjectItem(effect_json, "id");
        std::string id = cJSON_IsString(id_json) ? id_json->valuestring : "";
        light_id_json = cJSON_GetObjectItem(effect_json, "light_id");
        std::string light_id = cJSON_IsString(light_id_json) ? light_id_json->valuestring : "";

        light_handler.delete_effect(id, light_id);
    }
}

void handle_effect_msg(std::string msg) {
    cJSON *json = cJSON_Parse(msg.c_str());

    if (json) {
        cJSON *msg_json = NULL;
        cJSON *action_json = NULL;

        msg_json = cJSON_GetObjectItem(json, "message");
        action_json = cJSON_GetObjectItem(msg_json, "action");
        if (cJSON_IsNumber(action_json)) {
            EffectAction action = (EffectAction) action_json->valueint;
            switch (action) {
                case ADD_EFFECTS:
                    add_effects(json);
                    break;
                case DELETE_EFFECTS:
                    delete_effects(json);
                    break;
                default:
                    ESP_LOGW(TAG, "Unhandled action %d", action);
            }
        } else {
            ESP_LOGW(TAG, "Invalid action");
        }
    } else {
        ESP_LOGW(TAG, "Error parsing json");
    }

    cJSON_Delete(json);
}

std::map<std::string, message_handler> message_handlers{
{"light/test_id", handle_base_msg},
{"light/test_id/effect", handle_effect_msg}
};

void receive_message(std::string topic, std::string msg) {
    ESP_LOGI(TAG, "Handle message; topic: %s; message: %s", topic.c_str(), msg.c_str());
    auto found = message_handlers.find(topic);
    if (found == message_handlers.end()) {
        ESP_LOGW(TAG, "Handler doesnt exist for topic: %s", topic.c_str());
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
