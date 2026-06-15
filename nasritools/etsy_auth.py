"""
NasriTools — Etsy OAuth 2.0 (PKCE)
Run once: python nasritools/etsy_auth.py
Saves token to nasritools/etsy_token.json
"""

import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

CLIENT_ID   = "pluc0garrgcjzhim0hawxf0k"
REDIRECT    = "http://localhost:3003/callback"
SCOPES      = "listings_w listings_r listings_d shops_r"
TOKEN_FILE  = Path(__file__).parent / "etsy_token.json"
AUTH_URL    = "https://www.etsy.com/oauth/connect"
TOKEN_URL   = "https://api.etsy.com/v3/public/oauth/token"


# ── PKCE helpers ────────────────────────────────────────────────────────

def _pkce():
    verifier = secrets.token_urlsafe(64)
    digest   = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


# ── Local callback server ────────────────────────────────────────────────

_auth_code = None

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _auth_code = qs.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h1>Done! Return to terminal.</h1>")

    def log_message(self, *_):
        pass


# ── Token exchange ───────────────────────────────────────────────────────

def _exchange(code: str, verifier: str) -> dict:
    r = requests.post(TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT,
        "code":          code,
        "code_verifier": verifier,
    })
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
    """Load saved token, refreshing if expired. Raise if not authorized."""
    if not TOKEN_FILE.exists():
        raise FileNotFoundError("Not authenticated. Run: python nasritools/etsy_auth.py")
    token = json.loads(TOKEN_FILE.read_text())
    if time.time() >= token.get("expires_at", 0):
        token = refresh_token(token)
        TOKEN_FILE.write_text(json.dumps(token, indent=2))
    return token


def auth_header(token: dict) -> dict:
    return {"Authorization": f"Bearer {token['access_token']}",
            "x-api-key": CLIENT_ID}


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    global _auth_code

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

    print("\n" + "═" * 55)
    print("  NasriTools — Etsy Authorization")
    print("═" * 55)
    print("\n  خطوة 1: يفتح متصفحك تلقائياً على صفحة Etsy")
    print("  خطوة 2: اضغط 'Allow Access'")
    print("  خطوة 3: سيعود المتصفح لـ localhost — العملية انتهت\n")

    webbrowser.open(url)

    print("  انتظر...")
    server = HTTPServer(("", 3003), _Handler)
    server.timeout = 120
    server.handle_request()

    if not _auth_code:
        print("  ✗ لم يصل رمز التفويض. حاول مجدداً.")
        return

    print("  ✅ تم الحصول على الرمز — جارٍ تبادله بـ token...")
    token = _exchange(_auth_code, verifier)
    TOKEN_FILE.write_text(json.dumps(token, indent=2))
    print(f"  ✅ Token محفوظ في: {TOKEN_FILE}")
    print("  يمكنك الآن تشغيل: python nasritools/etsy_publisher.py\n")


if __name__ == "__main__":
    main()
