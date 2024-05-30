#ifndef LIGHT_H_
#define LIGHT_H_

#include <map>
#include <string>
#include <vector>

#include "FastLED.h"

class Light; // forward declaration

typedef void (*effect_func)(Light *light);

void turn_off(Light *light); // forward declaration

class Light {
private:
  CRGBPalette16 palette = CRGBPalette16(CRGB::Black);
  accum88 bpm = 100;
  uint8_t brightness = 255;
  TBlendType blend_type = LINEARBLEND;
  effect_func effect = turn_off;

public:
  Light(int led_cnt);
  std::vector<CRGB> leds;
  void do_effect();
  const CRGBPalette16& get_palette();
  void set_palette(const CRGBPalette16& palette);
  accum88 get_bpm();
  void set_bpm(accum88 bpm);
  uint8_t get_brightness();
  void set_brightness(uint8_t brightness);
  TBlendType get_blend_type();
  void set_blend_type(TBlendType blend_type);
};

typedef std::map<std::string, Light*> light_map;

class LightHandler {
private:
  light_map lights;
public:
  LightHandler(const light_map& lights);
  void init();
};

#endif // LIGHT_H_
