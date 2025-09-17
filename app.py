import re
import requests
from flask import Flask, request, Response, render_template_string
from urllib.parse import urljoin, urlparse, quote, unquote
import random
import time

app = Flask(__name__)
BASE_URL = None

# Реалистичные User-Agent (меняются рандомно)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]

POPULAR_SITES = [
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'icon': '▶️'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com', 'icon': '📷'},
    {'name': 'X (Twitter)', 'url': 'https://twitter.com', 'icon': '𝕏'},
    {'name': 'Upwork', 'url': 'https://www.upwork.com', 'icon': '💼'},
]

def make_proxy_url(target_url):
    """Создаёт проксированный URL"""
    return f'{BASE_URL}/proxy?url={quote(target_url)}'

def modify_urls_in_text(text, base_target_url):
    """Рекурсивно заменяет ВСЕ ссылки в тексте (HTML, JS, CSS)"""
    if not text:
        return text

    # Регулярное выражение для поиска URL (включая в JS и CSS)
    url_pattern = r'(["\'])(https?://[^\s"\']*?)(["\'])'
    
    def replace_url(match):
        quote_char = match.group(1)
        url = match.group(2)
        end_quote = match.group(3)
        proxied = make_proxy_url(url)
        return f'{quote_char}{proxied}{end_quote}'

    modified = re.sub(url_pattern, replace_url, text, flags=re.IGNORECASE)

    # Также заменяем незакавыченные URL (например, в location.href)
    loose_url_pattern = r'(https?://[^\s"\')}\];,]+)'
    modified = re.sub(loose_url_pattern, lambda m: make_proxy_url(m.group(1)), modified, flags=re.IGNORECASE)

    return modified

@app.before_request
def set_base_url():
    global BASE_URL
    if BASE_URL is None:
        BASE_URL = f"{request.scheme}://{request.host}"

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>bubles v2 — stealth proxy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #2c3e50, #4a69bd);
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-height: 100vh;
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px 20px;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .search-box {
                width: 100%;
                padding: 15px;
                font-size: 18px;
                border: none;
                border-radius: 50px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                text-align: center;
            }
            .sites-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                width: 100%;
                max-width: 500px;
            }
            .site-btn {
                background: rgba(255,255,255,0.15);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 50%;
                width: 80px;
                height: 80px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                color: white;
            }
            .site-btn:hover {
                background: rgba(255,255,255,0.25);
                transform: translateY(-5px);
            }
            .icon {
                font-size: 28px;
                margin-bottom: 5px;
            }
            .name {
                font-size: 12px;
                font-weight: 500;
            }
            .status {
                margin-top: 20px;
                padding: 10px;
                border-radius: 10px;
                background: rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>bubles v2</h1>
            <p>Stealth-режим: обход блокировок, подмена IP, исправление зависаний</p>
            <form action="/proxy" method="GET">
                <input type="text" name="url" class="search-box" placeholder="Введите URL (youtube.com, instagram.com...)" autocomplete="off" autofocus>
            </form>
            <div class="sites-grid">
                {% for site in sites %}
                <a href="/proxy?url={{ site.url }}" class="site-btn">
                    <div class="icon">{{ site.icon }}</div>
                    <div class="name">{{ site.name }}</div>
                </a>
                {% endfor %}
            </div>
            <div class="status">
                <strong>ℹ️ Важно:</strong> Первый запуск может занять 5-10 секунд. Не обновляйте страницу.
            </div>
        </div>
    </body>
    </html>
    ''', sites=POPULAR_SITES)

@app.route('/proxy')
def proxy():
    encoded_url = request.args.get('url', '').strip()
    if not encoded_url:
        return "URL не указан", 400

    # Декодируем URL
    try:
        target_url = unquote(encoded_url)
    except:
        target_url = encoded_url

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        # Выбираем случайный User-Agent
        user_agent = random.choice(USER_AGENTS)

        # Формируем заголовки, как от реального браузера
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': request.headers.get('Accept-Language', 'en-US,en;q=0.5'),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Referer': BASE_URL,
            'Origin': BASE_URL,
        }

        # Добавляем небольшую задержку, чтобы не выглядеть как бот
        time.sleep(random.uniform(0.1, 0.5))

        # Делаем запрос
        resp = requests.get(target_url, headers=headers, timeout=15, allow_redirects=True)

        content_type = resp.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            # Модифицируем HTML
            modified_content = modify_urls_in_text(resp.text, target_url)
            response = Response(modified_content, content_type=content_type)
        elif 'application/javascript' in content_type or 'text/css' in content_type:
            # Модифицируем JS и CSS
            modified_content = modify_urls_in_text(resp.text, target_url)
            response = Response(modified_content, content_type=content_type)
        else:
            # Бинарный контент (картинки, видео и т.д.) — просто проксируем
            response = Response(resp.content, content_type=content_type)

        # Копируем важные заголовки
        for key in ['Content-Length', 'Content-Encoding', 'Cache-Control', 'Expires', 'Pragma']:
            if key in resp.headers:
                response.headers[key] = resp.headers[key]

        return response

    except requests.exceptions.Timeout:
        return "Ошибка: Таймаут запроса. Сервер не ответил.", 504
    except requests.exceptions.RequestException as e:
        return f"Ошибка сети: {str(e)}", 502
    except Exception as e:
        return f"Внутренняя ошибка прокси: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
