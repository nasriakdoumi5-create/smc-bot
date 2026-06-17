"""
Re-authorize Etsy - Manual code entry (no local server needed)
Run: python reauth2.py
"""
import json, os, hashlib, base64, secrets, requests, time
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs

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

print("\n" + "="*60)
print("  NasriTools - Re-Authorization")
print("="*60)
print("\n1. Open this URL in your browser:\n")
print(auth_url)
print("\n2. Click 'Grant access'")
print("\n3. You'll see an error page (ERR_CONNECTION_REFUSED) - that's OK!")
print("   Copy the FULL URL from the browser address bar and paste it here.")
print("\n" + "-"*60)
full_url = input("Paste the redirect URL here: ").strip()

qs = parse_qs(urlparse(full_url).query)
code = qs.get("code", [None])[0]
if not code:
    print("ERROR: No code found in URL. Make sure you copied the full URL.")
    exit(1)

print("\nExchanging code for token...")
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

token = r.json()
token["expires_at"] = time.time() + token.get("expires_in", 3600) - 60
TOKEN_FILE.write_text(json.dumps(token, indent=2))

print("\nToken saved!")
print("Scopes: " + token.get("scope", "?"))
print("\nNow run: python setup_shop.py")
