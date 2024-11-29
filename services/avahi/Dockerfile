FROM alpine

RUN apk add --no-cache avahi avahi-tools

# Copy custom service files into the container
COPY ./services/ /etc/avahi/services/
COPY ./avahi-daemon.conf /etc/avahi/

ENTRYPOINT avahi-daemon --no-drop-root --no-rlimits --debug
