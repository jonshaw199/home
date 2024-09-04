#include "config_manager.h"
#include <esp_log.h>

//static const char* TAG = "ConfigManager";
static const char* NVS_NS = "storage";

ConfigManager::ConfigManager() {
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    // Open NVS namespace
    err = nvs_open(NVS_NS, NVS_READWRITE, &nvs_handle);
    ESP_ERROR_CHECK(err);
}

ConfigManager::~ConfigManager() {
    if (nvs_handle) {
        nvs_close(nvs_handle);
    }
}

void ConfigManager::set(const std::string& key, const std::string& value) {
    esp_err_t err = nvs_set_str(nvs_handle, key.c_str(), value.c_str());
    ESP_ERROR_CHECK(err);
    err = nvs_commit(nvs_handle);
    ESP_ERROR_CHECK(err);
}

std::string ConfigManager::get(const std::string& key) {
    std::string value;
    size_t required_size = 0;
    esp_err_t err = nvs_get_str(nvs_handle, key.c_str(), NULL, &required_size);
    if (err == ESP_OK) {
        value.resize(required_size);
        err = nvs_get_str(nvs_handle, key.c_str(), &value[0], &required_size);
        ESP_ERROR_CHECK(err);
    }
    return value;
}
