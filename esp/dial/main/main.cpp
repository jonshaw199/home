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
#include <map>
#include "cJSON.h"
#include <mutex>
#include <vector>
#include <algorithm>
#include "esp_timer.h"

static const char *TAG = "main";

// Task handles
TaskHandle_t mqtt_task_handle = nullptr;

// Queue to communicate Wi-Fi connection status
QueueHandle_t wifi_connected_queue;

// Initialize ConfigManager
ConfigManager config_manager;

struct DeviceStatusMessage {
    std::string msg_domain = "";
    int device_id = -1;  // -1 represents null
    std::string msg_type = "";
    float cpu_usage = -1.0;  
    float cpu_temperature = -1.0;  
    float memory_usage = -1.0;  
    float disk_usage = -1.0;  
    int network_sent = -1;  
    int network_received = -1;
    int64_t first_received_at = -1;
};

// Map device ID to last status message
std::map<int, DeviceStatusMessage> status_message_map;
std::mutex status_message_map_mutex; // Protects status_message_map

int page_idx = 0;
std::mutex page_idx_mutex; 

void handle_device_status_message(DeviceStatusMessage msg) {
    const std::lock_guard<std::mutex> lock(status_message_map_mutex);
    if (!status_message_map.contains(msg.device_id)) {
        msg.first_received_at = esp_timer_get_time();
    }
    status_message_map[msg.device_id] = msg;
}

DeviceStatusMessage parse_device_status_message(const std::string& json_str) {
    DeviceStatusMessage msg;
    cJSON* root = cJSON_Parse(json_str.c_str());
    if (!root) return msg;  // Return default if parsing fails

    auto get_string = [&](const char* key) -> std::string {
        cJSON* item = cJSON_GetObjectItem(root, key);
        return (item && cJSON_IsString(item)) ? item->valuestring : "";
    };

    auto get_float = [&](const char* key) -> float {
        cJSON* item = cJSON_GetObjectItem(root, key);
        return (item && cJSON_IsNumber(item)) ? static_cast<float>(item->valuedouble) : -1.0;
    };

    auto get_int = [&](const char* key) -> int {
        cJSON* item = cJSON_GetObjectItem(root, key);
        return (item && cJSON_IsNumber(item)) ? item->valueint : -1;
    };

    msg.msg_domain = get_string("msg_domain");
    msg.device_id = get_int("device_id");
    msg.msg_type = get_string("msg_type");
    msg.cpu_usage = get_float("cpu_usage");
    msg.cpu_temperature = get_float("cpu_temperature");
    msg.memory_usage = get_float("memory_usage");
    msg.disk_usage = get_float("disk_usage");
    msg.network_sent = get_int("network_sent");
    msg.network_received = get_int("network_received");

    cJSON_Delete(root);
    return msg;
}

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
            mqtt_client.subscribe("devices/+/device_status", [](const std::string& data) {
                ESP_LOGI(TAG, "Received data on topic devices/+/device_status: %s", data.c_str());
                DeviceStatusMessage msg = parse_device_status_message(data);
                handle_device_status_message(msg);
            });

            // Keep the MQTT task alive
            while (1) {
                vTaskDelay(pdMS_TO_TICKS(100));
            }            ESP_LOGE(TAG, "Failed to connect to Wi-Fi. MQTT initialization aborted.");

        } else {
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

// Function to get value at a specific index by sorting
DeviceStatusMessage get_value_at_index(const std::map<int, DeviceStatusMessage>& m, int i) {
    // Step 1: Use a multimap to sort by `first_received_at`
    std::multimap<long, DeviceStatusMessage> sorted_map;
    for (const auto& pair : m) {
        sorted_map.emplace(pair.second.first_received_at, pair.second);
    }

    // Step 2: Iterate over the sorted map and get the value at index `i`
    auto it = sorted_map.begin();
    std::advance(it, i);  // Move the iterator to the `i`-th element
    
    if (it != sorted_map.end()) {
        return it->second;  // Return a copy of the value
    }
    
    return DeviceStatusMessage();  // Return default if index is out of bounds
}

void draw_home(M5Canvas& canvas) {
    canvas.drawString("Home", 100, 100);
}

void draw_searching(M5Canvas& canvas) {
    canvas.drawString("Searching", 100, 100);
}

void draw_status(M5Canvas& canvas, DeviceStatusMessage& msg) {
    canvas.drawString("Status", 100, 100);
}

void draw(M5Canvas& canvas) {
    const std::lock_guard<std::mutex> page_idx_mutex_lock(page_idx_mutex);
    const std::lock_guard<std::mutex> status_message_map_mutex_lock(status_message_map_mutex);
    if (status_message_map.size()) {
        if (!page_idx) {
            draw_home(canvas);
        } else if (page_idx <= status_message_map.size()) {
            DeviceStatusMessage msg = get_value_at_index(status_message_map, page_idx - 1);
            draw_status(canvas, msg);
        } else {
            draw_searching(canvas);
        }
    } else {
        draw_searching(canvas);
    }
}

// Function to update display
void display_task(void *pvParameter) {
    ESP_LOGI(TAG, "Display task started");

    M5Dial.Display.fillScreen(TFT_BLACK);
    M5Canvas canvas(&M5Dial.Display);
    canvas.setTextFont(&fonts::Orbitron_Light_32);
    canvas.setTextColor(GREEN);

    while (1) {
        canvas.createSprite(M5Dial.Display.width(), M5Dial.Display.height());
        draw(canvas);

        M5Dial.Display.startWrite();
        canvas.pushSprite(&M5Dial.Display, 0, 0);
        M5Dial.Display.endWrite();

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void update_page_idx(int delta) {
    const std::lock_guard<std::mutex> page_idx_mutex_lock(page_idx_mutex);
    const std::lock_guard<std::mutex> status_message_map_mutex_lock(status_message_map_mutex);
    if (delta > 0) {
        int num_devices = status_message_map.size();
        int max_idx = num_devices ? num_devices + 1 : 0;
        page_idx = min(page_idx + delta, max_idx);
    } else if (delta < 0) {
        page_idx = max(page_idx + delta, 0);
    }
}

void m5dial_task(void *pvParameter) {
    ESP_LOGI(TAG, "M5Dial task started");

    long oldPosition = 0;

    while (1) {
        M5Dial.update();

        // Handle encoder
        long newPosition = M5Dial.Encoder.read();
        if (newPosition != oldPosition) {
            ESP_LOGI(TAG, "New position: %ld", newPosition);
            M5Dial.Speaker.tone(8000, 7);

            int delta = newPosition - oldPosition;
            update_page_idx(delta);

            oldPosition = newPosition;
        }
        if (M5Dial.BtnA.wasPressed()) {
            M5Dial.Encoder.readAndReset();
        }
        if (M5Dial.BtnA.pressedFor(5000)) {
            M5Dial.Encoder.write(100);
        }

        vTaskDelay(pdMS_TO_TICKS(20));
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
  
    auto m5_cfg = M5.config();
    M5Dial.begin(m5_cfg, true, false);

    // Create a queue to communicate Wi-Fi connection status
    wifi_connected_queue = xQueueCreate(1, sizeof(bool));

    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    xTaskCreate(display_task, "display_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(m5dial_task, "m5dial_task", 4096, nullptr, 5, nullptr);
}
