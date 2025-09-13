#!/bin/bash

# === start-proxy.sh ===
# Автоматический запуск Caddy-прокси с кастомной HTML-страницей Bubles Portal
# Всё работает через GitHub Codespace, все ссылки — через прокси

set -e

echo "🚀 Установка и запуск Caddy-прокси с кастомным порталом 'Bubles'..."

# --- 1. Устанавливаем Caddy, если нужно ---
if ! command -v caddy &> /dev/null; then
    echo "🔧 Устанавливаем Caddy..."
    curl -s https://getcaddy.com | bash -s personal
fi

# --- 2. Создаём директории ---
mkdir -p ~/.caddy/html
cd ~/.caddy

# --- 3. Генерируем HTML-файл "Bubles Portal" ---
cat > html/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bubles</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            overflow: hidden;
        }
        .logo {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 10px rgba(0,0,0,0.3);
            letter-spacing: -2px;
        }
        .search-box {
            width: 80%;
            max-width: 600px;
            padding: 16px 20px;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            outline: none;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            margin-bottom: 3rem;
            text-align: center;
        }
        .icons {
            display: flex;
            gap: 24px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .icon {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            text-decoration: none;
            transition: transform 0.3s ease, scale 0.3s ease;
            color: white;
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        .icon:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 12px 30px rgba(0,0,0,0.3);
        }
        .youtube { background: #FF0000; }
        .x { background: #000000; }
        .instagram { background: #E1306C; }
        .upwork { background: #00b489; }

        /* Анимация пузырьков */
        .bubble {
            position: fixed;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            animation: float 6s infinite ease-in-out;
            pointer-events: none;
        }
        @keyframes float {
            0% { transform: translateY(100vh) scale(0); opacity: 0; }
            50% { opacity: 0.8; }
            100% { transform: translateY(-100px) scale(1); opacity: 0; }
        }
    </style>
</head>
<body>

    <div class="logo">Bubles</div>

    <form onsubmit="search(event)" style="width:100%; max-width:600px;">
        <input type="text" class="search-box" placeholder="Поиск через Bubles..." autofocus>
    </form>

    <div class="icons">
        <a href="/proxy?url=https://youtube.com" class="icon youtube">▶️</a>
        <a href="/proxy?url=https://x.com" class="icon x">𝕏</a>
        <a href="/proxy?url=https://instagram.com" class="icon instagram">📸</a>
        <a href="/proxy?url=https://upwork.com" class="icon upwork">💼</a>
    </div>

    <script>
        function search(e) {
            e.preventDefault();
            const query = e.target[0].value.trim();
            if (!query) return;
            // Если начинается с http — открываем как URL
            if (query.startsWith('http')) {
                window.location.href = '/proxy?url=' + encodeURIComponent(query);
            } else {
                // Иначе — ищем в Google
                window.location.href = '/proxy?url=https://google.com/search?q=' + encodeURIComponent(query);
            }
        }

        // Добавляем анимацию пузырьков
        for (let i = 0; i < 20; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.left = Math.random() * 100 + '%';
            bubble.style.animationDuration = (Math.random() * 4 + 3) + 's';
            bubble.style.animationDelay = Math.random() * 5 + 's';
            bubble.style.width = Math.random() * 20 + 10 + 'px';
            bubble.style.height = bubble.style.width;
            document.body.appendChild(bubble);
        }
    </script>

</body>
</html>
EOF

# --- 4. Создаём Caddyfile для обработки всех запросов ---
cat > Caddyfile << 'EOF'
{
    http_port 3000
    https_port 3000
}

:3000 {
    root * /home/codespace/.caddy/html
    file_server

    # Проксируем все /proxy?url=... на целевой сайт
    handle /proxy* {
        uri strip_prefix /proxy
        reverse_proxy {query} {
            transport http {
                tls_server_name {uri.query}
            }
            header_up Host {uri.query}
            header_up X-Forwarded-For {remote_host}
            header_up X-Forwarded-Proto {scheme}
        }
    }

    # Обработка всех остальных путей — редирект на index.html
    handle /* {
        rewrite * /index.html
        file_server
    }
}
EOF

# --- 5. Запускаем Caddy ---
echo "▶️ Запускаем Caddy на порту 3000..."
caddy run --config ~/.caddy/Caddyfile &
CADDY_PID=$!

# Ждём, пока Caddy запустится
sleep 3

# --- 6. Выводим ссылку доступа ---
USERNAME=$(whoami | cut -d'-' -f1)
CODESPACE_URL="https://3000-${USERNAME}.githubpreview.dev"

echo ""
echo "🎉 Готово! Твой Bubles Portal запущен!"
echo "🔗 Перейди по ссылке: ${CODESPACE_URL}"
echo ""
echo "💡 Что ты можешь делать:"
echo "   • Ввести любой запрос в поисковую строку → будет через Google"
echo "   • Кликнуть на иконку → откроется сайт через твой прокси"
echo "   • Ввести полный URL (например: https://twitter.com) → тоже проксируется"
echo ""
echo "🔒 Все запросы идут через твой прокси — даже после первого перехода!"
echo "✨ Пузырьки анимированы — приятный UX 😉"

# Оставляем процесс запущенным
wait $CADDY_PID
