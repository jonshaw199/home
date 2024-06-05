#include "effect.hpp"

Effect::Effect(EffectType type, EffectConfig config) : type(type), config(config) {}

EffectType Effect::get_type() {
    return type;
}

void Effect::set_type(EffectType t) {
    type = t;
}

EffectConfig Effect::get_config() {
    return config;
}

void Effect::set_config(EffectConfig c) {
    config = c;
}
