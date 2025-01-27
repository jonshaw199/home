#include "mdns_resolver.h"

#include "mdns.h"
#include "esp_check.h"
#include <esp_log.h>
#include "lwip/ip_addr.h"

static const char *TAG = "mdns";

void MdnsResolver::init() {
    ESP_ERROR_CHECK(mdns_init());
    // ESP_ERROR_CHECK(mdns_hostname_set("esp32-device")); // Optional: set ESP32's hostname
    ESP_LOGI(TAG, "mDNS initialized");
}

std::string MdnsResolver::resolve_hostname(const std::string& hostname) {
    // Remove ".local" if present
    std::string trimmed_hostname = hostname;
    const std::string mdns_suffix = ".local";
    size_t pos = trimmed_hostname.rfind(mdns_suffix);
    if (pos != std::string::npos) {
        trimmed_hostname = trimmed_hostname.substr(0, pos);
    }

    // Query for IP by hostname
    esp_ip4_addr_t addr;
    std::string addr_str;
    if (mdns_query_a(trimmed_hostname.c_str(), 2000, &addr) == ESP_OK) {
        addr_str = ip4addr_ntoa(reinterpret_cast<const ip4_addr_t*>(&addr));
        ESP_LOGI(TAG, "Resolved %s to %s", hostname.c_str(), addr_str.c_str());
        return addr_str;
    } else {
        ESP_LOGE(TAG, "Failed to resolve %s", hostname.c_str());
        return hostname;
    }
}