idf_component_register(
    SRCS
        "main.cpp"
    REQUIRES 
        M5Dial
        MqttClient
        WifiConnector
        NvsManager
        ConfigManager
        esp_event
)

