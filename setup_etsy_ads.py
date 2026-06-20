"""
setup_etsy_ads.py
Enables Etsy Ads on all 5 bundle listings with a daily budget of €3.
Bundles get priority because they have higher value and better conversion.
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# All 5 bundle listing IDs
BUNDLE_IDS = [
    4524283886,   # Finance Bundle   €19.99
    4524724720,   # Health Bundle    €17.99
    4524724758,   # Productivity     €17.99
    4524724798,   # Business Bundle  €21.99
    4524724846,   # Complete Life    €39.99
]

DAILY_BUDGET_EUR = 300   # Etsy budget is in cents → 300 = €3.00


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


def enable_ad(token, lid):
    """Add a listing to Etsy Ads."""
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/ads",
        headers=auth_headers(token),
        json={"listing_ids": [lid]},
        timeout=30,
    )
    return r.ok, r.status_code, r.text[:200]


def set_budget(token):
    """Set shop-level daily budget for Etsy Ads."""
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/ads/daily_budget",
        headers=auth_headers(token),
        json={"daily_budget": DAILY_BUDGET_EUR},
        timeout=30,
    )
    return r.ok, r.status_code, r.text[:200]


def main():
    token = get_token()
    print("=" * 60)
    print("  NasriTools — Etsy Ads Setup")
    print(f"  Budget: €{DAILY_BUDGET_EUR/100:.2f}/day on 5 bundles")
    print("=" * 60)

    # Set daily budget
    print(f"\n[*] Setting daily budget to €{DAILY_BUDGET_EUR/100:.2f}...")
    ok, code, txt = set_budget(token)
    if ok:
        print(f"    Budget set OK")
    else:
        print(f"    Budget API returned {code}: {txt}")
        print(f"    (Set manually: Etsy → Marketing → Etsy Ads → Budget)")

    # Enable ads for each bundle
    print()
    ok_count = 0
    for lid in BUNDLE_IDS:
        token = get_token()
        print(f"  Enabling ad for [{lid}]...", end=" ", flush=True)
        ok, code, _ = enable_ad(token, lid)
        if ok:
            print(f"OK")
            ok_count += 1
        else:
            print(f"HTTP {code} (may already be active)")
        time.sleep(1)

    print(f"\n{'='*60}")
    print(f"  Done: {ok_count}/5 bundles activated for Etsy Ads")
    print(f"  Monitor performance: Etsy → Marketing → Etsy Ads")
    print(f"  Adjust budget after 7 days based on ROAS")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
