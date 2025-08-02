from flask import Flask, request, abort
import time, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Script content
SCRIPT_PAYLOAD = '''loadstring(game:HttpGet("https://vertex-z.onrender.com/main?key=skidder", true))()'''
PRIVATE_SCRIPT = '''loadstring(game:HttpGet("https://pandadevelopment.net/virtual/file/9638beb4d5e3ae06"))()'''
USED_KEYS = {}
RATE_LIMIT = {}  # IP or key : last access timestamp
ALLOWED_KEYS = {"skidder"}  # Only valid keys

# Security config
ANTI_SPAM_SECONDS = 5
CUSTOM_HEADER = "X-Executor-Auth"
EXPECTED_HEADER_VALUE = "VertexZClient"

# Executor validation
def is_valid_executor():
    ua = request.headers.get("User-Agent", "").lower()
    header = request.headers.get(CUSTOM_HEADER, "")
    if any(x in ua for x in ["synapse", "krnl", "fluxus", "delta", "executor", "Delta"]):
        return header == EXPECTED_HEADER_VALUE
    return False

# Rate limit logic
def rate_limited(key_or_ip):
    now = time.time()
    last = RATE_LIMIT.get(key_or_ip, 0)
    if now - last < ANTI_SPAM_SECONDS:
        return True
    RATE_LIMIT[key_or_ip] = now
    return False

# Homepage - shows script payload
@app.route("/")
def index():
    key = "skidder"
    host = request.host
    script = SCRIPT_PAYLOAD.format(host=host, key=key)
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Voidy X Script</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
                font-family: 'Segoe UI', sans-serif;
                color: #ffffff;
                margin: 0;
                padding: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                background: #111;
                border-radius: 40% 60% 60% 40% / 50% 30% 70% 50%;
                padding: 40px;
                max-width: 700px;
                width: 90%;
                box-shadow: 0 0 30px rgba(0, 225, 255, 0.4);
                border: 2px solid rgba(0, 225, 255, 0.3);
                animation: float 3s ease-in-out infinite;
                text-align: center;
            }}
            @keyframes float {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            h1 {{
                margin-top: 0;
                font-size: 28px;
                color: #00d4ff;
            }}
            pre {{
                background: #1d1d1d;
                padding: 15px;
                border-radius: 12px;
                overflow-x: auto;
                font-size: 14px;
                margin-top: 20px;
                color: #00ffe7;
                border: 1px solid #00d4ff44;
            }}
            button {{
                margin-top: 20px;
                background: #00d4ff;
                color: #000;
                font-weight: bold;
                padding: 10px 25px;
                font-size: 14px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: transform 0.2s, background 0.2s;
            }}
            button:hover {{
                background: #00bde0;
                transform: scale(1.05);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚡ Vertex Z | Script</h1>
            <pre id="scriptBox">{script}</pre>
            <button onclick="copyCode()">📋 Copy Script</button>
        </div>
        <script>
            function copyCode() {{
                const code = document.getElementById('scriptBox').innerText;
                navigator.clipboard.writeText(code).then(() => {{
                    alert('✅ Script copied to clipboard!');
                }});
            }}
        </script>
    </body>
    </html>
    '''

# Script endpoint
@app.route("/main")
def main():
    key = request.args.get("key", "")
    ip = request.remote_addr

    if not is_valid_executor():
        abort(403)

    if key not in ALLOWED_KEYS or key in USED_KEYS:
        abort(403)

    if rate_limited(ip):
        abort(429)

    USED_KEYS[key] = time.time()

    return PRIVATE_SCRIPT, 200, {
        'Content-Type': 'text/plain',
        'Cache-Control': 'no-store'
    }

# Custom error pages
@app.errorhandler(403)
def forbidden(e):
    return "-- Access Denied | Join our Discord: https://discord.com/invite/hCTCQwPKd3", 403

@app.errorhandler(429)
def ratelimit(e):
    return "-- Slow down! Too many requests.", 429

# Launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
