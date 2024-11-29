#!/bin/bash

# Clean up any leftover DBus PID file
rm -f /run/dbus/pid

# Start dbus-daemon
dbus-daemon --system

# Start avahi-daemon with your custom configuration
avahi-daemon --no-drop-root --debug
