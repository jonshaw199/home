FROM alpine:3.20.0
RUN apk --no-cache add mosquitto mosquitto-clients
ADD mosquitto.conf /mosquitto.conf
ENTRYPOINT /usr/sbin/mosquitto -c /mosquitto.conf
