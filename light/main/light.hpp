#ifndef LIGHT_H_
#define LIGHT_H_

#include <vector>
#include <map>

#include "FastLED.h"
#include "effect.hpp"

typedef std::multimap<int64_t, Effect> scheduled_effect_multimap;

class Light {
private:
  scheduled_effect_multimap scheduled_effects;

public:
  Light(int led_cnt);
  std::vector<CRGB> leds;
  void add_effect(Effect effect);
  void do_effect();
};


#endif // LIGHT_H_
