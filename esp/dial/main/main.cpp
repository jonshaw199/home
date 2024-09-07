#include <string>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include "wifi_connector.h"
#include "mqtt_client.hpp"
#include "nvs_manager.h"
#include "config_manager.h"
// Must come before M5Dial.h
#include "SPIFFS.h" // Needed for drawing images using M5GFX
// Must come after SPIFFS.h
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

// Delayed initialization for these
WiFiConnector *wifi_connector;
MqttClient *mqtt_client;

struct DeviceStatusMessage
{
    std::string msg_domain = "";
    int device_id = -1; // -1 represents null
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

void handle_device_status_message(DeviceStatusMessage msg)
{
    const std::lock_guard<std::mutex> lock(status_message_map_mutex);
    if (!status_message_map.contains(msg.device_id))
    {
        msg.first_received_at = esp_timer_get_time();
    }
    status_message_map[msg.device_id] = msg;
}

DeviceStatusMessage parse_device_status_message(const std::string &json_str)
{
    DeviceStatusMessage msg;
    cJSON *root = cJSON_Parse(json_str.c_str());
    if (!root)
        return msg; // Return default if parsing fails

    auto get_string = [&](const char *key) -> std::string
    {
        cJSON *item = cJSON_GetObjectItem(root, key);
        return (item && cJSON_IsString(item)) ? item->valuestring : "";
    };

    auto get_float = [&](const char *key) -> float
    {
        cJSON *item = cJSON_GetObjectItem(root, key);
        return (item && cJSON_IsNumber(item)) ? static_cast<float>(item->valuedouble) : -1.0;
    };

    auto get_int = [&](const char *key) -> int
    {
        cJSON *item = cJSON_GetObjectItem(root, key);
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
void mqtt_task(void *pvParameter)
{
    ESP_LOGI(TAG, "MQTT Task started");

    // Wait for Wi-Fi connection event
    bool wifi_connected;
    if (xQueueReceive(wifi_connected_queue, &wifi_connected, portMAX_DELAY))
    {
        if (wifi_connected)
        {
            ESP_LOGI(TAG, "Connected to Wi-Fi. Initializing MQTT...");

            std::string broker_host = config_manager.get("MQTT_BROKER");
            mqtt_client = new MqttClient(broker_host);
            mqtt_client->subscribe("devices/+/device_status", [](const std::string &data)
                                   {
                ESP_LOGI(TAG, "Received data on topic devices/+/device_status: %s", data.c_str());
                DeviceStatusMessage msg = parse_device_status_message(data);
                handle_device_status_message(msg); });
        }
        else
        {
            ESP_LOGE(TAG, "Failed to connect to Wi-Fi. MQTT initialization aborted.");
        }
    }
    vTaskDelete(nullptr);
}

// Function to initialize Wi-Fi and notify MQTT task
void wifi_task(void *pvParameter)
{
    ESP_LOGI(TAG, "Wi-Fi Task started");

    // Get Wi-Fi credentials from ConfigManager
    std::string ssid = config_manager.get("WIFI_SSID");
    std::string password = config_manager.get("WIFI_PASSWORD");

    // Define a callback function to notify MQTT task after Wi-Fi connects
    auto onConnect = []()
    {
        ESP_LOGI(TAG, "Connected to Wi-Fi!");
        bool wifi_connected = true;
        xQueueSend(wifi_connected_queue, &wifi_connected, portMAX_DELAY);
    };

    // Initialize Wi-Fi with callback
    wifi_connector = new WiFiConnector(ssid.c_str(), password.c_str(), onConnect);
    wifi_connector->connect();
    vTaskDelete(nullptr);
}

// Function to get value at a specific index by sorting
DeviceStatusMessage get_value_at_index(const std::map<int, DeviceStatusMessage> &m, int i)
{
    // Step 1: Use a multimap to sort by `first_received_at`
    std::multimap<long, DeviceStatusMessage> sorted_map;
    for (const auto &pair : m)
    {
        sorted_map.emplace(pair.second.first_received_at, pair.second);
    }

    // Step 2: Iterate over the sorted map and get the value at index `i`
    auto it = sorted_map.begin();
    std::advance(it, i); // Move the iterator to the `i`-th element

    if (it != sorted_map.end())
    {
        return it->second; // Return a copy of the value
    }

    return DeviceStatusMessage(); // Return default if index is out of bounds
}

void draw_home(M5Canvas &canvas)
{
    const char *png_file = "/fallout boy.png";
    if (SPIFFS.exists(png_file))
    {
        canvas.drawPngFile(SPIFFS, png_file, 50, 50);
    }
    else
    {
        ESP_LOGE("PNG", "PNG file not found");
    }
}

std::string float_to_str(float num, std::string postfix = "")
{
    if (num < 0.0f)
    {
        return "--";
    }
    else
    {
        return std::to_string(static_cast<int>(num)).append(postfix);
    }
}

void draw_status(M5Canvas &canvas, DeviceStatusMessage &msg)
{
    canvas.drawString("Name: Test Name", 50, 43);
    canvas.drawString(
        std::string("ID: ")
            .append(std::to_string(msg.device_id))
            .c_str(),
        50,
        60);
    canvas.drawString(
        std::string("CPU Usage: ").append(float_to_str(msg.cpu_usage, "%")).c_str(),
        50,
        77);
    canvas.drawString(
        std::string("CPU Temp: ").append(float_to_str(msg.cpu_temperature, "C")).c_str(),
        50,
        94);
    canvas.drawString(
        std::string("Mem Usage: ")
            .append(float_to_str(msg.memory_usage, "%"))
            .c_str(),
        50,
        111);
    canvas.drawString(
        std::string("Disk Usage: ")
            .append(float_to_str(msg.disk_usage, "%"))
            .c_str(),
        50,
        128);
    canvas.drawString(
        std::string("Upload: ")
            .append(float_to_str(msg.network_sent, "B"))
            .c_str(),
        50,
        145);
    canvas.drawString(
        std::string("Download: ")
            .append(float_to_str(msg.network_received, "B"))
            .c_str(),
        50,
        162);
    canvas.drawString("Alerts: 3", 50, 179); // TODO
}

void draw(M5Canvas &canvas)
{
    page_idx_mutex.lock();
    if (page_idx)
    {
        status_message_map_mutex.lock();
        DeviceStatusMessage msg = get_value_at_index(status_message_map, page_idx - 1);
        page_idx_mutex.unlock();
        status_message_map_mutex.unlock();
        draw_status(canvas, msg);
    }
    else
    {
        page_idx_mutex.unlock();
        draw_home(canvas);
    }
}

// Function to update display
void display_task(void *pvParameter)
{
    ESP_LOGI(TAG, "Display task started");

    M5Dial.Display.fillScreen(TFT_BLACK);
    M5Canvas canvas(&M5Dial.Display);
    canvas.setFont(&fonts::FreeMono9pt7b);
    canvas.setTextSize(0.9f);
    canvas.setTextColor(GREEN);

    while (1)
    {
        canvas.createSprite(M5Dial.Display.width(), M5Dial.Display.height());
        draw(canvas);

        M5Dial.Display.startWrite();
        canvas.pushSprite(&M5Dial.Display, 0, 0);
        M5Dial.Display.endWrite();

        vTaskDelay(pdMS_TO_TICKS(75));
    }
}

void update_page_idx(int delta)
{
    const std::lock_guard<std::mutex> page_idx_mutex_lock(page_idx_mutex);
    const std::lock_guard<std::mutex> status_message_map_mutex_lock(status_message_map_mutex);
    if (delta > 0)
    {
        int num_devices = status_message_map.size();
        int max_idx = num_devices; // This assumes there is a home screen
        page_idx = min(page_idx + delta, max_idx);
    }
    else
    {
        page_idx = max(page_idx + delta, 0);
    }
}

// Function to handle user input from encoder, buttons, etc...
void m5dial_task(void *pvParameter)
{
    ESP_LOGI(TAG, "M5Dial task started");

    long oldPosition = 0;

    while (1)
    {
        M5Dial.update();

        // Handle encoder
        long newPosition = M5Dial.Encoder.read();
        if (newPosition != oldPosition)
        {
            ESP_LOGI(TAG, "New position: %ld", newPosition);
            M5Dial.Speaker.tone(8000, 7);

            int delta = newPosition - oldPosition;
            update_page_idx(delta);

            oldPosition = newPosition;
        }

        // Handle buttons
        // if (M5Dial.BtnA.wasPressed())
        // {
        //     M5Dial.Encoder.readAndReset();
        // }
        // if (M5Dial.BtnA.pressedFor(5000))
        // {
        //     M5Dial.Encoder.write(100);
        // }

        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

void init_config()
{
    // Get Wi-Fi credentials from ConfigManager
    std::string ssid = config_manager.get("WIFI_SSID");
    std::string password = config_manager.get("WIFI_PASSWORD");
    std::string device_id = config_manager.get("DEVICE_ID");
    std::string mqtt_broker_host = config_manager.get("MQTT_BROKER");

    // Check if Wi-Fi credentials are set; if not, use default values
    if (ssid.empty())
    {
        ssid = CONFIG_WIFI_SSID;
        config_manager.set("WIFI_SSID", ssid);
    }
    if (password.empty())
    {
        password = CONFIG_WIFI_PASSWORD;
        config_manager.set("WIFI_PASSWORD", password);
    }
    if (device_id.empty())
    {
        device_id = CONFIG_DEVICE_ID;
        config_manager.set("DEVICE_ID", device_id);
    }
    if (mqtt_broker_host.empty())
    {
        mqtt_broker_host = CONFIG_MQTT_BROKER;
        config_manager.set("MQTT_BROKER", mqtt_broker_host);
    }
}

// Need to use arduino-esp32 SPIFFS since M5GFX is tightly coupled to it
void init_spiffs()
{
    if (!SPIFFS.begin(false, "/storage"))
    { // 'true' to format SPIFFS if mount fails
        ESP_LOGE("SPIFFS", "Failed to mount SPIFFS");
        return;
    }

    // Log memory information
    ESP_LOGI("SPIFFS", "Total bytes: %u, Used bytes: %u", SPIFFS.totalBytes(), SPIFFS.usedBytes());
}

extern "C" void app_main(void)
{
    init_config();

    init_spiffs();

    auto m5_cfg = M5.config();
    M5Dial.begin(m5_cfg, true, false);

    // Create a queue to communicate Wi-Fi connection status
    wifi_connected_queue = xQueueCreate(1, sizeof(bool));

    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    xTaskCreate(display_task, "display_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(m5dial_task, "m5dial_task", 4096, nullptr, 5, nullptr);
}
