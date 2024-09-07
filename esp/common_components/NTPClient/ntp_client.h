#ifndef NTP_CLIENT_H
#define NTP_CLIENT_H

#include <string>

class NTPClient
{
public:
    // Constructor
    NTPClient();

    // Destructor
    ~NTPClient();

    // Initializes the NTP client and fetches the current time
    void begin();

    // Sets the time zone for displaying time
    void setTimeZone(const char *timezone);

    std::string get_time_str(std::string format);

private:
    // Sets up the SNTP configuration
    void setup_sntp();

    // Waits for and obtains the current time from the NTP server
    void obtain_time();

    // Prints the current time to the log
    void print_time();

    std::string timezone; // Time zone string
};

#endif // NTP_CLIENT_H
