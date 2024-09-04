## Local dev

### Web server, controller, MQTT broker, and system reporter

`docker compose up -d`

### Web/mobile clients

#### Android

``` sh
cd client
npm i
npm run <android | ios | web>
adb -s <emulator-name> reverse tcp:8000 tcp:8000
```

### Devices

Requires ESP-IDF v5.1.4

#### Dial

```sh
cd esp/dial
idf.py build flash monitor
```

#### Lights

``` sh
cd esp/lights
idf.py build flash monitor
```
