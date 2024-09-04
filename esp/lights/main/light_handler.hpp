#ifndef LIGHT_HANDLER_H_
#define LIGHT_HANDLER_H_

#include <map>
#include <string>

#include "cJSON.h"

#include "light.hpp"

typedef std::map<std::string, Light&> light_map;

class LightHandler {
  private:
    light_map lights;

  public:
    LightHandler(const light_map& lights);
    void init();
    void add_effect(Effect effect, std::string light_id = "");
    void delete_effect(std::string id = "", std::string light_id = "");
};

#endif // LIGHT_HANDLER_H_
