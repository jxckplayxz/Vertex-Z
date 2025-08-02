from flask import Flask, request, Response, render_template_string

app = Flask(__name__)

# A simple in-memory blocklist using hashed (scrambled) IPs
blocked_hashes = set()

vertexz_loader_code = """
-- VertexZ
loadstring(game:HttpGet("https://vertex-z.onrender.com/main.lua"))()
"""

vertexz_loader_code = """
-- VertexZ main :)
loadstring(game:HttpGet("https://pandadevelopment.net/virtual/file/9638beb4d5e3ae06"))()
"""

# Your custom 404 HTML template
html_404_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>404 - Page Not Found</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --main-color: #7f5af0;
      --bg-color: #0f0f0f;
      --glass-color: rgba(255, 255, 255, 0.05);
      --text-color: #ffffff;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: linear-gradient(135deg, #141414, #1e1e1e);
      font-family: 'Segoe UI', sans-serif;
      color: var(--text-color);
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      overflow: hidden;
    }

    .container {
      background: var(--glass-color);
      backdrop-filter: blur(15px);
      border-radius: 40px;
      padding: 40px;
      width: 90%;
      max-width: 500px;
      box-shadow: 0 0 25px var(--main-color);
      border: 2px solid rgba(255, 255, 255, 0.1);
      text-align: center;
    }

    .title {
      font-size: 2.5em;
      font-weight: bold;
      margin-bottom: 10px;
    }

    .subtitle {
      font-size: 1.1em;
      margin-bottom: 25px;
      color: #aaa;
    }

    iframe {
      border: none;
      border-radius: 20px;
      width: 100%;
      height: 250px;
      box-shadow: 0 0 10px #00000080;
    }

    .squarkle-bg {
      position: absolute;
      width: 500px;
      height: 500px;
      background: radial-gradient(circle at 30% 30%, #7f5af0, transparent 70%);
      filter: blur(100px);
      z-index: -1;
    }
  </style>
</head>
<body>

  <div class="squarkle-bg"></div>

  <div class="container">
    <div class="title">404</div>
    <div class="subtitle">Page Not Found</div>
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
  title="Voidy About">
</iframe>

</body>
</html>
"""

# Optional: Simple scramble function (NOT stored IP, only hash)
def scramble_ip(ip):
    import hashlib
    return hashlib.sha256(ip.encode()).hexdigest()

@app.route("/vertexz.lua")
def vertexz_loader():
    user_ip = request.remote_addr
    scrambled = scramble_ip(user_ip)

    if scrambled in blocked_hashes:
        return render_template_string(html_404_template), 404

    return Response(vertexz_loader_code, mimetype="text/plain")

@app.route("/main.lua")
def vertexz_main():
    user_ip = request.remote_addr
    scrambled = scramble_ip(user_ip)

    if scrambled in blocked_hashes:
        return render_template_string(html_404_template), 404

    return Response(vertexz_main_code, mimetype="text/plain")

# Admin endpoint to block someone (manually for now)
@app.route("/block/<string:scrambled_ip>")
def block_ip(scrambled_ip):
    blocked_hashes.add(scrambled_ip)
    return f"Blocked {scrambled_ip}", 200

# Admin endpoint to unblock
@app.route("/unblock/<string:scrambled_ip>")
def unblock_ip(scrambled_ip):
    blocked_hashes.discard(scrambled_ip)
    return f"Unblocked {scrambled_ip}", 200

if __name__ == "__main__":
    app.run(debug=True)
 
