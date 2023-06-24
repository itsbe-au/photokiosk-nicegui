#!/bin/bash

export DISPLAY=:0

killall firefox
killall unclutter
killall chromium-browser

# sudo apt-get install unclutter
unclutter -idle 1 -root &

cd /home/photo/photokiosk-nicegui

# Stop running docker containers.
echo "Removing old containers."
docker container stop $(docker container ls -aq)
docker container rm photokiosk

# Fetch the latest source code
echo "Building the app."
git pull
docker build -t photokiosk .
docker run -dit -p 80:7777 --restart unless-stopped --name photokiosk -v "$(pwd)"/images:/app/images photokiosk

echo "Photokiosk docker container launched."

# Finally, launch Chrome in private kiosk mode
echo "Launching Chrome."
chromium-browser --kiosk http://localhost