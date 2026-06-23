"""
create_free_listing.py
Creates a free Budget Tracker Lite listing on Etsy (€0).
The file contains a link to the full version.
"""
import json, os, time, requests, urllib.parse, io
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

TITLE = "Budget Tracker Google Sheets FREE | Monthly Budget & Expense Tracker Starter"

DESCRIPTION = """⚡ FREE DOWNLOAD — No catch, no email required. Just click and use.

★★★★★ WHAT YOU GET (FREE VERSION):
✓ 3-Month Budget Tracker (Jan–Mar)
✓ Income & Expense Categories
✓ Auto-Calculating Totals
✓ Monthly Summary Overview
✓ Works on Google Sheets (free)

─────────────────────────────────
HOW TO USE:
1. Click the file to download
2. Open Google Sheets
3. File → Import → Upload the file
4. Start tracking immediately
─────────────────────────────────

📱 Works on Phone, Tablet & Desktop
🔓 No subscription, no account needed
✏️ Fully editable — change any category

─────────────────────────────────
WANT THE FULL VERSION?
The complete Budget Tracker includes:
✓ Full 12-Month Tracker
✓ Annual Summary Dashboard
✓ Savings & Debt Payoff Tracker
✓ Income vs Expense Charts
✓ Bill Payment Calendar

→ Visit our shop: nasritools.etsy.com
─────────────────────────────────

Questions? Message us — we reply within 24 hours.
© NasriTools — Professional Google Sheets Templates"""

TAGS = [
    "budget tracker", "free budget", "google sheets",
    "expense tracker", "monthly budget", "free template",
    "budget spreadsheet", "free download", "personal finance",
    "money tracker", "free planner", "budget tool", "finance tracker"
]

FREE_FILE_CONTENT = """NASRITOOLS — Budget Tracker Google Sheets (FREE Starter Version)
================================================================

Thank you for downloading! Here's how to get started:

STEP 1: Open this link in your browser (Google Sheets template):
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/copy
(This opens a pre-built template — click "Make a copy")

STEP 2: Save it to your Google Drive

STEP 3: Start filling in your income and expenses!

================================================================
WHAT'S INCLUDED IN THIS FREE VERSION:
- 3-Month Budget Tracker (January to March)
- Income & Expense categories (fully editable)
- Auto-calculating totals
- Monthly overview summary

================================================================
WANT THE COMPLETE VERSION? (12 months + charts + debt tracker)
→ https://nasritools.etsy.com

We have 118 templates for Finance, Business, Health & Productivity.
Use code WELCOME10 for 10% off your first purchase.

================================================================
NEED HELP?
Message us on Etsy — we reply within 24 hours.
nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
================================================================
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

def get_active_listing_meta(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                     headers=auth_headers(token), params={"limit": 1})
    if r.ok:
        results = r.json().get("results", [])
        if results:
            l = results[0]
            return l.get("return_policy_id"), l.get("shipping_profile_id")
    return None, None

def create_listing(token, return_policy_id, shipping_profile_id):
    tags_str = "&".join(f"tags[]={urllib.parse.quote(t, safe='')}" for t in TAGS[:13])
    data = (
        f"title={urllib.parse.quote(TITLE)}"
        f"&description={urllib.parse.quote(DESCRIPTION)}"
        f"&price=0.20"
        f"&quantity=999"
        f"&who_made=i_did"
        f"&when_made=2020_2025"
        f"&taxonomy_id=2078"
        f"&type=download"
        f"&is_digital=true"
        f"&{tags_str}"
    )
    if return_policy_id:
        data += f"&return_policy_id={return_policy_id}"
    if shipping_profile_id:
        data += f"&shipping_profile_id={shipping_profile_id}"

    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=data, timeout=30,
    )
    return r.ok, r.status_code, r.json() if r.ok else r.text[:300]

def upload_file(token, lid):
    content = FREE_FILE_CONTENT.encode("utf-8")
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
        headers=auth_headers(token),
        files={"file": ("Budget_Tracker_FREE_NasriTools.txt",
                        io.BytesIO(content), "text/plain")},
        data={"name": "Budget_Tracker_FREE_NasriTools.txt", "rank": 1},
        timeout=60,
    )
    return r.ok, r.status_code

def activate_listing(token, lid):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="state=active", timeout=30,
    )
    return r.ok, r.status_code, r.text[:200]

def main():
    print("=" * 65)
    print("  NasriTools — Create Free Budget Tracker Listing")
    print("=" * 65)

    token = get_token()

    print("[1] Fetching return policy...")
    rp_id, sp_id = get_active_listing_meta(token)
    print(f"    return_policy_id={rp_id} | shipping_profile_id={sp_id}")

    print("[2] Creating listing...")
    token = get_token()
    ok, code, result = create_listing(token, rp_id, sp_id)
    if not ok:
        print(f"    FAIL ({code}): {result}")
        return
    lid = result["listing_id"]
    print(f"    OK — listing_id={lid}")

    time.sleep(2)

    print("[3] Uploading digital file...")
    token = get_token()
    f_ok, f_code = upload_file(token, lid)
    print(f"    {'OK' if f_ok else f'FAIL ({f_code})'}")
    time.sleep(2)

    print("[4] Activating listing...")
    token = get_token()
    a_ok, a_code, a_text = activate_listing(token, lid)
    if a_ok:
        print(f"    OK ✅ — LIVE!")
        print(f"\n  Listing URL: https://www.etsy.com/listing/{lid}")
    else:
        print(f"    FAIL ({a_code}): {a_text[:100]}")

    print("=" * 65)

if __name__ == "__main__":
    main()
