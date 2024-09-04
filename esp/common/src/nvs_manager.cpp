#include "nvs_manager.h"
#include "esp_log.h"

static const char* TAG = "NvsManager";

NvsManager::NvsManager(const std::string& namespace_name) : namespace_name(namespace_name) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ret = nvs_open(namespace_name.c_str(), NVS_READWRITE, &handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Error (%s) opening NVS handle!", esp_err_to_name(ret));
    }
}

NvsManager::~NvsManager() {
    if (handle) {
        nvs_close(handle);
    }
}

esp_err_t NvsManager::setString(const std::string& key, const std::string& value) {
    esp_err_t ret = nvs_set_str(handle, key.c_str(), value.c_str());
    if (ret == ESP_OK) {
        ret = nvs_commit(handle);
    }
    return ret;
}

esp_err_t NvsManager::getString(const std::string& key, std::string& value) {
    size_t required_size;
    esp_err_t ret = nvs_get_str(handle, key.c_str(), nullptr, &required_size);
    if (ret == ESP_OK) {
        char* buffer = new char[required_size];
        ret = nvs_get_str(handle, key.c_str(), buffer, &required_size);
        if (ret == ESP_OK) {
            value.assign(buffer);
        }
        delete[] buffer;
    }
    return ret;
}

esp_err_t NvsManager::setInt(const std::string& key, int32_t value) {
    esp_err_t ret = nvs_set_i32(handle, key.c_str(), value);
    if (ret == ESP_OK) {
        ret = nvs_commit(handle);
    }
    return ret;
}

esp_err_t NvsManager::getInt(const std::string& key, int32_t& value) {
    return nvs_get_i32(handle, key.c_str(), &value);
}
