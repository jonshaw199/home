#include "config_utils.h"
#include "config_manager.h"

ConfigManager config_manager;

BaseConfig ConfigUtils::get_base_config() {
    std::string device_id = config_manager.get("DEVICE_ID");
    std::string ssid = config_manager.get("WIFI_SSID");
    std::string pass = config_manager.get("WIFI_PASSWORD");
    std::string mqtt_broker = config_manager.get("MQTT_BROKER");
    BaseConfig config = {device_id, ssid, pass, mqtt_broker};
    return config;
}

void ConfigUtils::set_base_config(BaseConfig config) {
    config_manager.set("DEVICE_ID", config.device_id);
    config_manager.set("WIFI_SSID", config.wifi_ssid);
    config_manager.set("WIFI_PASSWORD", config.wifi_pass);
    config_manager.set("MQTT_BROKER", config.mqtt_broker);
}

BaseConfig ConfigUtils::get_or_init_base_config(BaseConfig default_config) {
    if (config_manager.get("DEVICE_ID").empty()) {
        set_base_config(default_config);
        return default_config;
    } else {
        BaseConfig config;
        config.device_id = config_manager.get("DEVICE_ID");
        config.wifi_ssid = config_manager.get("WIFI_SSID");
        config.wifi_pass = config_manager.get("WIFI_PASSWORD");
        config.mqtt_broker = config_manager.get("MQTT_BROKER");
        return config;
    }
}