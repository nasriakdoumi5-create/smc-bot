"""
publish_starter.py
Publishes the Starter Budget Tracker (€0.99 lead magnet) to Etsy:
draft listing → 5 images → xlsx + PDF guide → activate.
Run:  python publish_starter.py
"""
import json, os, time, requests
from pathlib import Path

from build_starter import STARTER

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

SLUG       = STARTER["slug"]
FOLDER     = Path(__file__).parent / "output" / SLUG
PRICE      = 0.99
TAXONOMY   = 2078          # Templates (digital downloads)

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

def build_description():
    lines = [
        "★ Starter Budget Tracker — Google Sheets Template ★",
        "",
        "The easiest way to start budgeting. One clean page, 5-minute setup,",
        "and you finally know where your money goes.",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "✅ WHAT YOU GET",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "• My Budget dashboard — income, spending & what's left, auto-calculated",
        "• Income tab with simple category dropdowns",
        "• Spending tab that tracks every expense",
        "• Excel file (.xlsx) that works in Google Sheets AND Excel",
        "• PDF setup guide — you'll be running in 5 minutes",
        "• Instant digital download",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "⚡ HOW IT WORKS",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "1. Purchase & download",
        "2. Open in Google Sheets (free) or Excel",
        "3. Type your income and expenses — everything calculates itself",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "🧡 WHY NASRITOOLS",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "• Buy once, own forever — NO subscriptions, ever",
        "• No sign-ups, no watermarks, no locked cells",
        "• This is our starter tool — explore the shop for 116 more templates",
        "",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "❓ FAQ",
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
        "Q: Do I need Excel?",
        "A: No — works in Google Sheets, which is 100% free.",
        "",
        "Q: Is this really a one-time payment?",
        "A: Yes. €0.99, once. It's our welcome gift price.",
        "",
        "Q: Can I use it on my phone?",
        "A: Yes — via the free Google Sheets app.",
        "",
        "─────────────────────",
        "Instant download • Lifetime access • Made with care by NasriTools",
    ]
    return "\n".join(lines)

def main():
    print("=" * 60)
    print("  Publishing: Starter Budget Tracker (€0.99)")
    print("=" * 60)

    if not FOLDER.exists():
        print(f"  ✗ {FOLDER} not found — run: python build_starter.py")
        return

    token = get_token()

    # 1. Create draft listing
    print("  [1/4] Creating listing...")
    tags = [t.strip()[:20] for t in STARTER["tags"][:13]]
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={
            "quantity": 999,
            "title": STARTER["listing_title"][:140],
            "description": build_description(),
            "price": PRICE,
            "who_made": "i_did",
            "when_made": "2020_2025",
            "taxonomy_id": TAXONOMY,
            "type": "download",
            "is_supply": False,
            "is_digital": True,
            "tags": tags,
        },
        timeout=30,
    )
    if not r.ok:
        print(f"  ✗ Create failed: {r.status_code} {r.text[:300]}")
        return
    listing_id = r.json()["listing_id"]
    print(f"  ✓ listing_id = {listing_id}")

    # 2. Upload images
    print("  [2/4] Uploading 5 images...")
    images = sorted(FOLDER.glob(f"{SLUG}_0*.jpg"))
    for rank, img in enumerate(images[:10], 1):
        with open(img, "rb") as fh:
            r = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{listing_id}/images",
                headers=auth_headers(token),
                files={"image": (img.name, fh, "image/jpeg")},
                data={"rank": rank, "overwrite": "true"},
                timeout=60,
            )
        print(f"    {'✓' if r.ok else '✗'} {img.name}" + ("" if r.ok else f" ({r.status_code})"))
        time.sleep(0.5)

    # 3. Upload digital files
    print("  [3/4] Uploading digital files...")
    for rank, (fname, mime) in enumerate([
        (f"{SLUG}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        (f"{SLUG}_guide.pdf", "application/pdf"),
    ], 1):
        fpath = FOLDER / fname
        if not fpath.exists():
            print(f"    ⚠ missing {fname}")
            continue
        with open(fpath, "rb") as fh:
            r = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{listing_id}/files",
                headers=auth_headers(token),
                files={"file": (fname, fh, mime)},
                data={"name": fname, "rank": rank},
                timeout=120,
            )
        print(f"    {'✓' if r.ok else '✗'} {fname}" + ("" if r.ok else f" ({r.status_code}: {r.text[:100]})"))
        time.sleep(0.5)

    # 4. Activate
    print("  [4/4] Activating listing...")
    token = get_token()
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data={"state": "active"},
        timeout=30,
    )
    if r.ok:
        print(f"  ✓ LIVE → https://www.etsy.com/listing/{listing_id}")
    else:
        print(f"  ⚠ Could not auto-activate ({r.status_code}) — activate it in")
        print(f"    Shop Manager → Listings → Drafts")
        print(f"    {r.text[:200]}")

    print("=" * 60)

if __name__ == "__main__":
    main()
