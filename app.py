import re
import requests
from flask import Flask, request, redirect, render_template_string, Response
from urllib.parse import urljoin, urlparse, quote, unquote
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
BASE_URL = None

POPULAR_SITES = [
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'icon': '▶️'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com', 'icon': '📷'},
    {'name': 'X (Twitter)', 'url': 'https://twitter.com', 'icon': '𝕏'},
    {'name': 'Upwork', 'url': 'https://www.upwork.com', 'icon': '💼'},
]

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>bubles v4 — Стабильная версия</title>
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
            .error {
                background: rgba(255,0,0,0.2);
                padding: 15px;
                border-radius: 10px;
                margin: 20px;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>bubles v4</h1>
            <p>Стабильная версия: YouTube через Invidious, остальное через прокси</p>
            <form action="/proxy" method="GET">
                <input type="text" name="url" class="search-box" placeholder="Введите URL (например: youtube.com/watch?v=...)" autocomplete="off" autofocus>
            </form>
            <div class="sites-grid">
                {% for site in sites %}
                <a href="/proxy?url={{ site.url }}" class="site-btn">
                    <div class="icon">{{ site.icon }}</div>
                    <div class="name">{{ site.name }}</div>
                </a>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    ''', sites=POPULAR_SITES)

@app.before_request
def set_base_url():
    global BASE_URL
    if BASE_URL is None:
        BASE_URL = f"{request.scheme}://{request.host}"

@app.route('/proxy')
def proxy():
    try:
        url = request.args.get('url', '').strip()
        if not url:
            return "❌ Пожалуйста, укажите URL", 400

        # Добавляем https:// если нужно
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Обработка YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            try:
                # Извлекаем video ID
                video_id = None
                if 'v=' in url:
                    video_id = url.split('v=')[1].split('&')[0]
                elif 'youtu.be/' in url:
                    video_id = url.split('youtu.be/')[1].split('?')[0]

                if video_id:
                    invidious_url = f"https://invidious.io/watch?v={video_id}"
                    logger.info(f"✅ Перенаправление на Invidious: {invidious_url}")
                    return redirect(invidious_url)
                else:
                    return "❌ Не удалось извлечь ID видео из URL", 400
            except Exception as e:
                logger.error(f"Ошибка обработки YouTube URL: {str(e)}")
                return f"❌ Ошибка YouTube: {str(e)}", 500

        # Прокси для остальных сайтов
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': request.headers.get('Accept-Language', 'en-US,en;q=0.5'),
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            logger.info(f"🌐 Запрос к: {url}")
            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

            content_type = resp.headers.get('Content-Type', '')

            if 'text/html' in content_type:
                # Простая подмена ссылок
                modified_content = resp.text.replace('href="/', f'href="{url}/')
                modified_content = modified_content.replace('src="/', f'src="{url}/')
                response = Response(modified_content, content_type=content_type)
            else:
                response = Response(resp.content, content_type=content_type)

            return response

        except requests.exceptions.Timeout:
            return "⏰ Таймаут: Сервер не ответил за 15 секунд", 504
        except requests.exceptions.ConnectionError:
            return "🔌 Ошибка подключения к целевому серверу", 502
        except Exception as e:
            logger.error(f"Ошибка прокси: {str(e)}")
            return f"❌ Ошибка: {str(e)}", 500

    except Exception as e:
        logger.error(f"Необработанная ошибка: {str(e)}")
        return "❌ Внутренняя ошибка сервера. Пожалуйста, попробуйте позже.", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
