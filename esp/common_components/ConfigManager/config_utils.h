#ifndef CONFIG_UTILS_H
#define CONFIG_UTILS_H

#include <string>

struct BaseConfig {
    std::string device_id = "";
    std::string wifi_ssid = "";
    std::string wifi_pass = "";
    std::string mqtt_broker = "";
};

class ConfigUtils {
public:
    static BaseConfig get_base_config();
    static void set_base_config(BaseConfig config);
    static BaseConfig get_or_init_base_config(BaseConfig default_config);
};

#endif // CONFIG_UTILS_H