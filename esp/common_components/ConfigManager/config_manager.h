#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <string>
//#include <nvs_handle.h>
#include <nvs_flash.h>
#include <nvs.h>

class ConfigManager {
public:
    ConfigManager();
    ~ConfigManager();
    void set(const std::string& key, const std::string& value);
    std::string get(const std::string& key);

private:
    nvs_handle_t nvs_handle;
};

#endif // CONFIG_MANAGER_H
