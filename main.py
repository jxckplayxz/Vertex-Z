from flask import Flask, request, abort
import hashlib
import base64
import json
import os

app = Flask(__name__)

# Load banned IP hashes
BANLIST_FILE = "banlist.json"
if not os.path.exists(BANLIST_FILE):
    with open(BANLIST_FILE, "w") as f:
        json.dump([], f)

def scramble_ip(ip: str, secret: str = "secret-key"):
    return hashlib.sha256((ip + secret).encode()).hexdigest()

def load_banlist():
    with open(BANLIST_FILE, "r") as f:
        return json.load(f)

def save_banlist(banlist):
    with open(BANLIST_FILE, "w") as f:
        json.dump(banlist, f)

@app.route("/vertexz.lua")
def serve_loader():
    ip = request.remote_addr
    scrambled = scramble_ip(ip)

    # Block banned IPs
    if scrambled in load_banlist():
        return "Access Denied", 403

    # Log IP (hashed) silently
    with open("log.txt", "a") as f:
        f.write(scrambled + "\n")

    # Return the loader script
    return """
-- Vertex Z
loadstring(game:HttpGet("https://vertex-z.onrender.com/main.lua"))()
"""

@app.route("/main.lua")
def serve_loader():
    ip = request.remote_addr
    scrambled = scramble_ip(ip)

    # Block banned IPs
    if scrambled in load_banlist():
        return "Access Denied", 403

    # Log IP (hashed) silently
    with open("log.txt", "a") as f:
        f.write(scrambled + "\n")

    # Return the loader script
    return """
-- Vertex Z
loadstring(game:HttpGet("https://pandadevelopment.net/virtual/file/9638beb4d5e3ae06"))()
"""

# Admin route to ban/unban by unscrambling
@app.route("/admin/unban", methods=["POST"])
def unban_ip():
    code = request.form.get("code")
    if not code:
        return "Missing code", 400

    banlist = load_banlist()
    if code in banlist:
        banlist.remove(code)
        save_banlist(banlist)
        return f"Unbanned IP hash: {code}"
    return "Code not found", 404

@app.route("/admin/ban", methods=["POST"])
def ban_ip():
    ip = request.form.get("ip")
    if not ip:
        return "Missing IP", 400
    scrambled = scramble_ip(ip)
    banlist = load_banlist()
    if scrambled not in banlist:
        banlist.append(scrambled)
        save_banlist(banlist)
    return f"Banned {ip} (hash: {scrambled})"

