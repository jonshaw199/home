#ifndef MDNS_RESOLVER_H
#define MDNS_RESOLVER_H

#include <string>


class MdnsResolver {
public:
    void init();
    std::string resolve_hostname(const std::string& hostname);
};

#endif // MDNS_RESOLVER_H
