"""
NasriTools - Set Google Sheets Links & Build Bundle Delivery Files
1. Paste your 10 Google Sheets sharing links below
2. Run: python set_bundle_links.py
3. Script builds all 5 bundle .txt files and uploads them to Etsy
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
OUT_DIR    = Path(os.path.expanduser("~")) / "nasri_bundle_files"
OUT_DIR.mkdir(exist_ok=True)

# ════════════════════════════════════════════════════════════
#  PASTE YOUR 10 GOOGLE SHEETS SHARING LINKS HERE
#  (File → Share → "Anyone with the link" → Copy link)
# ════════════════════════════════════════════════════════════
LINKS = {
    "budget_tracker":             "PASTE_LINK_HERE",
    "habit_tracker":              "PASTE_LINK_HERE",
    "meal_planner":               "PASTE_LINK_HERE",
    "wedding_planner":            "PASTE_LINK_HERE",
    "workout_tracker":            "PASTE_LINK_HERE",
    "content_creator_planner":    "PASTE_LINK_HERE",
    "freelancer_invoice_tracker": "PASTE_LINK_HERE",
    "student_planner":            "PASTE_LINK_HERE",
    "goals_planner":              "PASTE_LINK_HERE",
    "weekly_planner":             "PASTE_LINK_HERE",
}

LABELS = {
    "budget_tracker":             "Budget Tracker",
    "habit_tracker":              "Habit Tracker",
    "meal_planner":               "Meal Planner",
    "wedding_planner":            "Wedding Planner",
    "workout_tracker":            "Workout Tracker",
    "content_creator_planner":    "Content Creator Planner",
    "freelancer_invoice_tracker": "Freelancer Invoice Tracker",
    "student_planner":            "Student Planner",
    "goals_planner":              "Goals Planner",
    "weekly_planner":             "Weekly Planner",
}

BUNDLES = {
    "finance_bundle": {
        "name":     "Finance Bundle",
        "products": ["budget_tracker", "freelancer_invoice_tracker", "goals_planner"],
        "filename": "finance_bundle_delivery.txt",
        "etsy_id":  4524283814,
    },
    "health_bundle": {
        "name":     "Health Bundle",
        "products": ["workout_tracker", "meal_planner", "habit_tracker"],
        "filename": "health_bundle_delivery.txt",
        "etsy_id":  4524276503,
    },
    "planner_bundle": {
        "name":     "Planner Bundle",
        "products": ["weekly_planner", "student_planner", "goals_planner"],
        "filename": "planner_bundle_delivery.txt",
        "etsy_id":  4524276527,
    },
    "business_bundle": {
        "name":     "Business Bundle",
        "products": ["content_creator_planner", "freelancer_invoice_tracker", "goals_planner"],
        "filename": "business_bundle_delivery.txt",
        "etsy_id":  4524276553,
    },
    "ultimate_bundle": {
        "name":     "Ultimate Bundle (All 10 Templates)",
        "products": [
            "budget_tracker", "habit_tracker", "meal_planner", "wedding_planner",
            "workout_tracker", "content_creator_planner", "freelancer_invoice_tracker",
            "student_planner", "goals_planner", "weekly_planner",
        ],
        "filename": "ultimate_bundle_delivery.txt",
        "etsy_id":  4524283886,
    },
}


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


def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def build_txt(bundle_name, pairs):
    sep = "=" * 64
    lines = [
        sep,
        f"  NasriTools — {bundle_name}",
        "  Thank you for your purchase!",
        sep,
        "",
        "HOW TO ACCESS YOUR TEMPLATES:",
        "  1. Click each link below",
        "  2. Click  File → Make a copy",
        "  3. Save it to your Google Drive — it's yours forever!",
        "",
        "-" * 64,
        "  YOUR TEMPLATES:",
        "-" * 64,
        "",
    ]
    for i, (label, link) in enumerate(pairs, 1):
        lines.append(f"  {i}. {label}")
        lines.append(f"     {link}")
        lines.append("")
    lines += [
        "-" * 64,
        "",
        "IMPORTANT:",
        "  • Make a copy before editing — do NOT request edit access",
        "  • Works on Google Sheets (free) and Microsoft Excel",
        "  • Lifetime access — yours forever after purchase",
        "",
        "NEED HELP?",
        "  Message us on Etsy — we reply within 24 hours.",
        "  nasritools.etsy.com",
        "",
        sep,
        "  Thank you for supporting NasriTools!",
        "  Please leave a review — it means the world to us ♥",
        sep,
    ]
    return "\n".join(lines)


def upload_file_to_listing(token, listing_id, filepath):
    """Upload a .txt file to an Etsy listing as a digital download."""
    with open(filepath, "rb") as f:
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/files",
            headers=auth_headers(token),
            files={"file": (filepath.name, f, "text/plain")},
            data={"name": filepath.name, "rank": 1},
            timeout=60,
        )
    return r


def publish_listing(token, listing_id):
    """Change listing state from draft to active."""
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "active"},
        timeout=30,
    )
    return r


def main():
    print(f"\n{'='*65}")
    print(f"  NasriTools - Bundle Delivery File Builder")
    print(f"{'='*65}\n")

    # Check links
    missing = [s for s, v in LINKS.items() if v == "PASTE_LINK_HERE"]
    if missing:
        print(f"  ⚠  You still need to paste {len(missing)} link(s) in LINKS dict:\n")
        for s in missing:
            print(f"     • {LABELS[s]}")
        print(f"\n  Open set_bundle_links.py and replace PASTE_LINK_HERE")
        print(f"  with the real sharing links from Google Sheets.\n")
        print(f"  How to get a link:")
        print(f"    1. Open the template in Google Sheets")
        print(f"    2. Click Share → Change to 'Anyone with the link' → Viewer")
        print(f"    3. Copy link and paste it above")
        print(f"{'='*65}\n")
        return

    token = get_token()

    # Build & upload each bundle
    for bkey, bundle in BUNDLES.items():
        pairs = [(LABELS[s], LINKS[s]) for s in bundle["products"]]
        content = build_txt(bundle["name"], pairs)
        out = OUT_DIR / bundle["filename"]
        out.write_text(content, encoding="utf-8")

        lid = bundle["etsy_id"]
        print(f"  [{bkey}]  Uploading {bundle['filename']} → listing {lid}")

        r = upload_file_to_listing(token, lid, out)
        time.sleep(1)

        if r.ok:
            print(f"    ✓ File uploaded")
        else:
            print(f"    ✗ Upload failed {r.status_code}: {r.text[:120]}")
            continue

        # Publish the listing
        rp = publish_listing(token, lid)
        time.sleep(1)
        if rp.ok:
            print(f"    ✓ Listing PUBLISHED  → https://www.etsy.com/listing/{lid}")
        else:
            print(f"    ✗ Publish failed {rp.status_code}: {rp.text[:120]}")

    print(f"\n{'='*65}")
    print(f"  Done! Bundle files built and uploaded to Etsy.")
    print(f"  Local copies saved to: {OUT_DIR}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
