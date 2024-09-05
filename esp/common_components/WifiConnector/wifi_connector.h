#ifndef WIFI_CONNECTOR_H
#define WIFI_CONNECTOR_H

#include <functional>
#include "esp_event.h"

class WiFiConnector {
public:
    // Constructor with callback for Wi-Fi connection
    WiFiConnector(const char* ssid, const char* password, std::function<void()> onConnectCallback);

    ~WiFiConnector();

    void connect();
    bool isConnected();

private:
    static void wifi_event_handler(void* arg, esp_event_base_t event_base, int32_t event_id, void* event_data);

    const char* ssid;
    const char* password;
    bool connected;
    std::function<void()> onConnectCallback;

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
};

#endif // WIFI_CONNECTOR_H
