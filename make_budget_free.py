"""
NasriTools - Make Budget Tracker Lite FREE on Etsy
Sets price to €0 to maximize downloads and collect first reviews
Run: python make_budget_free.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
LISTING_ID = 4523968643   # Budget Tracker Lite (Free version)
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t


def main():
    token = get_token()
    headers = {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
        "Content-Type": "application/json",
    }

    print(f"\n{'='*55}")
    print(f"  NasriTools - Make Budget Tracker Lite FREE")
    print(f"  Listing: {LISTING_ID}")
    print(f"{'='*55}\n")

    # Update title to make "FREE" prominent and add better tags
    title_update = {
        "title": "FREE Budget Tracker Google Sheets Template | Monthly Income Expense Planner | Savings Goal | Bill Tracker",
        "price": 0.00,
        "tags": [
            "free budget tracker", "budget tracker", "expense tracker",
            "monthly budget", "personal finance", "budget spreadsheet",
            "income tracker", "free template", "financial tracker",
            "money tracker", "household budget", "spending tracker",
            "free google sheets",
        ],
    }

    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{LISTING_ID}",
        headers=headers,
        json=title_update,
        timeout=30,
    )

    if r.ok:
        print(f"  Price    → FREE (€0.00)")
        print(f"  Title    → updated with FREE prefix")
        print(f"  Tags     → 13 SEO tags updated")
        print(f"\n  Budget Tracker Lite is now completely free!")
        print(f"  More downloads = more reviews = better ranking")
    else:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")

    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    main()
