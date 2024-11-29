FROM debian:bookworm

# Install required packages
RUN apt-get update && \
    apt-get install -y avahi-daemon avahi-utils dbus && \
    apt-get clean

# Ensure required directories exist
RUN mkdir -p /var/run/dbus

# Copy custom service files (if any) into the container
COPY ./services/ /etc/avahi/services/
COPY ./avahi-daemon.conf /etc/avahi/
COPY ./start.sh /usr/local/bin/start-avahi.sh
RUN chmod +x /usr/local/bin/start-avahi.sh

# Start dbus and avahi-daemon when the container starts
# CMD ["bash", "-c", "dbus-daemon --system && avahi-daemon --no-drop-root --debug"]
ENTRYPOINT ["/usr/local/bin/start-avahi.sh"]
