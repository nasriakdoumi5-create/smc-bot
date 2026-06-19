"""List all active listings with IDs and titles."""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

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
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

token = get_token()
listings, offset = [], 0
while True:
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
        headers=auth_headers(token),
        params={"limit": 100, "offset": offset},
        timeout=30,
    )
    batch = r.json().get("results", [])
    listings.extend(batch)
    if len(batch) < 100: break
    offset += 100

listings.sort(key=lambda x: x.get("price", {}).get("amount", 0), reverse=True)

print(f"\nActive listings: {len(listings)}\n")
for i, l in enumerate(listings, 1):
    lid   = l["listing_id"]
    price = l.get("price", {}).get("amount", 0) / 100
    title = l.get("title", "")[:65]
    print(f"{i:2}. €{price:.2f}  [{lid}]  {title}")
    print(f"     -> https://www.etsy.com/listing/{lid}")
