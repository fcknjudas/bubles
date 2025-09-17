import re
import requests
from flask import Flask, request, Response, render_template_string
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# Базовый URL вашего прокси (будет определён автоматически)
BASE_URL = None

# Популярные сайты
POPULAR_SITES = [
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'icon': '▶️'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com', 'icon': '📷'},
    {'name': 'X (Twitter)', 'url': 'https://twitter.com', 'icon': '𝕏'},
    {'name': 'Upwork', 'url': 'https://www.upwork.com', 'icon': '💼'},
]

def make_proxy_url(target_url):
    """Создаёт URL для проксирования через наш сервер"""
    return f'{BASE_URL}/proxy?url={target_url}'

def modify_html_content(html, target_base_url):
    """Модифицирует HTML: заменяет все ссылки на проксированные"""
    # Заменяем ссылки в href и src
    html = re.sub(r'(href|src)\\s*=\\s*["\']([^"\']*?)["\']',
                  lambda m: f'{m.group(1)}="{make_proxy_url(urljoin(target_base_url, m.group(2)))}"'
                  if not m.group(2).startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:'))
                  else f'{m.group(1)}="{m.group(2)}"',
                  html, flags=re.IGNORECASE)

    # Заменяем полные URL на проксированные
    html = re.sub(r'(https?://[^\s"\'<>]+)',
                  lambda m: make_proxy_url(m.group(1)),
                  html)

    return html

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
        <title>bubles — прокси-шлюз</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #6e8efb, #a777e3);
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
                background: rgba(255,255,255,0.2);
                backdrop-filter: blur(10px);
                border: none;
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
                background: rgba(255,255,255,0.3);
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>bubles</h1>
            <form action="/proxy" method="GET">
                <input type="text" name="url" class="search-box" placeholder="Введите URL сайта..." autocomplete="off" autofocus>
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

@app.route('/proxy')
def proxy():
    target_url = request.args.get('url', '').strip()
    if not target_url:
        return "URL не указан", 400

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    try:
        # Делаем запрос от имени сервера
        headers = {
            'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        resp = requests.get(target_url, headers=headers, timeout=10)

        # Если это HTML — модифицируем ссылки
        if 'text/html' in resp.headers.get('Content-Type', ''):
            modified_content = modify_html_content(resp.text, target_url)
            return Response(modified_content, content_type=resp.headers.get('Content-Type'))

        # Для остального контента — просто проксируем
        return Response(resp.content, content_type=resp.headers.get('Content-Type'))

    except Exception as e:
        return f"Ошибка прокси: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
