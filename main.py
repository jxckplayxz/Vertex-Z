from flask import Flask, request, abort
import time, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Configuration ---
SCRIPT_PAYLOAD = '''loadstring(game:HttpGet("https://{host}/main?key=skidder"))()'''
PRIVATE_SCRIPT = '''loadstring(game:HttpGet("https://pandadevelopment.net/virtual/file/9638beb4d5e3ae06"))()'''
ALLOWED_KEYS = {"skidder"}
USED_KEYS = {}
RATE_LIMIT = {}
ANTI_SPAM_SECONDS = 5

# --- Rate Limit Check ---
def rate_limited(ip):
    now = time.time()
    last = RATE_LIMIT.get(ip, 0)
    if now - last < ANTI_SPAM_SECONDS:
        return True
    RATE_LIMIT[ip] = now
    return False

# --- Homepage ---
@app.route("/")
def index():
    script = SCRIPT_PAYLOAD.format(host=request.host)
    return f'''
    <html>
    <head>
        <title>Vertex Z | Script</title>
        <style>
            body {{
                background: #0f0f0f;
                font-family: sans-serif;
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .box {{
                background: #1a1a1a;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                border: 2px solid #00d4ff;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
            }}
            pre {{
                background: #111;
                padding: 10px;
                border-radius: 10px;
                color: #00ffe7;
                overflow-x: auto;
            }}
            button {{
                margin-top: 15px;
                padding: 10px 20px;
                background: #00d4ff;
                color: black;
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>⚡ Vertex Z – Get Your Script</h2>
            <pre id="code">{script}</pre>
            <button onclick="copyCode()">📋 Copy Script</button>
        </div>
        <script>
            function copyCode() {{
                navigator.clipboard.writeText(document.getElementById("code").innerText);
                alert("✅ Script copied!");
            }}
        </script>
    </body>
    </html>
    '''

# --- Script Endpoint ---
@app.route("/main")
def main():
    key = request.args.get("key", "")
    ip = request.remote_addr

    if key not in ALLOWED_KEYS or key in USED_KEYS:
        abort(403)

    if rate_limited(ip):
        abort(429)

    USED_KEYS[key] = time.time()
    return PRIVATE_SCRIPT, 200, {
        'Content-Type': 'text/plain',
        'Cache-Control': 'no-store'
    }

# --- Errors ---
@app.errorhandler(403)
def forbidden(e):
    return "-- Access Denied | Join our Discord: https://discord.gg/hCTCQwPKd3", 403

@app.errorhandler(429)
def ratelimit(e):
    return "-- Too many requests. Please slow down.", 429

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
