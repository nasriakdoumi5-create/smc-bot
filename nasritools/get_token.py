"""
شغّل هذا على جهازك:
    python get_token.py

سيفتح المتصفح → اضغط Allow → يُطبع الـ token تلقائياً
"""
import base64, hashlib, json, secrets, time, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

CLIENT_ID = "pluc0garrgcjzhim0hawxf0k"
REDIRECT  = "http://localhost:3003/callback"
SCOPES    = "listings_w listings_r listings_d shops_r"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"

# ── PKCE ─────────────────────────────────────────────────────────────
verifier  = secrets.token_urlsafe(64)
digest    = hashlib.sha256(verifier.encode()).digest()
challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
state     = secrets.token_hex(16)

params = {
    "response_type":         "code",
    "redirect_uri":          REDIRECT,
    "scope":                 SCOPES,
    "client_id":             CLIENT_ID,
    "state":                 state,
    "code_challenge":        challenge,
    "code_challenge_method": "S256",
}
auth_url = "https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode(params)

# ── Local server to catch the redirect ───────────────────────────────
_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _code
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _code = qs.get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h1 style='font-family:sans-serif;color:green;padding:40px'>"
                         b"Done! Return to the terminal.</h1>")
    def log_message(self, *_): pass

print("\n" + "="*50)
print("  NasriTools — Etsy Auth")
print("="*50)
print("\n  1. المتصفح سيفتح الآن...")
print("  2. اضغط Allow Access")
print("  3. ارجع هنا")
print()

webbrowser.open(auth_url)

server = HTTPServer(("", 3003), Handler)
server.timeout = 120
print("  في انتظار الموافقة (دقيقتان)...")
server.handle_request()

if not _code:
    print("\n  لم يصل الرمز. انسخ قيمة code= من شريط المتصفح:")
    raw = input("  code= ").strip()
    _code = raw.split("code=")[-1].split("&")[0] if "code=" in raw else raw

# ── Exchange code for token ───────────────────────────────────────────
print("\n  جارٍ تحويل الرمز إلى Token...")
data = urllib.parse.urlencode({
    "grant_type":    "authorization_code",
    "client_id":     CLIENT_ID,
    "redirect_uri":  REDIRECT,
    "code":          _code,
    "code_verifier": verifier,
}).encode()

req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
with urllib.request.urlopen(req) as r:
    token = json.loads(r.read())

token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60

print("\n" + "="*50)
print("  ✅ نجح! انسخ هذا النص كاملاً وأرسله:")
print("="*50)
print(json.dumps(token, indent=2))
print("="*50)
