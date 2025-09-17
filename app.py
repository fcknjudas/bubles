from flask import Flask, request, redirect, render_template_string, Response
import requests
import re
from urllib.parse import urljoin, urlparse, quote, unquote

app = Flask(__name__)

# Список популярных сайтов
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
        <title>bubles v3 — Invidious + proxy</title>
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
            <h1>bubles v3</h1>
            <p>Использует Invidious для YouTube и прокси для других сайтов</p>
            <form action="/proxy" method="GET">
                <input type="text" name="url" class="search-box" placeholder="Введите URL..." autocomplete="off" autofocus>
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
    url = request.args.get('url', '').strip()
    if not url:
        return "URL не указан", 400

    if url.startswith('https://www.youtube.com'):
        # Для YouTube используем Invidious
        invidious_url = f"https://invidious.io/watch?v={url.split('v=')[1]}"
        return redirect(invidious_url)
    else:
        # Для остальных сайтов — прокси
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Referer': request.url,
                'Origin': request.url,
            }

            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)

            if 'text/html' in resp.headers.get('Content-Type', ''):
                # Модифицируем HTML
                modified_content = re.sub(r'(href|src)\\s*=\\s*["\']([^"\']*?)["\']',
                                          lambda m: f'{m.group(1)}="{urljoin(request.url, m.group(2))}"'
                                          if not m.group(2).startswith(('http://', 'https://'))
                                          else f'{m.group(1)}="{m.group(2)}"',
                                          resp.text, flags=re.IGNORECASE)

                response = Response(modified_content, content_type='text/html')
            else:
                response = Response(resp.content, content_type=resp.headers.get('Content-Type'))

            for key in ['Content-Length', 'Content-Encoding']:
                if key in resp.headers:
                    response.headers[key] = resp.headers[key]

            return response

        except Exception as e:
            return f"Ошибка: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
