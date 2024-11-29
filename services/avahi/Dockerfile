FROM alpine

RUN apk add --no-cache avahi avahi-tools

# Copy custom service files into the container
COPY ./services/ /etc/avahi/services/
COPY ./avahi-daemon.conf /etc/avahi/
COPY ./start.sh /usr/local/bin/start-avahi.sh
# Make executable
RUN chmod +x /usr/local/bin/start-avahi.sh

ENTRYPOINT avahi-daemon --no-drop-root --no-rlimits --debug
