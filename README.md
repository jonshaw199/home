## Local dev

### Web server, controller, MQTT broker, and system reporter

`HOME_ENV=development docker compose up -d`

### Web/mobile clients

```sh
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

```sh
cd esp/lights
idf.py build flash monitor
```

#### Environmental

```sh
cd esp/environmental
idf.py build flash monitor
```

### Misc Notes

- For convenience, add a record to DNS server for home.com that points to MQTT broker; all devices can then point to home.com and the underlying IP can be changed easily
