from flask import Flask, request, session, redirect, url_for, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Upload config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
ks_code = '''loadstring(game:HttpGet("https://voidy-script.neocities.org/idk"))()'''
script_code = '''loadstring(game:HttpGet("https://voidy-script.neocities.org/test"))()'''
za_code = '''loadstring(game:HttpGet("https://raw.githubusercontent.com/jxckplayxz/cool/refs/heads/main/aaa"))() -- btw this is just the loader so its useless :)'''
error_code = '''Bro why you tryna see source you a skid or sum? oh yea btw join our server --> https://discord.gg/zMPJxeMMrK'''

# HTML templates
home_page = '''...'''  # keep your current home_page string
locked_page = '''...'''  # keep your current locked_page string

def is_executor():
    user_agent = request.headers.get('User-Agent', '').lower()
    executor_keywords = ['synapse', 'roblox', 'krnl', 'fluxus', 'executor', 'delta']
    return any(exec in user_agent for exec in executor_keywords)

@app.route('/')
def index():
    script_code = f'loadstring(game:HttpGet("https://{request.host}/script?key=skidder"))()'
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
            <pre id="scriptBox">{script_code}</pre>
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


executed_keys = {}

@app.route('/track', methods=['POST'])
def track():
    key = request.form.get("key", "")
    executed_keys[key] = time.time()
    return "Tracked", 200

@app.route('/raw')
def raw():
    key = request.args.get("key", "")
    last_exec = executed_keys.get(key)

    if last_exec and time.time() - last_exec < 10:
        return ks_code, 200, {'Content-Type': 'text/plain'}
    else:
        return error_code, 200, {'Content-Type': 'text/plain'}

@app.route('/error')
def error():
    if is_executor() and request.args.get("key") == "skidder":
        return za_code, 200, {'Content-Type': 'text/plain'}
    return "Error page has been deleted or moved", 403

@app.route('/main')
def main():
    if is_executor() and request.args.get("key") == "skidder":
        return main_code, 200, {'Content-Type': 'text/plain'}
    return "Unauthorized", 403

    
@app.route('/script')
def script():
    if is_executor() and request.args.get("key") == "skidder":
        return script_code, 200, {'Content-Type': 'text/plain'}
    return "Error page has been deleted or moved", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20039)
