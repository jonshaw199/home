#include "mqtt_utils.hpp"
#include "esp_log.h"

static const char *TAG = "MqttUtils";

const std::map<Group, std::string> MqttUtils::groups = {
    {GROUP_ENVIRONMENTAL, "environmentals"},
    {GROUP_DIAL, "dials"},
    {GROUP_SYSTEM, "systems"}
};

const std::map<Subtopic, std::string> MqttUtils::subtopics = {
    {SUBTOPIC_COMMAND, "command"},
    {SUBTOPIC_STATUS, "status"}
};

const std::map<Action, std::string> MqttUtils::actions = {
    {ACTION_ENVIRONMENTAL_STATUS, "environmental__status"},
    //{ACTION_DIAL_STATUS, "dial__status"},
    {ACTION_SYSTEM_STATUS, "system__status"},
    //{ACTION_PLUG_STATUS, "plug__status"}
};

std::string MqttUtils::get_root_command_subscribe_topic() {
    auto subtopic_it = MqttUtils::subtopics.find(SUBTOPIC_COMMAND);
    
    if (subtopic_it != MqttUtils::subtopics.end()) {
        return subtopic_it->second;
    } else {
        ESP_LOGW(TAG, "Unable to get root subscribe topic");
        return "";
    }
}

std::string MqttUtils::get_group_command_subscribe_topic(Group group) {
    auto group_it = MqttUtils::groups.find(group);
    auto subtopic_it = MqttUtils::subtopics.find(SUBTOPIC_COMMAND);
    
    if (group_it != MqttUtils::groups.end() && subtopic_it != MqttUtils::subtopics.end()) {
        return group_it->second + "/" + subtopic_it->second;
    } else {
        ESP_LOGW(TAG, "Unable to get group subscribe topic");
        // Return an empty string if not found
        return "";
    }
}

std::string MqttUtils::get_device_command_subscribe_topic(Group group, const std::string device_id) {
    auto group_it = MqttUtils::groups.find(group);
    auto subtopic_it = MqttUtils::subtopics.find(SUBTOPIC_COMMAND);
    
    if (group_it != MqttUtils::groups.end() && subtopic_it != MqttUtils::subtopics.end()) {
        return group_it->second + "/" + device_id + "/" + subtopic_it->second;
    } else {
        ESP_LOGW(TAG, "Unable to get device subscribe topic");
        // Return an empty string if not found
        return "";
    }
}

std::string MqttUtils::get_device_publish_status_topic(Group group, const std::string device_id) {
    auto group_it = MqttUtils::groups.find(group);
    auto subtopic_it = MqttUtils::subtopics.find(SUBTOPIC_STATUS);
    
    if (group_it != MqttUtils::groups.end() && subtopic_it != MqttUtils::subtopics.end()) {
        return group_it->second + "/" + device_id + "/" + subtopic_it->second;
    } else {
        ESP_LOGW(TAG, "Unable to get publish status topic");
        // Return an empty string if not found
        return "";
    }
}

Topics MqttUtils::get_topics(Group group, std::string device_id) {
    Topics topics;
    topics.device_command_subscribe_topic = MqttUtils::get_device_command_subscribe_topic(group, device_id);
    topics.group_command_subscribe_topic = MqttUtils::get_group_command_subscribe_topic(group);
    topics.root_command_subscribe_topic = MqttUtils::get_root_command_subscribe_topic();
    topics.device_status_publish_topic = MqttUtils::get_device_publish_status_topic(group, device_id);
    return topics;
}

template <typename T>
std::string MqttUtils::get_map_str(T key, const std::map<T, std::string>& map) {    
    auto it = map.find(key);

    if (it != map.end()) {
        return it->second;
    } else {
        ESP_LOGW(TAG, "Unble to get map value");
        return "";
    }
}

std::string MqttUtils::get_group_str(Group group) {
    return MqttUtils::get_map_str<Group>(group, MqttUtils::groups);
}

std::string MqttUtils::get_subtopic_str(Subtopic subtopic) {
    return MqttUtils::get_map_str<Subtopic>(subtopic, MqttUtils::subtopics);
}

std::string MqttUtils::get_action_str(Action action) {
    return MqttUtils::get_map_str<Action>(action, MqttUtils::actions);
}