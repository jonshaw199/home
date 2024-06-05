#include "effect_config.hpp"

const CRGBPalette16& EffectConfig::get_palette() {
  return palette;
}

void EffectConfig::set_palette(const CRGBPalette16& p) {
  palette = p;
}

accum88 EffectConfig::get_bpm() {
  return bpm;
}

void EffectConfig::set_bpm(accum88 b) {
  bpm = b;
}

uint8_t EffectConfig::get_brightness() {
  return brightness;
}

void EffectConfig::set_brightness(uint8_t b) {
  brightness = b;
}

TBlendType EffectConfig::get_blend_type() {
  return blend_type;
}

void EffectConfig::set_blend_type(TBlendType b) {
  blend_type = b;
}

int64_t EffectConfig::get_start_time() {
    return start_time;
}

void EffectConfig::set_start_time(int64_t t) {
    start_time = t;
}

int64_t EffectConfig::get_duration() {
    return duration;
}

void EffectConfig::set_duration(int64_t d) {
    duration = d;
}

