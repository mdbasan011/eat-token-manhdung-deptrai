import re
import requests
import urllib3
from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs, unquote

# Tắt cảnh báo SSL cho sạch log
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# Mở CORS để giao diện Web (Frontend) có thể gọi vào API này
CORS(app)

def extract_eat_token_from_url(text):
    if not text: return None
    text = text.strip()
    match = re.search(r'[?&]eat=([^&\s]+)', text)
    if match: return unquote(match.group(1))
    match2 = re.search(r'^eat=([^&\s]+)', text)
    if match2: return unquote(match2.group(1))
    if len(text) > 50 and 'http' not in text and ' ' not in text:
        return text
    return None

def get_garena_data(eat_token):
    try:
        callback_url = f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
        response = requests.get(callback_url, allow_redirects=False, timeout=10, verify=False)

        if 300 <= response.status_code < 400 and "Location" in response.headers:
            redirect_url = response.headers["Location"]
            params = parse_qs(urlparse(redirect_url).query)

            token_val = params.get("access_token", [None])[0]
            acc_id = params.get("account_id", [None])[0]
            nick = params.get("nickname", [None])[0]
            reg = params.get("region", [None])[0]

            if not token_val or not acc_id:
                return {"status": "error", "message": "Data extraction failed"}
            
            open_id = "N/A"
            try:
                inspect_res = requests.get(f"https://100067.connect.garena.com/oauth/token/inspect?token={token_val}", timeout=10, verify=False)
                open_id = inspect_res.json().get("open_id", "N/A")
            except: pass

            return {
                "credit": "Telegram : @liggdzut1",
                "status": "success",
                "account_id": acc_id,
                "account_nickname": nick,
                "open_id": open_id,
                "access_token": token_val,
                "region": reg
            }
        return {"status": "error", "message": "Token expired or invalid"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/Eat", methods=["GET"])
def get_token_info():
    raw_input = request.args.get("eat_token")
    if not raw_input:
        return jsonify({"status": "error", "message": "Missing token"}), 400
    
    token = extract_eat_token_from_url(raw_input)
    if not token:
        return jsonify({"status": "error", "message": "Invalid format"}), 400

    return jsonify(get_garena_data(token))

# Vercel cần dòng này để nhận diện instance
app.debug = True
          
