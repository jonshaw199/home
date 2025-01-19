FROM alpine

RUN apk add --no-cache avahi avahi-tools

# Copy custom service files into the container
COPY ./services/ /etc/avahi/services/
COPY ./avahi-daemon.conf /etc/avahi/

# Add a script to set the hostname dynamically
COPY ./set-hostname.sh /usr/local/bin/set-hostname.sh
RUN chmod +x /usr/local/bin/set-hostname.sh

# Use the script as the entrypoint
ENTRYPOINT ["/usr/local/bin/set-hostname.sh"]