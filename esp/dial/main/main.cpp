#include <string>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include "wifi_connector.h"
#include "mqtt_client.hpp"
#include "nvs_manager.h"
#include "config_manager.h"
#include "M5Dial.h"

static const char *TAG = "main";

// Task handles
TaskHandle_t mqtt_task_handle = nullptr;

// Queue to communicate Wi-Fi connection status
QueueHandle_t wifi_connected_queue;

// Initialize ConfigManager
ConfigManager config_manager;

// Function to initialize MQTT
void mqtt_task(void *pvParameter) {
    ESP_LOGI(TAG, "MQTT Task started");

    // Wait for Wi-Fi connection event
    bool wifi_connected;
    if (xQueueReceive(wifi_connected_queue, &wifi_connected, portMAX_DELAY)) {
        if (wifi_connected) {
            ESP_LOGI(TAG, "Connected to Wi-Fi. Initializing MQTT...");

            std::string broker_host = config_manager.get("MQTT_BROKER");
            MqttClient mqtt_client(broker_host);
            mqtt_client.subscribe("#", [](const std::string& data) {
                ESP_LOGI(TAG, "Received data on topic #: %s", data.c_str());
            });

            // Keep the MQTT task alive
            while (1) {
                vTaskDelay(pdMS_TO_TICKS(100));
            }
        } else {
            ESP_LOGE(TAG, "Failed to connect to Wi-Fi. MQTT initialization aborted.");
            vTaskDelete(nullptr);
        }
    }
    vTaskDelete(nullptr);
}

// Function to initialize Wi-Fi and notify MQTT task
void wifi_task(void *pvParameter) {
    ESP_LOGI(TAG, "Wi-Fi Task started");

    // Get Wi-Fi credentials from ConfigManager
    std::string ssid = config_manager.get("WIFI_SSID");
    std::string password = config_manager.get("WIFI_PASSWORD");

    // Define a callback function to notify MQTT task after Wi-Fi connects
    auto onConnect = []() {
        ESP_LOGI(TAG, "Connected to Wi-Fi!");
        bool wifi_connected = true;
        xQueueSend(wifi_connected_queue, &wifi_connected, portMAX_DELAY);
    };

    // Initialize Wi-Fi with callback
    WiFiConnector wifi(ssid.c_str(), password.c_str(), onConnect);
    wifi.connect();

    // Keep the Wi-Fi task alive
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void draw_function(LovyanGFX* gfx) {
    int x      = rand() % gfx->width();
    int y      = rand() % gfx->height();
    int r      = (gfx->width() >> 4) + 2;
    uint16_t c = rand();
    gfx->fillRect(x - r, y - r, r * 2, r * 2, c);
}

// Function to update display
void display_task(void *pvParameter) {
    ESP_LOGI(TAG, "Display task started");

    while (1) {
        // Draw
        int x      = rand() % M5Dial.Display.width();
        int y      = rand() % M5Dial.Display.height();
        int r      = (M5Dial.Display.width() >> 4) + 2;
        uint16_t c = rand();
        M5Dial.Display.fillCircle(x, y, r, c);
        draw_function(&M5Dial.Display);
        // Sleep?
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void init_config() {
    // Get Wi-Fi credentials from ConfigManager
    std::string ssid = config_manager.get("WIFI_SSID");
    std::string password = config_manager.get("WIFI_PASSWORD");
    std::string device_id = config_manager.get("DEVICE_ID");
    std::string mqtt_broker_host = config_manager.get("MQTT_BROKER");

    // Check if Wi-Fi credentials are set; if not, use default values
    if (ssid.empty()) {
        ssid = CONFIG_WIFI_SSID;
        config_manager.set("WIFI_SSID", ssid);
    }
    if (password.empty()) {
        password = CONFIG_WIFI_PASSWORD;
        config_manager.set("WIFI_PASSWORD", password);
    }
    if (device_id.empty()) {
        device_id = CONFIG_DEVICE_ID;
        config_manager.set("DEVICE_ID", device_id);
    }
    if (mqtt_broker_host.empty()) {
        mqtt_broker_host = CONFIG_MQTT_BROKER;
        config_manager.set("MQTT_BROKER", mqtt_broker_host);
    }
}

extern "C" void app_main(void) {
    init_config();
  
    M5Dial.begin();

    // Create a queue to communicate Wi-Fi connection status
    wifi_connected_queue = xQueueCreate(1, sizeof(bool));

    if (wifi_connected_queue == nullptr) {
        ESP_LOGE(TAG, "Failed to create queue");
        return;
    }

    // Create Wi-Fi and MQTT tasks
    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    // TODO
    //xTaskCreate(display_task, "display_task", 4096, nullptr, 5, nullptr);

    // Ensure the MQTT task is created successfully
    if (mqtt_task_handle == nullptr) {
        ESP_LOGE(TAG, "Failed to create MQTT task");
    }
}
