#!/bin/bash
# Установка Docker
apt-get update && apt-get install -y docker.io

# Запуск Firefox с веб-интерфейсом (без VNC)
docker run -d --rm \
    -p 5800:5800 \
    -e DISPLAY_WIDTH=1024 \
    -e DISPLAY_HEIGHT=768 \
    -e ENABLE_CJK_FONT=1 \
    -e SECURE_CONNECTION=1 \
    -v firefox-data:/config \
    --name firefox \
    jlesage/firefox

echo "=========================================="
echo "🦊 Firefox запущен в безопасном режиме"
echo "🌐 URL: https://${CODESPACE_NAME}-5800.preview.app.github.dev"
echo "=========================================="
