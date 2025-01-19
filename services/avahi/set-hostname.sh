#!/bin/sh

# Assuming HOME_HOSTNAME is already set in the environment or script
AVAHI_HOST_NAME="${HOME_HOSTNAME%%.*}"

# Replace the placeholder in avahi-daemon.conf
sed -i "s/%AVAHI_HOST_NAME%/${AVAHI_HOST_NAME}/" /etc/avahi/avahi-daemon.conf

echo "Starting Avahi with hostname: ${AVAHI_HOST_NAME}"

# Start the Avahi daemon
exec avahi-daemon --no-drop-root --no-rlimits --debug
