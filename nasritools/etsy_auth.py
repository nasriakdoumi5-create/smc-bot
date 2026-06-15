"""
NasriTools — Etsy OAuth 2.0 (PKCE)
Run once: python nasritools/etsy_auth.py
Saves token to nasritools/etsy_token.json

Supports two modes:
  - Auto (default): opens browser + local server catches the code
  - Manual: shows URL, you paste the redirect URL back
"""

import base64
import hashlib
import json
import secrets
import sys
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
REDIRECT   = "http://localhost:3003/callback"
SCOPES     = "listings_w listings_r listings_d shops_r"
TOKEN_FILE = Path(__file__).parent / "etsy_token.json"
AUTH_URL   = "https://www.etsy.com/oauth/connect"
TOKEN_URL  = "https://api.etsy.com/v3/public/oauth/token"


# ── PKCE ────────────────────────────────────────────────────────────────

def _pkce():
    verifier  = secrets.token_urlsafe(64)
    digest    = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Token exchange ───────────────────────────────────────────────────────

def _exchange(code: str, verifier: str) -> dict:
    r = requests.post(TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT,
        "code":          code,
        "code_verifier": verifier,
    })
    if not r.ok:
        print(f"\n  Etsy error: {r.text}")
        r.raise_for_status()
    data = r.json()
    data["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return data


def refresh_token(token: dict) -> dict:
    r = requests.post(TOKEN_URL, data={
        "grant_type":    "refresh_token",
        "client_id":     CLIENT_ID,
        "refresh_token": token["refresh_token"],
    })
    r.raise_for_status()
    data = r.json()
    data["expires_at"] = time.time() + data.get("expires_in", 3600) - 60
    return data


# ── Public API ───────────────────────────────────────────────────────────

def get_token() -> dict:
    if not TOKEN_FILE.exists():
        raise FileNotFoundError(
            "Not authenticated. Run: python nasritools/etsy_auth.py"
        )
    token = json.loads(TOKEN_FILE.read_text())
    if time.time() >= token.get("expires_at", 0):
        token = refresh_token(token)
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
    return token


def auth_header(token: dict) -> dict:
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key": CLIENT_ID,
    }


# ── Auto mode: local server ──────────────────────────────────────────────

_auth_code = None

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _auth_code = qs.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b"<h1 style='font-family:sans-serif;color:green'>"
            b"Done! Go back to the terminal.</h1>"
        )
    def log_message(self, *_):
        pass


def _auto_mode(params: dict, verifier: str):
    global _auth_code
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("\n  [AUTO] Opening browser...")
    webbrowser.open(url)
    print("  Waiting for Etsy redirect (120 sec)...")
    server = HTTPServer(("", 3003), _Handler)
    server.timeout = 120
    server.handle_request()
    return _auth_code


# ── Manual mode: paste redirect URL ─────────────────────────────────────

def _manual_mode(params: dict, verifier: str):
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("\n" + "─" * 60)
    print("  افتح هذا الرابط في متصفحك واضغط Allow:")
    print("─" * 60)
    print(f"\n  {url}\n")
    print("─" * 60)
    print("  بعد الموافقة، المتصفح سيذهب إلى localhost:3003")
    print("  وسيظهر خطأ 'This site can't be reached' — هذا طبيعي!")
    print("  انسخ الـ URL الكامل من شريط المتصفح وألصقه هنا:")
    print("─" * 60)
    raw = input("\n  URL: ").strip()
    qs  = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query)
    return qs.get("code", [None])[0]


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    verifier, challenge = _pkce()
    state = secrets.token_hex(16)

    params = {
        "response_type":         "code",
        "redirect_uri":          REDIRECT,
        "scope":                 SCOPES,
        "client_id":             CLIENT_ID,
        "state":                 state,
        "code_challenge":        challenge,
        "code_challenge_method": "S256",
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)

    print("\n" + "═" * 60)
    print("  NasriTools — Etsy Authorization")
    print("═" * 60)
    print("\n  خطوة 1: يفتح المتصفح تلقائياً على صفحة Etsy")
    print("  خطوة 2: اضغط 'Allow Access' في المتصفح")
    print("  خطوة 3: ارجع هنا — سيكمل البرنامج تلقائياً")
    print("\n  جارٍ فتح المتصفح...")

    webbrowser.open(url)

    print("  في انتظار موافقتك في المتصفح (دقيقتان)...\n")

    global _auth_code
    server = HTTPServer(("", 3003), _Handler)
    server.timeout = 120
    server.handle_request()

    code = _auth_code

    if not code:
        print("\n  لم يصل الرمز تلقائياً.")
        print("  انسخ فقط الرقم بعد كلمة 'code=' من شريط المتصفح والصقه هنا:")
        raw = input("  code= ").strip()
        code = raw.split("code=")[-1].split("&")[0] if "code=" in raw else raw

    if not code:
        print("\n  ✗ لم يُستلم رمز التفويض.")
        print("  السبب: التطبيق لا يزال Pending Approval على Etsy.")
        return

    print("\n  ✅ جارٍ تحويل الرمز إلى Access Token...")
    try:
        token = _exchange(code, verifier)
    except Exception as e:
        print(f"\n  ✗ فشل: {e}")
        print("  السبب: التطبيق لا يزال Pending Approval على Etsy.")
        return

    TOKEN_FILE.write_text(json.dumps(token, indent=2))
    print(f"  ✅ Token محفوظ!")
    print("  الآن شغّل: python nasritools/build_and_publish.py\n")


if __name__ == "__main__":
    main()
