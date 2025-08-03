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

# Main executor code and key system code
main_code = '''loadstring(game:HttpGet("https://voidy-script.neocities.org/JujutsuInfinite"))()'''
ks_code = '''loadstring(game:HttpGet("https://vertex-z.onrender.com/main?key=skidder"))()'''
za_code = '''loadstring(game:HttpGet("https://voidy-script.neocities.org/script"))() -- btw this is just the loader so its useless :)'''
error_code = '''Bro why you tryna see source you a skid or sum? oh yea btw join our server --> https://discord.gg/zMPJxeMMrK'''

# HTML templates
home_page = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>404 - Page Not Found</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --main-color: #7f5af0;
      --bg-color: #0f0f0f;
      --glass-color: rgba(255, 255, 255, 0.07);
      --text-color: #ffffff;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: linear-gradient(135deg, #0f0f0f, #1c1c1c);
      font-family: 'Segoe UI', sans-serif;
      color: var(--text-color);
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      background: var(--glass-color);
      backdrop-filter: blur(30px) saturate(180%);
      -webkit-backdrop-filter: blur(30px) saturate(180%);
      border-radius: 40px;
      padding: 40px;
      width: 95%;
      max-width: 600px;
      box-shadow: 0 0 30px rgba(127, 90, 240, 0.4), inset 0 0 20px rgba(255, 255, 255, 0.03);
      border: 1.5px solid rgba(255, 255, 255, 0.15);
      text-align: center;
      overflow-y: auto;
      max-height: 90vh;
      animation: glowIn 1s ease-out;
    }

    .title {
      font-size: 3em;
      font-weight: bold;
      margin-bottom: 10px;
      text-shadow: 0 0 10px var(--main-color);
    }

    .subtitle {
      font-size: 1.2em;
      margin-bottom: 25px;
      color: #bbb;
    }

    .section {
      text-align: left;
      margin-top: 20px;
      background: rgba(255, 255, 255, 0.06);
      padding: 15px 20px;
      border-radius: 20px;
      box-shadow: inset 0 0 10px rgba(255,255,255,0.05), 0 0 8px rgba(127, 90, 240, 0.1);
    }

    .section h2 {
      font-size: 1.3em;
      margin-bottom: 10px;
      color: #ffffffcc;
      text-shadow: 0 0 5px rgba(127, 90, 240, 0.3);
    }

    .section ul {
      list-style: none;
      padding-left: 0;
    }

    .section ul li {
      margin: 6px 0;
      font-size: 1em;
    }

    .section a {
      text-decoration: none;
      color: var(--main-color);
      font-weight: bold;
      transition: color 0.3s ease;
    }

    .section a:hover {
      color: #a88bff;
      text-shadow: 0 0 6px #7f5af0;
    }

    iframe {
      border: none;
      border-radius: 20px;
      width: 100%;
      height: 200px;
      box-shadow: 0 0 12px #00000080;
      margin-top: 25px;
    }

    .squarkle-bg {
      position: absolute;
      width: 600px;
      height: 600px;
      background: radial-gradient(circle at 30% 30%, #7f5af0, transparent 70%);
      filter: blur(120px);
      z-index: -1;
    }

    @keyframes glowIn {
      from {
        opacity: 0;
        transform: scale(0.97);
        box-shadow: 0 0 0 transparent;
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }
  </style>
</head>
<body>

  <div class="squarkle-bg"></div>

  <div class="container">
    <div class="title">Vertex Z</div>
    <div class="subtitle">Vertex Z #1 steal a brainrot Script</div>

    <div class="section">
      <h2>🚀 Features</h2>
      <ul>
        <li>⚡ Speed Boost</li>
        <li>🦘 Jump Boost</li>
        <li>🌀 Multi-Jump</li>
        <li>🎯 And more...</li>
      </ul>
    </div>

    <div class="section">
      <h2>🎮 Supported Game</h2>
      <ul>
        <li>🔹 Steal a brainrot</li>
        <li>🔹 More to come</li>
      </ul>
    </div>

    <div class="section">
      <h2>📜 Get Script</h2>
      <ul>
        <li>🔗 <a href="https://vertex-z.onrender.com/script" target="_blank">Script</a></li>
      </ul>
    </div>

    <iframe src="https://voidy-script.neocities.org/about"></iframe>
  </div>

  <iframe 
    src=".." 
    style="
      position: fixed;
      bottom: 0px;
      right: 0px;
      width: 0px;
      height: 0px;
      border: none;
      border-radius: 0px;
      box-shadow: 0 0 0px rgba(0,0,0,0.0);
      z-index: 0;
      backdrop-filter: blur(6px);
      overflow: hidden;
    "
    title="Vertex z About">
  </iframe>

</body>
</html>
'''
 
locked_page = '''...'''  # keep your current locked_page string

@app.route('/')
def home():
    return render_template_string(home_page)

@app.route('/verify', methods=['POST'])
def verify():
    key = request.form.get('key')
    if key == "voidy-skid-off":
        session['verified'] = True
        return redirect('/212')
    return redirect('/')

def is_executor():
    user_agent = request.headers.get('User-Agent', '').lower()
    executor_keywords = ['synapse', 'roblox', 'krnl', 'fluxus', 'executor', 'delta']
    return any(exec in user_agent for exec in executor_keywords)

@app.route('/212')
def hidden():
    query_key = request.args.get("key", "")
    is_exec = is_executor()
    verified = session.get('verified')

    if not verified and not is_exec:
        return redirect('/')

    if is_exec:
        if query_key == "skidder":
            return render_template_string(locked_page, code=main_code, can_see_code=True)
        else:
            return render_template_string(locked_page, code="", can_see_code=False)

    return render_template_string(locked_page, code="", can_see_code=False)

@app.route('/script')
def execute():
    script_code = f'loadstring(game:HttpGet("https://{request.host}/error?key=skidder"))()'
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Voidy X Script</title>
    <meta charset="UTF-8">
    <style>
        body {
            background: radial-gradient(circle at center, #0f0f0f 0%, #1a1a1a 100%);
            color: white;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .container {
            background: #121212;
            border-radius: 20px;
            padding: 40px 50px;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.15);
            max-width: 750px;
            width: 90%;
            text-align: center;
        }

        .title {
            font-size: 28px;
            margin-bottom: 20px;
            color: #00d4ff;
            font-weight: bold;
        }

        pre {
            background: #1e1e1e;
            padding: 20px;
            border-radius: 12px;
            overflow-x: auto;
            font-size: 14px;
            margin-bottom: 20px;
            border: 1px solid #2a2a2a;
        }

        .btn {
            display: inline-block;
            margin: 8px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
            color: white;
            background: #00d4ff;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background 0.2s ease;
            text-decoration: none;
        }

        .btn:hover {
            background: #00aacc;
        }

        .discord-btn {
            background: #5865F2;
        }

        .discord-btn:hover {
            background: #4752c4;
        }

        .reviews-section {
            margin-top: 30px;
            text-align: left;
        }

        .reviews-title {
            font-size: 22px;
            color: #00d4ff;
            margin-bottom: 15px;
            font-weight: 600;
            text-align: center;
        }

        .review-item {
            background-color: #1e1e1e;
            border: 1px solid #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }

        .review-user {
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 5px;
        }

        .review-text {
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="title">⚡ Vertex Z Script</div>
        <pre id="scriptBox">''' + script_code + '''</pre>
        <button class="btn" onclick="copyCode()">Copy Script</button>
        <a class="btn discord-btn" href="https://discord.gg/hCTCQwPKd3" target="_blank">Join Discord</a>

        <div class="reviews-section">
            <div class="reviews-title">💬 User Reviews</div>
            <div class="review-list" id="reviewContainer">
            </div>
        </div>
    </div>

    <script>
        function copyCode() {
            const code = document.getElementById('scriptBox').innerText;
            navigator.clipboard.writeText(code).then(() => {
                alert('Script copied to clipboard!');
            });
        }

        const reviews = [
            { user: "Lilbabby87", text: "10/10 best script known to man and it get better and better every update" },
            { user: "manman01901", text: "1of the best script I ever used!" },
            { user: "elitelyex", text: "really recommend, i like to play music while playing." },
            { user: "thegrinch04616", text: "The script is insanely good in sab for a free script! THERES also other games that i have yet to try." },
        ];

        const container = document.getElementById("reviewContainer");
        reviews.forEach(review => {
            const div = document.createElement("div");
            div.className = "review-item";

            const user = document.createElement("div");
            user.className = "review-user";
            user.innerText = review.user;

            const text = document.createElement("div");
            text.className = "review-text";
            text.innerText = review.text;

            div.appendChild(user);
            div.appendChild(text);
            container.appendChild(div);
        });
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
