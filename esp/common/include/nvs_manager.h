#ifndef NVS_MANAGER_H
#define NVS_MANAGER_H

#include <string>
#include "nvs_flash.h"
#include "nvs.h"

class NvsManager {
public:
    // Constructor: Initializes NVS
    NvsManager(const std::string& namespace_name);

    // Destructor: Closes NVS handle
    ~NvsManager();

    // Set a string value in NVS
    esp_err_t setString(const std::string& key, const std::string& value);

    // Get a string value from NVS
    esp_err_t getString(const std::string& key, std::string& value);

    // Set an integer value in NVS
    esp_err_t setInt(const std::string& key, int32_t value);

    // Get an integer value from NVS
    esp_err_t getInt(const std::string& key, int32_t& value);

private:
    nvs_handle_t handle;
    std::string namespace_name;
};

#endif // NVS_MANAGER_H
