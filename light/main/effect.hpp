#ifndef EFFECT_H_
#define EFFECT_H_

#include "effect_config.hpp"

enum EffectType {
  TURN_OFF,
  BEATWAVE
};

class Effect {
private:
    EffectType type = TURN_OFF;
    EffectConfig config;

public:
    Effect(EffectType type, EffectConfig config);
    EffectType get_type();
    void set_type(EffectType type);
    EffectConfig get_config();
    void set_config(EffectConfig config);
};

#endif // EFFECT_H_
