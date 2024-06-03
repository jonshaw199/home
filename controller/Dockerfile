FROM python:3.9.19-alpine3.20
WORKDIR /code
RUN apk --no-cache add mosquitto-clients
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
ENTRYPOINT python controller.py
