from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

POPULAR_SITES = [
    {'name': 'YouTube', 'url': 'https://www.youtube.com', 'icon': '▶️'},
    {'name': 'Instagram', 'url': 'https://www.instagram.com', 'icon': '📷'},
    {'name': 'X (Twitter)', 'url': 'https://twitter.com', 'icon': '𝕏'},
    {'name': 'Upwork', 'url': 'https://www.upwork.com', 'icon': '💼'},
    {'name': 'TikTok', 'url': 'https://www.tiktok.com', 'icon': '🎵'},
    {'name': 'Reddit', 'url': 'https://www.reddit.com', 'icon': '🔺'},
]

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>bubles — универсальный шлюз</title>
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
            <form action="/go" method="GET">
                <input type="text" name="url" class="search-box" placeholder="Введите URL или название сайта..." autocomplete="off" autofocus>
            </form>
            <div class="sites-grid">
                {% for site in sites %}
                <a href="/go?url={{ site.url }}" class="site-btn">
                    <div class="icon">{{ site.icon }}</div>
                    <div class="name">{{ site.name }}</div>
                </a>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    ''', sites=POPULAR_SITES)

@app.route('/go')
def go():
    url = request.args.get('url', '').strip()
    if not url:
        return redirect('/')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return redirect(url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # ← ВАЖНО: Render использует порт 10000