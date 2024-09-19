#include "mqtt_utils.hpp"
#include "esp_log.h"

static const char *TAG = "MqttUtils";

const std::map<Group, std::string> MqttUtils::groups = {
    {GROUP_ENVIRONMENTAL, "environmentals"},
    {GROUP_DIAL, "dials"},
    {GROUP_SYSTEM, "systems"},
    {GROUP_PLUG, "plugs"}
};

const std::map<Subtopic, std::string> MqttUtils::subtopics = {
    {SUBTOPIC_COMMAND, "command"},
    {SUBTOPIC_STATUS, "status"}
};

const std::map<Action, std::string> MqttUtils::actions = {
    {ACTION_REQUEST_STATUS, "request_status"},
    {ACTION_ENVIRONMENTAL_STATUS, "environmental__status"},
    {ACTION_ENVIRONMENTAL_REQUEST_STATUS, "environmental__request_status"},
    {ACTION_DIAL_STATUS, "dial__status"},
    {ACTION_DIAL_REQUEST_STATUS, "dial__request_status"},
    {ACTION_SYSTEM_STATUS, "system__status"},
    {ACTION_SYSTEM_REQUEST_STATUS, "system__request_status"},
    {ACTION_PLUG_STATUS, "plug__status"},
    {ACTION_PLUG_REQUEST_STATUS, "plug__request_status"}
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

// JSON-related utils

// Function to parse a JSON string and return a cJSON object
cJSON* MqttUtils::parse_json_string(const std::string& json_str) {
    // Use cJSON_Parse to parse the JSON string
    cJSON *json_obj = cJSON_Parse(json_str.c_str());

    // If parsing failed, print an error and return nullptr
    if (json_obj == nullptr) {
        const char *error_ptr = cJSON_GetErrorPtr();
        if (error_ptr != nullptr) {
            ESP_LOGE(TAG, "Unable to parse JSON");
        }
        return nullptr;
    }

    // Return the cJSON object
    return json_obj;
}

// Function to get the string value for a given key from a cJSON object
std::string MqttUtils::get_json_string_value(cJSON* json_obj, const std::string& key) {
    // Check if the json_obj is valid
    if (json_obj == nullptr) {
        return {}; // Return empty string if the JSON object is invalid
    }

    // Get the item corresponding to the key
    cJSON* item = cJSON_GetObjectItemCaseSensitive(json_obj, key.c_str());

    // Check if the item exists and is a string
    if (item != nullptr && cJSON_IsString(item) && item->valuestring != nullptr) {
        return item->valuestring; // Return the string value
    }

    // Return an empty string if the key doesn't exist or value is not a string
    return {};
}