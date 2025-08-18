#!/bin/bash
# Установка Docker
apt-get update && apt-get install -y docker.io

# Запуск Firefox с VNC
docker run -d --rm \
    -p 5800:5800 \
    -p 5900:5900 \
    -v firefox-config:/config:rw \
    --name firefox \
    jlesage/firefox

echo "Firefox запущен!"
echo "Доступ через:"
echo "- Веб-интерфейс VNC: https://${CODESPACE_NAME}-5800.preview.app.github.dev"
echo "- Клиент VNC: ${CODESPACE_NAME}-5900.preview.app.github.dev"
