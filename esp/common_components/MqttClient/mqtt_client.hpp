#ifndef MQTT_CLIENT_HPP
#define MQTT_CLIENT_HPP

#include <string>
#include <functional>
#include <map>
#include <vector>
#include <esp_event.h>
#include <mqtt_client.h>

class MqttClient
{
public:
    MqttClient(const std::string &broker_url, std::function<void()> onConnectCallback);
    ~MqttClient();

    void subscribe(const std::string &topic, std::function<void(const std::string &)> callback);

private:
    static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data);
    bool topic_matches(const std::string &topic, const std::string &pattern);
    std::function<void()> onConnectCallback;

    esp_mqtt_client_handle_t client;
    std::map<std::string, std::function<void(const std::string &)>> topic_callbacks;
    std::vector<std::string> wildcard_topics;
};

#endif // MQTT_CLIENT_HPP
