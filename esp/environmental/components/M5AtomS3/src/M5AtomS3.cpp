#include "M5AtomS3.h"

using namespace m5;

M5AtomS3 AtomS3;

void M5AtomS3::begin(bool ledEnable) {
    M5.begin();
    _led_enable = ledEnable;
}

void M5AtomS3::begin(m5::M5Unified::config_t cfg, bool ledEnable) {
    M5.begin(cfg);
    _led_enable = ledEnable;
}

void M5AtomS3::update() {
    M5.update();
}
