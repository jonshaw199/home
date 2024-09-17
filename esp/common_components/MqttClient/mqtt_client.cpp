#include "mqtt_client.hpp"
#include <esp_log.h>
#include <algorithm>
#include <vector>
#include <string>
#include <cstring> // For strtok

static const char *TAG = "MqttUtils";

MqttClient::MqttClient(const std::string &broker_url, std::function<void()> onConnectCallback)
    : onConnectCallback(onConnectCallback)
{
    esp_mqtt_client_config_t mqtt_cfg = {};
    mqtt_cfg.broker.address.uri = broker_url.c_str();
    mqtt_cfg.session.protocol_ver = MQTT_PROTOCOL_V_5;

    // Initialize MQTT client
    client = esp_mqtt_client_init(&mqtt_cfg);

    // MQTT 5.0 specific connection properties
    esp_mqtt5_connection_property_config_t connect_property = {};
    connect_property.session_expiry_interval = 10;
    connect_property.maximum_packet_size = 1024;
    connect_property.receive_maximum = 65535;
    connect_property.topic_alias_maximum = 2;
    connect_property.request_resp_info = true;
    connect_property.will_delay_interval = 10;
    connect_property.payload_format_indicator = true;
    connect_property.message_expiry_interval = 10;

    // Set MQTT 5.0 connection properties
    esp_mqtt5_client_set_connect_property(client, &connect_property);

    esp_mqtt_client_register_event(client, MQTT_EVENT_CONNECTED, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_DISCONNECTED, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_SUBSCRIBED, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_UNSUBSCRIBED, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_PUBLISHED, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_DATA, &MqttClient::mqtt_event_handler, this);
    esp_mqtt_client_register_event(client, MQTT_EVENT_ERROR, &MqttClient::mqtt_event_handler, this);

    esp_mqtt_client_start(client);
}

MqttClient::~MqttClient()
{
    if (client)
    {
        esp_mqtt_client_stop(client);
        esp_mqtt_client_destroy(client);
        client = nullptr;
    }
}

void MqttClient::subscribe(const std::string &topic, std::function<void(const std::string &)> callback)
{
    topic_callbacks[topic] = callback;

    // If the topic has a wildcard, store it for pattern matching
    if (topic.find('#') != std::string::npos || topic.find('+') != std::string::npos)
    {
        wildcard_topics.push_back(topic);
    }

    esp_mqtt_client_subscribe(client, topic.c_str(), 0);
    ESP_LOGI(TAG, "Subscribed to topic: %s", topic.c_str());
}

void MqttClient::mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    MqttClient *self = static_cast<MqttClient *>(handler_args);
    esp_mqtt_event_handle_t event = static_cast<esp_mqtt_event_handle_t>(event_data);

    switch (event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT Connected");
        // Invoke the callback if it's set
        if (self->onConnectCallback)
        {
            self->onConnectCallback();
        }
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT Disconnected");
        break;
    case MQTT_EVENT_SUBSCRIBED:
        if (event->topic)
        {
            ESP_LOGI(TAG, "Subscription confirmed for topic: %s", event->topic);
        }
        else
        {
            ESP_LOGI(TAG, "Subscription confirmed (unknown topic)");
        }
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "Unsubscribed from topic");
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "Message published");
        break;
    case MQTT_EVENT_DATA:
    {
        std::string topic(event->topic, event->topic_len);
        std::string data(event->data, event->data_len);

        // Check for exact match first
        if (self->topic_callbacks.find(topic) != self->topic_callbacks.end())
        {
            self->topic_callbacks[topic](data);
        }
        else
        {
            // Check for wildcard matches
            for (const auto &wildcard_topic : self->wildcard_topics)
            {
                if (self->topic_matches(topic, wildcard_topic))
                {
                    self->topic_callbacks[wildcard_topic](data);
                }
                else
                {
                    ESP_LOGW(TAG, "No callback exists to handle MQTT_EVENT_DATA for topic: %s", topic.c_str());
                }
            }
        }
        break;
    }
    case MQTT_EVENT_ERROR:
        ESP_LOGE(TAG, "MQTT Error: %d", event->error_handle->error_type);
        break;
    default:
        ESP_LOGW(TAG, "Unhandled MQTT event id: %ld", event_id);
        break;
    }
}

// Helper function to split a string by a delimiter
std::vector<std::string> split(const std::string &str, char delimiter)
{
    std::vector<std::string> tokens;
    size_t start = 0;
    size_t end = str.find(delimiter);

    while (end != std::string::npos)
    {
        tokens.push_back(str.substr(start, end - start));
        start = end + 1;
        end = str.find(delimiter, start);
    }

    tokens.push_back(str.substr(start));
    return tokens;
}

// Helper function to check if a topic matches a wildcard pattern
bool MqttClient::topic_matches(const std::string &topic, const std::string &pattern)
{
    std::vector<std::string> topic_levels = split(topic, '/');
    std::vector<std::string> pattern_levels = split(pattern, '/');

    // If levels don't match in size and there's no wildcard '#', it's not a match
    if (pattern_levels.size() != topic_levels.size() && pattern_levels.back() != "#")
    {
        return false;
    }

    // Compare each level
    for (size_t i = 0; i < pattern_levels.size(); i++)
    {
        const std::string &pattern_level = pattern_levels[i];
        const std::string &topic_level = topic_levels[i];

        if (pattern_level == "#")
        {
            return true; // Matches anything after this point
        }
        else if (pattern_level == "+")
        {
            continue; // Matches exactly one level, so skip to next
        }
        else if (pattern_level != topic_level)
        {
            return false; // No match
        }
    }

    // If all levels matched, return true
    return true;
}

void MqttClient::publish(const std::string &topic, const std::string &message, int qos, bool retain)
{
    int msg_id = esp_mqtt_client_publish(client, topic.c_str(), message.c_str(), 0, qos, retain);

    if (msg_id != -1)
    {
        ESP_LOGI(TAG, "Message published to topic: %s, msg_id=%d", topic.c_str(), msg_id);
    }
    else
    {
        ESP_LOGE(TAG, "Failed to publish message to topic: %s", topic.c_str());
    }
}

