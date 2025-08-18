#!/bin/bash
# Install Docker
apt-get update
apt-get install -y docker.io

# Run Firefox with noVNC
docker run -d \
    -p 6080:6080 \
    -v /dev/shm:/dev/shm \
    --name firefox \
    dorowu/ubuntu-desktop-lxde-vnc
