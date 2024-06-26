#ifndef LIGHT_H_
#define LIGHT_H_

#include <vector>
#include <map>

#include "FastLED.h"
#include "effect.hpp"

#include <mutex>

typedef std::multimap<int64_t, Effect> scheduled_effect_multimap;

class Light {
private:
  scheduled_effect_multimap scheduled_effects;
  std::mutex scheduled_effects_mutex;

public:
  Light(int led_cnt);
  std::vector<CRGB> leds;
  void add_effect(Effect effect);
  void delete_effect(std::string id = "");
  void do_effect(uint64_t time);
};


#endif // LIGHT_H_
