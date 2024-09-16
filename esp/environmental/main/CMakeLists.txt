idf_component_register(SRCS "main.cpp"
                    INCLUDE_DIRS "."
                    REQUIRES 
                        M5AtomS3
                        MqttClient
                        WifiConnector
                        NvsManager
                        ConfigManager
                        json
                    )
