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
#include "config_utils.h"
#include "KY015.hpp"

#define KY015_GPIO_PIN GPIO_NUM_8 // Use the appropriate GPIO pin connected to the KY-015 data pin

static const char *TAG = "main";

Topics topics = MqttUtils::get_topics(GROUP_ENVIRONMENTAL, CONFIG_DEVICE_ID);
std::string status_action = MqttUtils::get_action_str(ACTION_ENVIRONMENTAL_STATUS);

// Task handles
TaskHandle_t mqtt_task_handle = nullptr;

// Semaphore to communicate Wi-Fi connection status
SemaphoreHandle_t wifi_connected_semaphore;

BaseConfig default_config = {
    CONFIG_DEVICE_ID, 
    CONFIG_WIFI_SSID, 
    CONFIG_WIFI_PASSWORD, 
    CONFIG_MQTT_BROKER
};
BaseConfig config = ConfigUtils::get_or_init_base_config(default_config);

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

cJSON* build_json(KY015::Data& sensor_data) {
    // Build the JSON message using cJSON
    cJSON *root = cJSON_CreateObject();
    cJSON_AddStringToObject(root, "src", config.device_id.c_str());
    cJSON_AddStringToObject(root, "dest", topics.device_status_publish_topic.c_str());
    cJSON_AddStringToObject(root, "action", status_action.c_str());

    cJSON *body = cJSON_CreateObject();
    cJSON_AddNumberToObject(body, "temperature_c", sensor_data.temperature);
    cJSON_AddNumberToObject(body, "humidity", sensor_data.humidity);
    cJSON_AddBoolToObject(body, "sensor_read_success", sensor_data.success);
    cJSON_AddItemToObject(root, "body", body);

    return root;
}

void publish_status() {
    ESP_LOGI(TAG, "Publishing status");
    KY015::Data data = get_sensor_state();
    if (mqtt_client) {
        cJSON *json = build_json(data);
        char *json_str = cJSON_Print(json);
        mqtt_client->publish(topics.device_status_publish_topic, json_str);
        // Important!
        cJSON_Delete(json);
        free(json_str);
    } else {
        ESP_LOGW(TAG, "MQTT is not initialized; not publishing status");
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

        std::string broker_host = config.mqtt_broker;

        auto handle_command = [](const std::string &data)
        {
            ESP_LOGI(TAG, "Received MQTT command: %s", data.c_str());
            cJSON* json = MqttUtils::parse_json_string(data);
            std::string action = MqttUtils::get_json_string_value(json, "action");
            if (
                action == MqttUtils::get_action_str(ACTION_ENVIRONMENTAL_REQUEST_STATUS)
                    || action == MqttUtils::get_action_str(ACTION_REQUEST_STATUS)
            ) {
                publish_status();
            } else {
                ESP_LOGI(TAG, "Skipping msg with action: %s", action.c_str());
            }
            // Important!
            cJSON_Delete(json);
        };

        auto subscribe = [&handle_command]()
        {   
            mqtt_client->subscribe(topics.root_command_subscribe_topic.c_str(), handle_command);
            mqtt_client->subscribe(topics.group_command_subscribe_topic.c_str(), handle_command);
            mqtt_client->subscribe(topics.device_command_subscribe_topic.c_str(), handle_command);
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
    std::string ssid = config.wifi_ssid;
    std::string password = config.wifi_pass;

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

void draw(M5Canvas &canvas, KY015::Data &data) {
    canvas.setFont(&fonts::FreeMono12pt7b);
    canvas.setTextColor(WHITE);
    canvas.drawString("Temp", 2, 2);

    canvas.setFont(&fonts::FreeMono24pt7b);
    canvas.setTextColor(GREEN);
    float temp_f = data.temperature * (9/5) + 32;
    std::string temp_str = float_to_str(temp_f, "F");
    canvas.drawString(temp_str.c_str(), 2, 22);

    canvas.setFont(&fonts::FreeMono12pt7b);
    canvas.setTextColor(WHITE);
    canvas.drawString("Humidity", 2, 66);

    canvas.setFont(&fonts::FreeMono24pt7b);
    canvas.setTextColor(GREEN);
    std::string hum_str = float_to_str(data.humidity, "%");
    canvas.drawString(hum_str.c_str(), 2, 86);
}

// Function to update the display, etc.
void m5atom_task(void *pvParameter)
{
    ESP_LOGI(TAG, "M5Atom task started");

    AtomS3.Display.fillScreen(TFT_BLACK);
    M5Canvas canvas(&AtomS3.Display);

    while (1) {
        AtomS3.update();

        KY015::Data data = get_sensor_state();

        if (data.success) {
            canvas.createSprite(AtomS3.Display.width(), AtomS3.Display.height());
            draw(canvas, data);
            AtomS3.Display.startWrite();
            canvas.pushSprite(&AtomS3.Display, 0, 0);
            AtomS3.Display.endWrite();
        }

        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

// Function to publish status updates on a regular interval
void reporting_task(void *pvParameter)
{
    ESP_LOGI(TAG, "Reporting task started");

    while (1) {
        publish_status();

        vTaskDelay(pdMS_TO_TICKS(10000));
    }
}

extern "C" void app_main(void)
{
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
