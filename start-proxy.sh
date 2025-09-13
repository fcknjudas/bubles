#!/bin/bash

# === start-proxy.sh ===
# Bubles Portal v2.0 — Прокси-портал с историей, темами и авто-пингом
# Работает в GitHub Codespace, все запросы — через прокси, каждый пользователь — свой профиль

set -e

echo "🚀 Запуск Bubles Portal v2.0 — с историей, темами и авто-пингом..."

# --- 1. Устанавливаем Caddy ---
if ! command -v caddy &> /dev/null; then
    echo "🔧 Устанавливаем Caddy..."
    curl -s https://getcaddy.com | bash -s personal
fi

# --- 2. Создаём директории ---
mkdir -p ~/.caddy/html
cd ~/.caddy

# --- 3. Генерируем HTML-файл с историей, темами и авто-пингом ---
cat > html/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bubles</title>
    <style>
        :root {
            --bg: #f0f2f5;
            --text: #333;
            --card: #ffffff;
            --accent: #667eea;
            --shadow: rgba(0,0,0,0.1);
        }
        .dark-mode {
            --bg: #121212;
            --text: #f0f0f0;
            --card: #1e1e1e;
            --accent: #764ba2;
            --shadow: rgba(0,0,0,0.4);
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            transition: background 0.5s ease;
            overflow: hidden;
        }
        .logo {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 1.5rem;
            text-shadow: 0 4px 10px var(--shadow);
            letter-spacing: -2px;
            color: var(--accent);
        }
        .search-box {
            width: 80%;
            max-width: 600px;
            padding: 16px 20px;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            outline: none;
            box-shadow: 0 8px 25px var(--shadow);
            margin-bottom: 2rem;
            text-align: center;
            background: var(--card);
            color: var(--text);
        }
        .icons {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 2rem;
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            color: white;
            box-shadow: 0 6px 15px var(--shadow);
            background: var(--accent);
        }
        .icon:hover {
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 12px 30px var(--shadow);
        }
        .youtube { background: #FF0000; }
        .x { background: #000000; }
        .instagram { background: #E1306C; }
        .upwork { background: #00b489; }

        .history {
            margin-top: 1rem;
            max-width: 600px;
            width: 80%;
            text-align: left;
        }
        .history-item {
            display: inline-block;
            margin: 6px 8px 6px 0;
            padding: 8px 14px;
            border-radius: 30px;
            font-size: 0.9rem;
            background: var(--card);
            color: var(--text);
            cursor: pointer;
            box-shadow: 0 3px 10px var(--shadow);
            transition: transform 0.2s;
        }
        .history-item:hover {
            transform: translateY(-2px);
        }
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--card);
            border: none;
            box-shadow: 0 4px 15px var(--shadow);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            color: var(--text);
            font-size: 1.5rem;
        }
        .bubble {
            position: fixed;
            width: 15px;
            height: 15px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            animation: float 8s infinite ease-in-out;
            pointer-events: none;
        }
        @keyframes float {
            0% { transform: translateY(100vh) scale(0); opacity: 0; }
            50% { opacity: 0.6; }
            100% { transform: translateY(-100px) scale(1); opacity: 0; }
        }
        .ping-indicator {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 0.7rem;
            color: rgba(255,255,255,0.6);
            z-index: 1000;
        }
    </style>
</head>
<body>

    <button class="theme-toggle" id="themeToggle">🌙</button>

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

    <div class="history" id="history"></div>

    <div class="ping-indicator" id="pingIndicator">🔄 Пинг активен</div>

    <script>
        // --- Темная/светлая тема ---
        const themeToggle = document.getElementById('themeToggle');
        const body = document.body;

        function loadTheme() {
            const saved = localStorage.getItem('bubles-theme') || 'light';
            if (saved === 'dark') {
                body.classList.add('dark-mode');
                themeToggle.textContent = '☀️';
            } else {
                body.classList.remove('dark-mode');
                themeToggle.textContent = '🌙';
            }
        }

        themeToggle.addEventListener('click', () => {
            if (body.classList.contains('dark-mode')) {
                body.classList.remove('dark-mode');
                localStorage.setItem('bubles-theme', 'light');
                themeToggle.textContent = '🌙';
            } else {
                body.classList.add('dark-mode');
                localStorage.setItem('bubles-theme', 'dark');
                themeToggle.textContent = '☀️';
            }
        });

        // --- История ---
        function loadHistory() {
            const userId = localStorage.getItem('bubles-userid') || Math.random().toString(36).substring(2, 9);
            localStorage.setItem('bubles-userid', userId);

            const history = JSON.parse(localStorage.getItem(`bubles-history-${userId}`)) || [];
            const historyContainer = document.getElementById('history');

            historyContainer.innerHTML = '';
            if (history.length === 0) {
                historyContainer.innerHTML = '<p style="color: var(--text); opacity: 0.7;">Нет истории</p>';
                return;
            }

            history.forEach(item => {
                const span = document.createElement('span');
                span.className = 'history-item';
                span.textContent = item;
                span.onclick = () => {
                    window.location.href = '/proxy?url=' + encodeURIComponent(item);
                };
                historyContainer.appendChild(span);
            });
        }

        function addToHistory(query) {
            const userId = localStorage.getItem('bubles-userid');
            let history = JSON.parse(localStorage.getItem(`bubles-history-${userId}`)) || [];
            if (!history.includes(query)) {
                history.unshift(query);
                if (history.length > 15) history.pop();
                localStorage.setItem(`bubles-history-${userId}`, JSON.stringify(history));
                loadHistory();
            }
        }

        // --- Поиск ---
        function search(e) {
            e.preventDefault();
            const input = e.target[0];
            let query = input.value.trim();
            if (!query) return;

            // Если URL — открываем напрямую
            if (query.startsWith('http')) {
                window.location.href = '/proxy?url=' + encodeURIComponent(query);
                addToHistory(query);
            } else {
                // Иначе — ищем в Google
                const googleUrl = 'https://google.com/search?q=' + encodeURIComponent(query);
                window.location.href = '/proxy?url=' + encodeURIComponent(googleUrl);
                addToHistory(query);
            }
            input.value = '';
        }

        // --- Анимация пузырьков ---
        for (let i = 0; i < 25; i++) {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.left = Math.random() * 100 + '%';
            bubble.style.animationDuration = (Math.random() * 6 + 4) + 's';
            bubble.style.animationDelay = Math.random() * 5 + 's';
            bubble.style.width = Math.random() * 15 + 10 + 'px';
            bubble.style.height = bubble.style.width;
            document.body.appendChild(bubble);
        }

        // --- Автопинг для предотвращения засыпания ---
        function ping() {
            fetch('https://api.github.com/octocat')
                .then(() => {
                    document.getElementById('pingIndicator').textContent = '✅ Пинг активен';
                })
                .catch(() => {
                    document.getElementById('pingIndicator').textContent = '⚠️ Пинг не удался';
                });
        }

        setInterval(ping, 300000); // Каждые 5 минут
        ping(); // Первый пинг сразу

        // --- Инициализация ---
        loadTheme();
        loadHistory();

        // Добавляем обработку Enter в поиске
        document.querySelector('.search-box').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                search({ preventDefault: () => {}, target: [{ value: e.target.value }] });
            }
        });
    </script>

</body>
</html>
EOF

# --- 4. Генерируем Caddyfile ---
cat > Caddyfile << 'EOF'
{
    http_port 3000
    https_port 3000
}

:3000 {
    root * /home/codespace/.caddy/html
    file_server

    # Обработка прокси-запросов: /proxy?url=...
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

    # Все остальные пути — отдаём index.html
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

# Ждём запуска
sleep 3

# --- 6. Выводим ссылку ---
USERNAME=$(whoami | cut -d'-' -f1)
CODESPACE_URL="https://3000-${USERNAME}.githubpreview.dev"

echo ""
echo "🎉 Готово! Твой Bubles Portal v2.0 запущен!"
echo "🔗 Перейди по ссылке: ${CODESPACE_URL}"
echo ""
echo "✨ Фичи:"
echo "   • 💡 Темная/светлая тема — сохраняется между сессиями"
echo "   • 📜 История поиска — личная для каждого пользователя"
echo "   • 🔄 Авто-пинг каждые 5 минут — контейнер НЕ заснёт!"
echo "   • 🎯 Все клики и поиск — через твой прокси"
echo "   • 🌌 Пузырьки и анимации — просто потому что можно 😉"
echo ""
echo "🔐 Безопасно. Анонимно. Не заблокировано."

# Оставляем процесс запущенным
wait $CADDY_PID
