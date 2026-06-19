"""
NasriTools - Shop Announcement Updater
Updates the Etsy shop announcement with current promotions.
Edit ANNOUNCEMENT below and run: python update_announcement.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# ── Edit this announcement as needed ─────────────────────────────────────────
ANNOUNCEMENT = """\
🎉 Welcome to NasriTools — Premium Google Sheets Templates!

⚡ INSTANT DOWNLOAD — Start using in minutes, no waiting.
✅ Works on Google Sheets (FREE) & Microsoft Excel
♾️ Lifetime access — buy once, yours forever

🔥 BEST SELLERS:
• Budget Tracker — track every expense automatically
• Habit Tracker — build 30 daily habits with streak counter
• Content Creator Planner — plan months of content in one weekend
• Ultimate Bundle — ALL 10 templates at 65% off!

🎁 FREE GIFT: Get our Budget Tracker Lite for FREE (check our shop!)

💬 Questions? Message us — we reply within 24 hours.
⭐ Happy customer? A review takes 30 seconds and helps us grow!

nasritools.etsy.com
"""


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


def main():
    token = get_token()

    print(f"\n{'='*60}")
    print(f"  NasriTools - Shop Announcement Updater")
    print(f"{'='*60}\n")

    print("  Updating shop announcement…", end=" ")
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"announcement": ANNOUNCEMENT},
        timeout=30,
    )

    if r.ok:
        print("✓")
        print(f"\n  Announcement updated successfully!")
    else:
        print(f"✗  {r.status_code}: {r.text[:200]}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
