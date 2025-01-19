## Local dev

First steps:

- `sudo apt install avahi-daemon` (for mDNS)
- Rename `.env.template` in root directory to `.env`
- Rename `services/home/.dev_pgpass.template` to `.dev_pgpass`
  - TODO: password
- Disable publishing in Avahi config
  1. Edit `/etc/avahi/avahi-daemon.conf`
  2. Set `disable-publishing=yes`
  3. Restart service with `sudo systemctl restart avahi-daemon`
- Generate certs for controller:

```
mkdir ./services/controller/certs

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ./services/controller/certs/key.pem \
  -out ./services/controller/certs/cert.pem
```

Updated steps; need a private CA now:

1. Generate a private CA certificate (`ca.crt` and `ca.key`)
2. Generate private key (`server.key`)
3. Create CSR (`server.csr`)
4. Use the private CA (`ca.crt` and `ca.key`) to sign the CSR (`server.csr`), creating `server.crt` for each domain
5. Include `subjectAltName` for the domain in the certificate (important for modern browsers)

### Web server, controller, MQTT broker, and system reporter

`docker compose --profile optional up -d`

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

### Testing prod locally

- Change `HOME_ENV` to `production` in root `.env` file
- Point `jonshaw199.com` and `www.jonshaw199.com` to localhost in `/etc/hosts`
