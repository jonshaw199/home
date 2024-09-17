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
#include "mqtt_utils.hpp"
#include "nvs_manager.h"
#include "config_manager.h"
#include "KY015.hpp"

#define KY015_GPIO_PIN GPIO_NUM_8 // Use the appropriate GPIO pin connected to the KY-015 data pin

static const char *TAG = "main";

Topics topics = MqttUtils::get_topics(GROUP_ENVIRONMENTAL, CONFIG_DEVICE_ID);
std::string status_action = MqttUtils::get_action_str(ACTION_ENVIRONMENTAL_STATUS);

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
std::mutex sensor_state_mutex;
KY015::Data sensor_state = {0.0, 0.0, false};

KY015 sensor(KY015_GPIO_PIN); // TODO: pin

KY015::Data get_sensor_state() {
    const std::lock_guard<std::mutex> lock(sensor_state_mutex);
    return sensor_state;
}

void set_sensor_state(KY015::Data data) {
    const std::lock_guard<std::mutex> lock(sensor_state_mutex);
    sensor_state = data;
}

cJSON* build_json(float temp, float humidity) {
    // Build the JSON message using cJSON
    cJSON *root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "src", config_manager.get("DEVICE_ID").c_str());
    cJSON_AddStringToObject(root, "dest", topics.device_status_publish_topic.c_str());
    cJSON_AddStringToObject(root, "action", status_action.c_str());

    cJSON *body = cJSON_CreateObject();
    cJSON_AddNumberToObject(body, "temperature_c", temp);
    cJSON_AddNumberToObject(body, "humidity", humidity);
    cJSON_AddItemToObject(root, "body", body);

    return root;
}

void publish_status() {
    KY015::Data data = get_sensor_state();
    if (data.success) {
        if (mqtt_client) {
            cJSON *json = build_json(data.temperature, data.humidity);
            char *json_str = cJSON_Print(json);
            mqtt_client->publish(topics.device_status_publish_topic, json_str);
            cJSON_Delete(json);
            free(json_str);
        } else {
            ESP_LOGW(TAG, "MQTT is not initialized; not publishing");
        }
    } else {
        ESP_LOGW(TAG, "Sensor failure; not publishing");
    }
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
            ESP_LOGI(TAG, "Received MQTT data: %s", data.c_str());
        };

        auto subscribe = [&handle_msg]()
        {   
            mqtt_client->subscribe(topics.root_command_subscribe_topic.c_str(), handle_msg);
            mqtt_client->subscribe(topics.group_command_subscribe_topic.c_str(), handle_msg);
            mqtt_client->subscribe(topics.device_command_subscribe_topic.c_str(), handle_msg);
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
        KY015::Data data = sensor.read();
        if (data.success) {
            ESP_LOGD(TAG, "Temperature: %.1f C, Humidity: %.1f %%", data.temperature, data.humidity);
        } else {
            ESP_LOGD(TAG, "Failed to read sensor data.");
        }
        set_sensor_state(data);

        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// Function to update the display, etc.
void m5atom_task(void *pvParameter)
{
    ESP_LOGI(TAG, "M5Atom task started");

    while (true) {
        {
            KY015::Data data = get_sensor_state();

            // Display the temperature and humidity
            AtomS3.Display.clear();
            AtomS3.Display.setCursor(0, 0);
            AtomS3.Display.printf("Temp: %.2f C\n", data.temperature);
            AtomS3.Display.printf("Humidity: %.2f %%\n", data.humidity);
            AtomS3.update();
        }

        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// Function to publish status updates on a regular interval
void reporting_task(void *pvParameter)
{
    ESP_LOGI(TAG, "M5Atom task started");

    while (1) {
        publish_status();

        vTaskDelay(pdMS_TO_TICKS(10000));
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

    xTaskCreate(wifi_task, "wifi_task", 4096, nullptr, 4, nullptr);
    xTaskCreate(mqtt_task, "mqtt_task", 4096, nullptr, 5, &mqtt_task_handle);
    xTaskCreate(m5atom_task, "m5atom_task", 4096, nullptr, 6, nullptr);
    xTaskCreate(temp_humidity_task, "temp_humidity_task", 4096, nullptr, 5, nullptr);
    xTaskCreate(reporting_task, "reporting_task", 4096, nullptr, 5, nullptr);
}
