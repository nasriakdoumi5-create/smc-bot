"""
fix_all_gaps.py
Fixes 3 remaining gaps:
1. Adds FAQ block to all listing descriptions
2. Updates shop announcement
3. Adds message-to-buyers template
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

FAQ_BLOCK = """

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Can I edit the template after purchase?
A: Yes! Everything is fully editable — colors, categories, formulas, data.

Q: Do I need to pay for Google Sheets?
A: No. Google Sheets is 100% free. You only need a free Google account.

Q: How do I access my file after purchase?
A: Check your email or go to Etsy → Your Account → Purchases → Download.
   Then click the Google Sheets link → File → Make a Copy → it's yours forever.

Q: Will it work on my phone?
A: Yes! Download the free Google Sheets app (iOS/Android) and open the file there.
   Note: Downloads don't work in the Etsy mobile app — open etsy.com in your browser instead.

Q: Is this a physical product?
A: No. This is a digital download — instant access after purchase.

Q: Can I get a refund?
A: Digital downloads are non-refundable once accessed, per Etsy policy.
   Have questions before purchasing? Message me — I respond within 24 hours!

Q: What if I need help setting it up?
A: Message me anytime — I'm happy to help you get started ✅

→ More templates: nasritools.etsy.com"""

SHOP_ANNOUNCEMENT = """✅ Welcome to NasriTools! All templates are instant digital downloads — no waiting, no shipping.

📥 HOW IT WORKS: Purchase → Check email → Click Google Sheets link → File → Make a Copy → Done in 2 minutes!

📱 Mobile users: If download doesn't show in the Etsy app, open etsy.com in your phone browser → Your Account → Purchases.

💬 Questions? Message me — I respond within 24 hours. Happy organizing! 🎯"""

MESSAGE_TO_BUYERS = """Thank you for your purchase! 🎉

Here's how to access your Google Sheets template:

1. Open the PDF attached to this order (check your email or Etsy → Purchases)
2. Click the Google Sheets link inside the PDF
3. Go to File → Make a Copy → save to your Google Drive
4. Start using it — it's yours forever! ✅

📱 On mobile: Use the Google Sheets app (free) to open and edit your file.

Questions? Reply to this message — I'm here to help!

Thank you for supporting NasriTools 🙏
nasritools.etsy.com"""

FAQ_MARKER = "❓ FREQUENTLY ASKED QUESTIONS"

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

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
        )
        if not r.ok:
            break
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        if len(results) < 100:
            break
        offset += 100
    return listings

def update_listing_desc(token, lid, description):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({"description": description}),
        timeout=30,
    )
    return r.ok, r.status_code

def update_shop(token, announcement, message):
    r = requests.put(
        f"{API}/shops/{SHOP_ID}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({
            "announcement": announcement,
            "digital_sale_message": message,
        }),
        timeout=30,
    )
    return r.ok, r.status_code

def main():
    print("=" * 65)
    print("  NasriTools — Fix All Gaps (FAQ + Announcement + Message)")
    print("=" * 65)

    token = get_token()
    print("[*] Token OK\n")

    # ── Step 1: Update shop announcement + message to buyers ──────────
    print("[1/2] Updating shop announcement & message to buyers...")
    token = get_token()
    ok, code = update_shop(token, SHOP_ANNOUNCEMENT, MESSAGE_TO_BUYERS)
    if ok:
        print(f"  ✅ Shop updated (HTTP {code})")
    else:
        print(f"  ❌ Failed (HTTP {code})")

    # ── Step 2: Add FAQ to all listings ───────────────────────────────
    print("\n[2/2] Adding FAQ to all listings...")
    listings = get_all_listings(token)
    print(f"  Found {len(listings)} listings\n")

    ok_count = skip_count = fail_count = 0

    for l in listings:
        lid   = l["listing_id"]
        title = l["title"][:45]
        desc  = l.get("description", "") or ""

        if FAQ_MARKER in desc:
            print(f"  [SKIP] {title[:40]}")
            skip_count += 1
            continue

        new_desc = desc + FAQ_BLOCK

        print(f"  [FAQ]  {title[:40]} ...", end=" ", flush=True)
        token = get_token()
        ok, code = update_listing_desc(token, lid, new_desc)
        if ok:
            print(f"OK ({code})")
            ok_count += 1
        else:
            print(f"FAILED ({code})")
            fail_count += 1
        time.sleep(1.2)

    print(f"\n{'='*65}")
    print(f"  Shop: Updated ✅")
    print(f"  FAQ:  {ok_count} updated | {skip_count} skipped | {fail_count} failed")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
