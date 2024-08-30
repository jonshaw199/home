#!/bin/bash

# Variables
SERVICE_NAME="js-home-system.service"
SERVICE_FILE_PATH="/etc/systemd/system/$SERVICE_NAME"
SCRIPT_PATH="/path/to/your/system.py"
ENV_FILE_PATH="/path/to/your/.env"

# Create a systemd service file
echo "Creating systemd service file at $SERVICE_FILE_PATH"

cat <<EOF | sudo tee $SERVICE_FILE_PATH > /dev/null
[Unit]
Description=System Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_PATH
WorkingDirectory=$(dirname $SCRIPT_PATH)
EnvironmentFile=$ENV_FILE_PATH
Restart=always
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to recognize the new service
echo "Reloading systemd daemon"
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling $SERVICE_NAME to start on boot"
sudo systemctl enable $SERVICE_NAME

# Start the service
echo "Starting $SERVICE_NAME"
sudo systemctl start $SERVICE_NAME

# Check the status of the service
echo "Checking the status of $SERVICE_NAME"
systemctl status $SERVICE_NAME

