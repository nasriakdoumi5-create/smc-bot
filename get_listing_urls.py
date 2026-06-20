import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

def get_price(l):
    p = l.get("price", {})
    return p.get("amount", 0) / max(p.get("divisor", 100), 1)

token = get_token()
r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active", headers=auth_headers(token), params={"limit": 100})
listings = r.json().get("results", [])

print(f"\n{'='*70}")
print(f"  NasriTools — All Listings")
print(f"{'='*70}\n")
for l in sorted(listings, key=lambda x: x["title"]):
    lid   = l["listing_id"]
    title = l["title"][:45]
    price = get_price(l)
    url   = f"https://www.etsy.com/listing/{lid}"
    print(f"€{price:>6.2f}  {title}")
    print(f"        {url}\n")
