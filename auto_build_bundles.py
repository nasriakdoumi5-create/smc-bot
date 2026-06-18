"""
NasriTools - Auto Build Bundle Delivery Files
1. Fetches digital files metadata from existing Etsy listings
2. Downloads each file and scans for Google Sheets links
3. Automatically populates all 5 bundle delivery .txt files
Run: python auto_build_bundles.py
"""
import json, os, re, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
OUT_DIR    = Path(os.path.expanduser("~")) / "nasri_bundle_files"
OUT_DIR.mkdir(exist_ok=True)

# Which products go in which bundle
BUNDLES = {
    "finance_bundle": {
        "name":      "Finance Bundle",
        "products":  ["budget_tracker", "freelancer_invoice_tracker", "goals_planner"],
        "filename":  "finance_bundle_delivery.txt",
    },
    "health_bundle": {
        "name":      "Health Bundle",
        "products":  ["workout_tracker", "meal_planner", "habit_tracker"],
        "filename":  "health_bundle_delivery.txt",
    },
    "planner_bundle": {
        "name":      "Planner Bundle",
        "products":  ["weekly_planner", "student_planner", "goals_planner"],
        "filename":  "planner_bundle_delivery.txt",
    },
    "business_bundle": {
        "name":      "Business Bundle",
        "products":  ["content_creator_planner", "freelancer_invoice_tracker", "goals_planner"],
        "filename":  "business_bundle_delivery.txt",
    },
    "ultimate_bundle": {
        "name":      "Ultimate Bundle (All 10 Templates)",
        "products":  [
            "budget_tracker", "habit_tracker", "meal_planner", "wedding_planner",
            "workout_tracker", "content_creator_planner", "freelancer_invoice_tracker",
            "student_planner", "goals_planner", "weekly_planner",
        ],
        "filename":  "ultimate_bundle_delivery.txt",
    },
}

PRODUCT_LABELS = {
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

SHEETS_PATTERN = re.compile(
    r'https?://docs\.google\.com/spreadsheets/[^\s\'"<>\]]+',
    re.IGNORECASE
)
DRIVE_PATTERN = re.compile(
    r'https?://drive\.google\.com/[^\s\'"<>\]]+',
    re.IGNORECASE
)


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


def get_listing_files(token, listing_id):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}/files",
        headers=auth_headers(token),
        timeout=15,
    )
    if r.ok:
        return r.json().get("results", [])
    print(f"    files API: {r.status_code} {r.text[:100]}")
    return []


def extract_links_from_text(text):
    links = SHEETS_PATTERN.findall(text) + DRIVE_PATTERN.findall(text)
    seen = set()
    unique = []
    for l in links:
        l = l.rstrip(".,;)")
        if l not in seen:
            seen.add(l)
            unique.append(l)
    return unique


def try_download_file(url, token):
    """Try to download a file and extract Google Sheets links from its content."""
    try:
        r = requests.get(url, headers=auth_headers(token), timeout=20)
        if r.ok:
            # Try text decoding
            for enc in ["utf-8", "latin-1", "cp1252"]:
                try:
                    text = r.content.decode(enc, errors="replace")
                    links = extract_links_from_text(text)
                    if links:
                        return links
                except Exception:
                    pass
    except Exception as e:
        print(f"    download error: {e}")
    return []


def build_delivery_file(bundle_name, product_links):
    sep = "=" * 64
    lines = [
        sep,
        f"  NasriTools — {bundle_name}",
        f"  Thank you for your purchase!",
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
    for i, (label, link) in enumerate(product_links, 1):
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


def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Auto Build Bundle Delivery Files")
    print(f"{'='*65}\n")

    # Step 1: extract links from all 10 main products
    print("  Step 1: Extracting Google Sheets links from Etsy listings...\n")
    product_links = {}   # slug → link

    for slug, label in PRODUCT_LABELS.items():
        lid = published.get(slug)
        if not lid:
            print(f"  [{slug}] SKIP — no listing ID")
            continue

        print(f"  [{slug}]  (listing {lid})")
        files = get_listing_files(token, str(lid))
        time.sleep(0.5)

        found_link = None
        for f in files:
            url = f.get("url") or f.get("download_url") or f.get("public_url")
            if url:
                print(f"    file: {f.get('filename', '?')}  → trying download...")
                links = try_download_file(url, token)
                if links:
                    found_link = links[0]
                    print(f"    ✓ found: {found_link[:70]}")
                    break
                else:
                    print(f"    no link extracted from file content")
            else:
                print(f"    file: {f.get('filename', '?')} — no download URL in API response")

        product_links[slug] = found_link
        if not found_link:
            print(f"    ✗ no link found — will use placeholder")

    # Step 2: build bundle files
    print(f"\n  Step 2: Building bundle delivery files...\n")
    missing = []

    for bkey, bundle in BUNDLES.items():
        pairs = []
        for slug in bundle["products"]:
            label = PRODUCT_LABELS.get(slug, slug)
            link  = product_links.get(slug)
            if not link:
                link = f"[LINK NEEDED: {label} — paste your Google Sheets link here]"
                missing.append(slug)
            pairs.append((label, link))

        content = build_delivery_file(bundle["name"], pairs)
        out = OUT_DIR / bundle["filename"]
        out.write_text(content, encoding="utf-8")
        print(f"  ✓  {bundle['filename']}")

    # Summary
    print(f"\n{'='*65}")
    if not missing:
        print(f"  ALL LINKS FOUND — bundle files are complete!")
        print(f"  Ready to upload to Etsy.")
    else:
        missing_unique = list(dict.fromkeys(missing))
        print(f"  {len(missing_unique)} links still missing:")
        for s in missing_unique:
            print(f"    • {PRODUCT_LABELS[s]}")
        print(f"\n  Open the files and replace the placeholder text")
        print(f"  with your actual Google Sheets sharing links.")

    print(f"\n  Files saved to: {OUT_DIR}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
