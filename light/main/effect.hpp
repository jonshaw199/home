#ifndef EFFECT_H_
#define EFFECT_H_

#include "FastLED.h"

enum EffectType {
  TURN_OFF,
  BEATWAVE
};

class Effect {
private:
    EffectType type = TURN_OFF;
    CRGBPalette16 palette = CRGBPalette16(CRGB::Blue);
    accum88 bpm = 100;
    uint8_t brightness = 50;
    TBlendType blend_type = LINEARBLEND;
    int64_t start_time = 0;
    int64_t duration = 999999999;

public:
    Effect(EffectType type);
    EffectType get_type();
    void set_type(EffectType type);
    const CRGBPalette16& get_palette();
    void set_palette(const CRGBPalette16& palette);
    accum88 get_bpm();
    void set_bpm(accum88 bpm);
    uint8_t get_brightness();
    void set_brightness(uint8_t brightness);
    TBlendType get_blend_type();
    void set_blend_type(TBlendType blend_type);
    int64_t get_start_time();
    void set_start_time(int64_t start_time);
    int64_t get_duration();
    void set_duration(int64_t duration);
};

#endif // EFFECT_H_
