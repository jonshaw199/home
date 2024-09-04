#include "effect.hpp"

std::string Effect::get_id() {
    return id;
}

void Effect::set_id(std::string i) {
   id = i;
}

EffectType Effect::get_type() {
    return type;
}

void Effect::set_type(EffectType t) {
    type = t;
}

const CRGBPalette16& Effect::get_palette() {
  return palette;
}

void Effect::set_palette(const CRGBPalette16& p) {
  palette = p;
}

accum88 Effect::get_bpm() {
  return bpm;
}

void Effect::set_bpm(accum88 b) {
  bpm = b;
}

uint8_t Effect::get_brightness() {
  return brightness;
}

void Effect::set_brightness(uint8_t b) {
  brightness = b;
}

TBlendType Effect::get_blend_type() {
  return blend_type;
}

void Effect::set_blend_type(TBlendType b) {
  blend_type = b;
}

int64_t Effect::get_start_time() {
    return start_time;
}

void Effect::set_start_time(int64_t t) {
    start_time = t;
}

int64_t Effect::get_duration() {
    return duration;
}

void Effect::set_duration(int64_t d) {
    duration = d;
}
