## Local Dev

### Run server

`./services/home/manage.py runserver`

### Run redis for channels

`docker run --rm -p 6379:6379 redis:7` 

### Run on-prem controller

`python controller/controller.py`
`mosquitto -v -c controller/mosquitto.conf`

### Run client

#### Android

`cd client`
`npm run android`
`adb -s <emulator-name> reverse tcp:8000 tcp:8000`
