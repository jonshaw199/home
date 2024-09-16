#ifndef KY015_H
#define KY015_H

#include "driver/gpio.h"

class KY015 {
public:
    struct Data {
        float temperature;
        float humidity;
        bool success;
    };

    KY015(gpio_num_t pin);
    Data read();

private:
    gpio_num_t dataPin;

    bool waitForStateChange(int timeoutUs, int targetState);
    int measureHighTime();
};

#endif