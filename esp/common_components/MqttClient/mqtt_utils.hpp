#ifndef MQTT_UTILS_H
#define MQTT_UTILS_H

#include <map>
#include <string>

struct Topics {
    std::string root_command_subscribe_topic = "";
    std::string group_command_subscribe_topic = "";
    std::string device_command_subscribe_topic = "";
    std::string device_status_publish_topic = "";
};

enum Group {
    GROUP_ENVIRONMENTAL,
    GROUP_DIAL,
    GROUP_SYSTEM,
    GROUP_PLUG
};

enum Subtopic {
    SUBTOPIC_STATUS,
    SUBTOPIC_COMMAND
};

enum Action {
    ACTION_ENVIRONMENTAL_STATUS,
    ACTION_DIAL_STATUS,
    ACTION_SYSTEM_STATUS,
    ACTION_PLUG_STATUS
};

class MqttUtils {
public:
    static const std::map<Group, std::string> groups;
    static const std::map<Subtopic, std::string> subtopics;
    static const std::map<Action, std::string> actions;

    static std::string get_root_command_subscribe_topic();
    static std::string get_group_command_subscribe_topic(Group group);
    static std::string get_device_command_subscribe_topic(Group group, std::string device_id);
    static std::string get_device_publish_status_topic(Group group, std::string device_id);
    static Topics get_topics(Group group, std::string device_id);

    static std::string get_group_str(Group group);
    static std::string get_subtopic_str(Subtopic subtopic);
    static std::string get_action_str(Action action);

private:
    template <typename T>
    static std::string get_map_str(T key, const std::map<T, std::string>& map);
};

#endif // MQTT_UTILS_H