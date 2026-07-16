"""
update_shop.py
Sets the shop announcement + digital purchase message automatically.
Run once:  python update_shop.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

TITLE = "Google Sheets Templates — Budget, Business & Planner Spreadsheets | Buy Once, Own Forever"

ANNOUNCEMENT = (
    "Welcome to NasriTools! 🧡 116 Google Sheets templates that work instantly — "
    "no subscriptions, no sign-ups, no watermarks. Buy once, own forever. "
    "Every template is fully customizable and works on phone, tablet & desktop. "
    "New tools added every week. Questions? Message me — I reply fast."
)

DIGITAL_MESSAGE = (
    "Thank you for your purchase! 🧡\n\n"
    "HOW TO GET YOUR TEMPLATE:\n"
    "1. Open the PDF you just downloaded\n"
    "2. Click the link inside\n"
    "3. Go to File → Make a Copy — that's it, the template is yours forever\n\n"
    "TIP: Use it on any device — phone, tablet or desktop.\n\n"
    "Need help or want a custom change? Message me anytime — I usually reply "
    "within a few hours. And if you love the template, a 5-star review helps "
    "my small shop more than you know. Thank you! — Nasri"
)

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
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }

def main():
    print("=" * 60)
    print("  NasriTools — Shop Settings Updater")
    print("=" * 60)
    token = get_token()

    r = requests.put(
        f"{API}/shops/{SHOP_ID}",
        headers=auth_headers(token),
        data={
            "title": TITLE,
            "announcement": ANNOUNCEMENT,
            "digital_sale_message": DIGITAL_MESSAGE,
            "sale_message": DIGITAL_MESSAGE,
        },
        timeout=30,
    )
    if r.ok:
        shop = r.json()
        print("  ✓ Shop title set")
        print("  ✓ Announcement set")
        print("  ✓ Digital purchase message set")
        print("  ✓ Order message set")
        print(f"\n  Announcement now: {shop.get('announcement','')[:80]}...")
    else:
        print(f"  ✗ Failed: {r.status_code} {r.text[:300]}")
    print("=" * 60)

if __name__ == "__main__":
    main()
