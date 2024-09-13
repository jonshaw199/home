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
#include "esp_timer.h"
#include "ntp_client.h"

static const char *TAG = "main";

// Task handles
TaskHandle_t mqtt_task_handle = nullptr;

// Semaphore to communicate Wi-Fi connection status
SemaphoreHandle_t wifi_connected_semaphore;

// Initialize ConfigManager
ConfigManager config_manager;

// Initialize NTPClient
NTPClient ntp_client;

// Delayed initialization for these
WiFiConnector *wifi_connector;
MqttClient *mqtt_client;

struct DeviceStatus
{
    float cpu_usage = -1.0;
    float cpu_temperature = -1.0;
    float memory_usage = -1.0;
    float disk_usage = -1.0;
    int network_sent = -1;
    int network_received = -1;
    int64_t first_received_at = -1;   
};

struct DeviceStatusMessage
{
    std::string src = "";
    std::string dest = "";
    std::string action = "";
    DeviceStatus body;
};

typedef std::map<std::string, DeviceStatusMessage> status_message_map_t;

// Map device ID to last status message
status_message_map_t status_message_map;
std::mutex status_message_map_mutex; // Protects status_message_map

int page_idx = 0;
std::mutex page_idx_mutex;

void handle_device_status_message(DeviceStatusMessage msg)
{
    const std::lock_guard<std::mutex> lock(status_message_map_mutex);
    if (!status_message_map.contains(msg.src))
    {
        msg.first_received_at = esp_timer_get_time();
    }
    status_message_map[msg.src] = msg;
}

DeviceStatusMessage parse_device_status_message(const std::string &json_str)
{
    DeviceStatusMessage msg;
    cJSON *root = cJSON_Parse(json_str.c_str());
    if (!root)
        return msg; // Return default if parsing fails

    // Helper lambdas to extract data
    auto get_string = [&](cJSON *node, const char *key) -> std::string
    {
        cJSON *item = cJSON_GetObjectItem(node, key);
        return (item && cJSON_IsString(item)) ? item->valuestring : "";
    };

    auto get_float = [&](cJSON *node, const char *key) -> float
    {
        cJSON *item = cJSON_GetObjectItem(node, key);
        return (item && cJSON_IsNumber(item)) ? static_cast<float>(item->valuedouble) : -1.0;
    };

    auto get_int = [&](cJSON *node, const char *key) -> int
    {
        cJSON *item = cJSON_GetObjectItem(node, key);
        return (item && cJSON_IsNumber(item)) ? item->valueint : -1;
    };

    // Parse top-level fields
    msg.src = get_string(root, "src");
    msg.dest = get_string(root, "dest");
    msg.action = get_string(root, "action");

    // Parse the "body" object
    cJSON *body = cJSON_GetObjectItem(root, "body");
    if (body && cJSON_IsObject(body))
    {
        msg.body.cpu_usage = get_float(body, "cpu_usage");
        msg.body.cpu_temperature = get_float(body, "cpu_temperature");
        msg.body.memory_usage = get_float(body, "memory_usage");
        msg.body.disk_usage = get_float(body, "disk_usage");
        msg.body.network_sent = get_int(body, "network_sent");
        msg.body.network_received = get_int(body, "network_received");
        // Optionally set first_received_at if the JSON contains a timestamp
    }

    cJSON_Delete(root);
    return msg;
}


// Function to initialize MQTT
void mqtt_task(void *pvParameter)
{
    ESP_LOGI(TAG, "MQTT Task started");

    // Wait for the semaphore indicating Wi-Fi connection
    if (xSemaphoreTake(wifi_connected_semaphore, portMAX_DELAY) == pdTRUE)
    {
        ESP_LOGI(TAG, "Connected to Wi-Fi. Initializing MQTT...");

        std::string broker_host = config_manager.get("MQTT_BROKER");

        auto handle_msg = [](const std::string &data)
        {
            ESP_LOGI(TAG, "Received data on topic devices/+/device_status: %s", data.c_str());
            DeviceStatusMessage msg = parse_device_status_message(data);
            handle_device_status_message(msg);
        };

        auto subscribe = [&handle_msg]()
        {
            mqtt_client->subscribe("+/announce_status", handle_msg);
        };

        auto onConnect = [&subscribe]()
        {
            subscribe();
        };

        mqtt_client = new MqttClient(broker_host, onConnect);
    }
    else
    {
        ESP_LOGE(TAG, "Failed to receive semaphore. MQTT initialization aborted.");
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
        xSemaphoreGive(wifi_connected_semaphore); // Signal that Wi-Fi is connected
    };

    // Initialize Wi-Fi with callback
    wifi_connector = new WiFiConnector(ssid.c_str(), password.c_str(), onConnect);
    wifi_connector->connect();
    vTaskDelete(nullptr);
}

// Function to get value at a specific index by sorting
DeviceStatusMessage get_value_at_index(const std::map<std::string, DeviceStatusMessage> &m, int i)
{
    // Step 1: Use a multimap to sort by `first_received_at`
    std::multimap<long, DeviceStatusMessage> sorted_map;
    for (const auto &pair : m)
    {
        sorted_map.emplace(pair.second.body.first_received_at, pair.second);
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

void draw_home(M5Canvas &canvas, int num_devices)
{
    // Image
    const char *png_file = "/fallout boy.png";
    if (SPIFFS.exists(png_file))
    {
        canvas.drawPngFile(SPIFFS, png_file, 20, 55);
    }
    else
    {
        ESP_LOGE("PNG", "PNG file not found");
    }

    int32_t x = 110;

    // Time
    canvas.drawString(ntp_client.get_time_str("%H:%M:%S").c_str(), x, 60);
    // Date
    canvas.drawString(ntp_client.get_time_str("%Y-%m-%d").c_str(), x, 80);

    // # Devices
    canvas.drawString(std::string("Devices: ").append(std::to_string(num_devices)).c_str(), x, 110);
    // # Alerts
    canvas.drawString("Alerts: 0", x, 130); // TODO
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
    canvas.drawString("Name: Office PC", 50, 43);
    canvas.drawString(
        std::string("ID: ")
            .append(msg.src)
            .c_str(),
        50,
        60);
    canvas.drawString(
        std::string("CPU Usage: ").append(float_to_str(msg.body.cpu_usage, "%")).c_str(),
        50,
        77);
    canvas.drawString(
        std::string("CPU Temp: ").append(float_to_str(msg.body.cpu_temperature, "C")).c_str(),
        50,
        94);
    canvas.drawString(
        std::string("Mem Usage: ")
            .append(float_to_str(msg.body.memory_usage, "%"))
            .c_str(),
        50,
        111);
    canvas.drawString(
        std::string("Disk Usage: ")
            .append(float_to_str(msg.body.disk_usage, "%"))
            .c_str(),
        50,
        128);
    canvas.drawString(
        std::string("Upload: ")
            .append(float_to_str(msg.body.network_sent, "B"))
            .c_str(),
        50,
        145);
    canvas.drawString(
        std::string("Download: ")
            .append(float_to_str(msg.body.network_received, "B"))
            .c_str(),
        50,
        162);
    canvas.drawString("Alerts: 3", 50, 179); // TODO
}

void draw(M5Canvas &canvas)
{
    page_idx_mutex.lock();
    status_message_map_mutex.lock();
    if (page_idx)
    {
        DeviceStatusMessage msg = get_value_at_index(status_message_map, page_idx - 1);
        page_idx_mutex.unlock();
        status_message_map_mutex.unlock();
        draw_status(canvas, msg);
    }
    else
    {
        page_idx_mutex.unlock();
        int num_devices = status_message_map.size();
        status_message_map_mutex.unlock();
        draw_home(canvas, num_devices);
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

// Function to set system time using sntp
void ntp_task(void *pvParameter)
{
    ESP_LOGI(TAG, "NTP task started");

    // TODO: handle timezone
    ntp_client.begin();

    vTaskDelete(nullptr);
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

    // Create a semaphore to communicate Wi-Fi connection status
    wifi_connected_semaphore = xSemaphoreCreateBinary();

    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    xTaskCreate(display_task, "display_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(m5dial_task, "m5dial_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(ntp_task, "ntp_task", 4096, nullptr, 5, nullptr);
}
