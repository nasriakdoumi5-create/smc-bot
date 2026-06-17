"""
Re-authorize Etsy with shops_w scope
Run: python reauth.py
"""
import json, os, hashlib, base64, secrets, requests, webbrowser
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
REDIRECT   = "http://localhost:3003/callback"
SCOPES     = "listings_r listings_w listings_d shops_r shops_w transactions_r"

# PKCE
verifier  = secrets.token_urlsafe(64)
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b"=").decode()
state = secrets.token_urlsafe(16)

auth_url = "https://www.etsy.com/oauth/connect?" + urlencode({
    "response_type":         "code",
    "client_id":             CLIENT_ID,
    "redirect_uri":          REDIRECT,
    "scope":                 SCOPES,
    "state":                 state,
    "code_challenge":        challenge,
    "code_challenge_method": "S256",
})

code_holder = [None]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "/callback" in self.path:
            qs = parse_qs(urlparse(self.path).query)
            code_holder[0] = qs.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Auth complete! You can close this tab.</h2>")
    def log_message(self, *a): pass

server = HTTPServer(("", 3003), Handler)
t = threading.Thread(target=server.handle_request)
t.start()

print("\n" + "="*60)
print("  NasriTools - Re-Authorization (shops_w scope)")
print("="*60)
print("\nOpening browser... If it doesn't open, paste this URL:")
print("\n" + auth_url + "\n")

try:
    webbrowser.open(auth_url)
except Exception:
    pass

print("Waiting for authorization...")
t.join(timeout=120)
server.server_close()

code = code_holder[0]
if not code:
    print("ERROR: No code received. Run again and complete in browser.")
    exit(1)

print("Code received! Exchanging for token...")
r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
    "grant_type":    "authorization_code",
    "client_id":     CLIENT_ID,
    "redirect_uri":  REDIRECT,
    "code":          code,
    "code_verifier": verifier,
})

if not r.ok:
    print("Token exchange failed: " + r.text)
    exit(1)

import time
token = r.json()
token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
TOKEN_FILE.write_text(json.dumps(token, indent=2))

print("\nToken saved to: " + str(TOKEN_FILE))
print("Scopes: " + token.get("scope", "?"))
print("\nNow run: python setup_shop.py")
