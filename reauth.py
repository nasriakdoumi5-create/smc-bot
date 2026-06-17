"""
Re-authorize Etsy with shops_w scope
Run: python reauth.py
"""
import json, os, hashlib, base64, secrets, requests, webbrowser, time
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
REDIRECT   = "http://localhost:3003/callback"
SCOPES     = "listings_r listings_w listings_d shops_r shops_w transactions_r"

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
        qs = parse_qs(urlparse(self.path).query)
        code = qs.get("code", [None])[0]
        if code:
            code_holder[0] = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Done! Return to PowerShell.</h1>")
        else:
            self.send_response(204)
            self.end_headers()
    def log_message(self, *a): pass

print("\n" + "=" * 60)
print("  NasriTools - Re-Authorization (shops_w)")
print("=" * 60)
print("\nOpening browser... Grant access then return here.\n")

webbrowser.open(auth_url)

server = HTTPServer(("", 3003), Handler)
server.timeout = 5
deadline = time.time() + 120

print("Waiting for browser callback (2 min timeout)...")
while code_holder[0] is None and time.time() < deadline:
    server.handle_request()

server.server_close()

code = code_holder[0]
if not code:
    print("Timed out. Run again.")
    exit(1)

print("Code received! Exchanging...")
r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
    "grant_type":    "authorization_code",
    "client_id":     CLIENT_ID,
    "redirect_uri":  REDIRECT,
    "code":          code,
    "code_verifier": verifier,
})

if not r.ok:
    print("Failed: " + r.text)
    exit(1)

token = r.json()
token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
TOKEN_FILE.write_text(json.dumps(token, indent=2))
print("\nToken saved. Scopes: " + token.get("scope", "?"))
print("Run: python setup_shop.py")
