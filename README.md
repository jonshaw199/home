## Local Dev

### Run web server, controller, and MQTT broker

`docker compose up`

### Run clients

#### Android

``` sh
cd client
npm run android
adb -s <emulator-name> reverse tcp:8000 tcp:8000
```

### Run lights

``` sh
cd light
idf.py build flash monitor
```
