#!/bin/bash
# Установка Docker
apt-get update && apt-get install -y docker.io

# Оптимизация для мощных машин
if [ $(nproc) -gt 2 ]; then
    echo "🦾 Мощная машина обнаружена! Оптимизируем настройки..."
    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1
fi

# Запуск Firefox с веб-интерфейсом
docker run -d --rm \
    -p 5800:5800 \
    -e DISPLAY_WIDTH=1600 \
    -e DISPLAY_HEIGHT=900 \
    -v firefox-config:/config:rw \
    --name firefox \
    jlesage/firefox

echo "=========================================="
echo "🌐 Firefox запущен с веб-интерфейсом!"
echo "🔗 Откройте: https://${CODESPACE_NAME}-5800.preview.app.github.dev"
echo "=========================================="
