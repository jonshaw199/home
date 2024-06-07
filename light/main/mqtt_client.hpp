#ifndef MQTT_CLIENT_H_
#define MQTT_CLIENT_H_

#include <string>

#include "mqtt_client.h"

typedef void (*message_cb)(std::string msg);

class MQTTClient {
    public:
        static void init(message_cb cb);
};

#endif // MQTT_CLIENT_H_
