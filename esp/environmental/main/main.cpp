#include <string>
#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <mutex>
#include "cJSON.h"

#include "M5AtomS3.h"
#include "wifi_connector.h"
#include "mqtt_client.hpp"
#include "nvs_manager.h"
#include "config_manager.h"
#include "KY015.hpp"

#define KY015_GPIO_PIN GPIO_NUM_8 // Use the appropriate GPIO pin connected to the KY-015 data pin

static const char *TAG = "main";
static const int UPDATE_INTERVAL_MS = 1000;

// Task handles
TaskHandle_t mqtt_task_handle = nullptr;

// Semaphore to communicate Wi-Fi connection status
SemaphoreHandle_t wifi_connected_semaphore;

// Initialize ConfigManager
ConfigManager config_manager;

// Delayed initialization for these
WiFiConnector *wifi_connector;
MqttClient *mqtt_client;

// Global variables to store temperature and humidity
float global_temperature = 0.0;
float global_humidity = 0.0;
std::mutex temp_humidity_mutex;  // Mutex for thread-safe access

KY015 sensor(KY015_GPIO_PIN); // TODO: pin

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
            ESP_LOGI(TAG, "Received MQTT data: %s", data.c_str());
        };

        auto subscribe = [&handle_msg]()
        {   
            mqtt_client->subscribe("command", handle_msg);
            mqtt_client->subscribe("environmentals/command", handle_msg);
            mqtt_client->subscribe(std::string("environmentals/").append(CONFIG_DEVICE_ID).append("/command").c_str(), handle_msg);
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

// Function to report temp and humitidy
void temp_humidity_task(void *pvParameter)
{
    ESP_LOGI(TAG, "Temp/humidity task started");

    while (true) {
        KY015::Data sensorData = sensor.read();
        if (sensorData.success) {
            ESP_LOGI(TAG, "Temperature: %.1f C, Humidity: %.1f %%", sensorData.temperature, sensorData.humidity);
        } else {
            ESP_LOGE(TAG, "Failed to read sensor data.");
        }

        vTaskDelay(pdMS_TO_TICKS(UPDATE_INTERVAL_MS));
    }
}

// Function to update the display, etc.
void m5atom_task(void *pvParameter)
{
    ESP_LOGI(TAG, "M5Atom task started");

    while (true) {
        {
            temp_humidity_mutex.lock();
            float temp = global_temperature;
            float humidity = global_humidity;
            temp_humidity_mutex.unlock();

            // Display the temperature and humidity
            AtomS3.Display.clear();
            AtomS3.Display.setCursor(0, 0);
            AtomS3.Display.printf("Temp: %.2f C\n", temp);
            AtomS3.Display.printf("Humidity: %.2f %%\n", humidity);
            AtomS3.update();
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
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

extern "C" void app_main(void)
{
    init_config();

    auto cfg = M5.config();
    AtomS3.begin(cfg);

    // Create a semaphore to communicate Wi-Fi connection status
    wifi_connected_semaphore = xSemaphoreCreateBinary();

    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    xTaskCreate(m5atom_task, "m5atom_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(temp_humidity_task, "temp_humidity_task", 4096, nullptr, 5, nullptr);
}
