#!/bin/bash
# Установка Docker
apt-get update && apt-get install -y docker.io

# Минимальные настройки для снижения нагрузки
docker run -d --rm \
    -p 5800:5800 \
    -e DISPLAY_WIDTH=1024 \
    -e DISPLAY_HEIGHT=768 \
    -e VNC_PASSWORD=password \
    -v firefox-data:/config \
    --name firefox \
    jlesage/firefox

echo "=================================="
echo "🦊 Firefox запущен в легком режиме"
echo "🔗 URL: https://${CODESPACE_NAME}-5800.preview.app.github.dev"
echo "🔒 Пароль VNC: password"
echo "=================================="
