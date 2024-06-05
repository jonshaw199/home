#ifndef LIGHT_HANDLER_H_
#define LIGHT_HANDLER_H_

#include <map>
#include <string>

#include "light.hpp"

typedef std::map<std::string, Light*> light_map;

class LightHandler {
private:
  light_map lights;
public:
  LightHandler(const light_map& lights);
  void init();
};

#endif // LIGHT_HANDLER_H_
