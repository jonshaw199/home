#ifndef MQTT_CLIENT_H_
#define MQTT_CLIENT_H_

#include <string>
#include <vector>

#include "mqtt_client.h"

typedef void (*message_cb)(std::string topic, std::string msg);
typedef std::vector<std::string> topic_vector;

class MQTTClient {
    public:
        static void init(topic_vector topics, message_cb cb);
};

#endif // MQTT_CLIENT_H_
