## Local Dev

### Run server

``` sh
// TODO postgres
docker run --rm -p 6379:6379 redis:7 
./services/home/manage.py runserver
```

### Run on-prem controller

``` sh
python controller/controller.py
mosquitto -v -c controller/mosquitto.conf
```

### Run client

#### Android

``` sh
cd client
npm run android
adb -s <emulator-name> reverse tcp:8000 tcp:8000
```

