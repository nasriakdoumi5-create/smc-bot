"""
etsy_reauth.py
Re-authenticate with Etsy and save a FRESH token to ~/etsy_token.json
(the file every publish script reads). Run this when you get a
403 / invalid token error.

Run:  python etsy_reauth.py
"""
import base64, hashlib, json, os, secrets, time, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import requests

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
REDIRECT   = "http://localhost:3003/callback"
SCOPES     = ("listings_w listings_r listings_d shops_r shops_w "
              "transactions_r billing_r profile_r")
AUTH_URL   = "https://www.etsy.com/oauth/connect"
TOKEN_URL  = "https://api.etsy.com/v3/public/oauth/token"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"   # <-- home dir

_auth_code = None

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _auth_code = qs.get("code", [None])[0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"<h1 style='font-family:sans-serif;color:#16a34a'>"
                         b"Done! Go back to the terminal.</h1>")
    def log_message(self, *_): pass

def main():
    verifier  = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_hex(16)

    params = {
        "response_type": "code", "redirect_uri": REDIRECT, "scope": SCOPES,
        "client_id": CLIENT_ID, "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)

    print("=" * 60)
    print("  Etsy Re-Authentication")
    print("=" * 60)
    print("  1. Browser opens on Etsy's authorize page")
    print("  2. Click 'Allow Access'")
    print("  3. Come back here — it finishes automatically\n")
    print("  Opening browser...")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    print(f"\n  If the browser didn't open, paste this URL manually:\n  {url}\n")
    print("  In the browser: verify your identity if Etsy asks, then click")
    print("  'Allow Access'. Waiting up to 5 minutes...")

    server = HTTPServer(("", 3003), _Handler)
    server.timeout = 300          # 5 minutes — time for identity verification
    server.handle_request()
    code = _auth_code

    # Manual fallback — loop so an accidental empty Enter doesn't quit
    while not code:
        print("\n  Auto-catch didn't fire. After clicking 'Allow Access', the")
        print("  browser lands on a localhost page (may show 'can't be reached'")
        print("  — that's fine). Copy the FULL address bar URL and paste it here.")
        print("  (or press Enter on an empty line to give up)")
        raw = input("\n  URL: ").strip()
        if not raw:
            break
        if "code=" in raw:
            code = raw.split("code=")[-1].split("&")[0]
        else:
            print("  ⚠ That URL has no 'code=' in it — make sure you finished")
            print("    clicking Allow first, then copy the address it redirected to.")

    if not code:
        print("\n  ✗ No authorization code received. Run the script again.")
        return

    print("\n  Exchanging code for token...")
    r = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code", "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT, "code": code, "code_verifier": verifier,
    })
    if not r.ok:
        print(f"  ✗ Failed: {r.status_code} {r.text[:200]}")
        return
    token = r.json()
    token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
    TOKEN_FILE.write_text(json.dumps(token, indent=2))
    print(f"  ✅ Fresh token saved to {TOKEN_FILE}")
    print("\n  Now run:  python publish_premium.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
