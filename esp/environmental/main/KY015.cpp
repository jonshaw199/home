
#include "KY015.hpp"
#include "esp_log.h"
#include <vector>
#include <rom/ets_sys.h>

static const char *TAG = "KY015";

KY015::KY015(gpio_num_t pin) : dataPin(pin) {
    gpio_set_direction(dataPin, GPIO_MODE_INPUT_OUTPUT);
}

KY015::Data KY015::read() {
    Data sensorData = {0.0f, 0.0f, false};

    // Send start signal
    gpio_set_direction(dataPin, GPIO_MODE_OUTPUT);
    gpio_set_level(dataPin, 0);
    ets_delay_us(18000); // Keep low for at least 18ms
    gpio_set_level(dataPin, 1);
    ets_delay_us(30);    // High for 20-40us

    gpio_set_direction(dataPin, GPIO_MODE_INPUT);

    // Check sensor's response
    if (!waitForStateChange(80, 0) || !waitForStateChange(80, 1)) {
        ESP_LOGE(TAG, "Sensor not responding.");
        return sensorData;
    }

    // Read 40 bits of data (5 bytes)
    uint8_t data[5] = {0};
    for (int i = 0; i < 40; ++i) {
        if (!waitForStateChange(50, 0)) {
            ESP_LOGE(TAG, "Failed to read bit.");
            return sensorData;
        }

        // Measure the length of the high state to determine bit value
        int duration = measureHighTime();
        if (duration == -1) {
            ESP_LOGE(TAG, "Failed to measure high time.");
            return sensorData;
        }

        // If the high state is longer than ~30us, it's a '1' bit
        int byteIndex = i / 8;
        int bitIndex = 7 - (i % 8);
        if (duration > 40) {
            data[byteIndex] |= (1 << bitIndex);
        }
    }

    // Validate checksum
    if (data[4] != (data[0] + data[1] + data[2] + data[3])) {
        ESP_LOGE(TAG, "Checksum error.");
        return sensorData;
    }

    // Parse temperature and humidity
    sensorData.humidity = data[0] + data[1] * 0.1f;
    sensorData.temperature = data[2] + data[3] * 0.1f;
    sensorData.success = true;

    return sensorData;
}


bool KY015::waitForStateChange(int timeoutUs, int targetState) {
    int elapsed = 0;
    while (gpio_get_level(dataPin) == targetState) {
        ets_delay_us(1);
        if (++elapsed >= timeoutUs) {
            return false;
        }
    }
    return true;
}

int KY015::measureHighTime() {
    int duration = 0;
    while (gpio_get_level(dataPin) == 1) {
        ets_delay_us(1);
        if (++duration > 100) {
            return -1; // Timeout
        }
    }
    return duration;
}

