#include "ntp_client.h"
#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_log.h"
#include <time.h>
#include <nvs_flash.h>

static const char *TAG = "NTPClient";

NTPClient::NTPClient() : timezone("PST8PDT") {}

NTPClient::~NTPClient() {}

void NTPClient::begin()
{
    setup_sntp();
    obtain_time();
    print_time();
}

void NTPClient::setTimeZone(const char *timezone)
{
    this->timezone = timezone;
}

void NTPClient::setup_sntp()
{
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    // ESP_ERROR_CHECK(esp_event_loop_create_default());

    esp_sntp_config_t config = ESP_NETIF_SNTP_DEFAULT_CONFIG("pool.ntp.org");
    config.sync_cb = nullptr;
    esp_netif_sntp_init(&config);
    esp_netif_sntp_start();
}

void NTPClient::obtain_time()
{
    time_t now = 0;
    struct tm timeinfo = {0};

    int retry = 0;
    const int retry_count = 15;
    while (esp_netif_sntp_sync_wait(2000 / portTICK_PERIOD_MS) == ESP_ERR_TIMEOUT && ++retry < retry_count)
    {
        ESP_LOGI(TAG, "Waiting for system time to be set... (%d/%d)", retry, retry_count);
    }

    time(&now);
    localtime_r(&now, &timeinfo);
    ESP_LOGI(TAG, "Current time: %s", asctime(&timeinfo));
}

std::string NTPClient::get_time_str(std::string format = "%Y-%m-%d %H:%M:%S")
{
    setenv("TZ", timezone.c_str(), 1);
    tzset();

    time_t now;
    struct tm timeinfo;
    char buffer[64];

    // Get the current time
    time(&now);

    // Convert it to local time
    localtime_r(&now, &timeinfo);

    // Format time as a string, e.g., "2024-09-07 14:23:45"
    strftime(buffer, sizeof(buffer), format.c_str(), &timeinfo);

    return std::string(buffer);
}

void NTPClient::print_time()
{
    ESP_LOGI(TAG, "Current time: %s", get_time_str().c_str());
}
