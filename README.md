## Local dev

First steps:

- Rename `.env.template` in root directory to `.env`

### Web server, controller, MQTT broker, and system reporter

`docker compose --optional system-reporter up -d`

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

- Generating fixtures:
  - To export multiple apps or models at once, list them in the command like this: `python manage.py dumpdata app1.ModelName1 app2.ModelName2 --indent 2 > fixtures.json`
  - For all models in an app: `python manage.py dumpdata app_name --indent 2 > app_fixtures.json`
  - To dump all models in all apps, you can run: `python manage.py dumpdata --indent 2 > all_fixtures.json`
