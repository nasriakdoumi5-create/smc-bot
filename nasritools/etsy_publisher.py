"""
NasriTools — Etsy Auto-Publisher
Publishes built products from output/ to Etsy automatically.

Usage:
  python nasritools/etsy_publisher.py                  # publish all un-published
  python nasritools/etsy_publisher.py budget_tracker   # publish one product
  python nasritools/etsy_publisher.py --list           # show published status
"""

import json
import sys
import time
from pathlib import Path

import requests

from nasritools.etsy_auth import auth_header, get_token, CLIENT_ID
from nasritools.products import CATALOG

OUTPUT_DIR   = Path(__file__).parent.parent / "output"
PUBLISHED_DB = Path(__file__).parent / "published.json"
API          = "https://api.etsy.com/v3/application"

TAXONOMY_ID  = 2078   # Paper & Party Supplies → Templates (digital downloads)
WHEN_MADE    = "2020_2025"


# ── Persistence ──────────────────────────────────────────────────────────

def _load_db() -> dict:
    if PUBLISHED_DB.exists():
        return json.loads(PUBLISHED_DB.read_text())
    return {}

def _save_db(db: dict):
    PUBLISHED_DB.write_text(json.dumps(db, indent=2))


# ── Etsy API helpers ─────────────────────────────────────────────────────

def _get(path: str, token: dict, **params) -> dict:
    r = requests.get(f"{API}{path}", headers=auth_header(token), params=params)
    r.raise_for_status()
    return r.json()

def _post(path: str, token: dict, json_body=None, files=None, data=None) -> dict:
    headers = auth_header(token)
    if json_body is not None:
        headers["Content-Type"] = "application/json"
        r = requests.post(f"{API}{path}", headers=headers, json=json_body)
    else:
        r = requests.post(f"{API}{path}", headers=headers, files=files, data=data)
    if not r.ok:
        print(f"    API error {r.status_code}: {r.text[:300]}")
        r.raise_for_status()
    return r.json()

def _patch(path: str, token: dict, json_body: dict) -> dict:
    headers = {**auth_header(token), "Content-Type": "application/json"}
    r = requests.patch(f"{API}{path}", headers=headers, json=json_body)
    r.raise_for_status()
    return r.json()


# ── Shop lookup ──────────────────────────────────────────────────────────

def get_shop_id(token: dict) -> int:
    data = _get("/users/me", token)
    shop_id = data.get("shop_id") or data.get("primary_email")
    if not shop_id:
        # fallback: search by name
        shops = _get("/shops", token, shop_name="NasriTools")
        shop_id = shops["results"][0]["shop_id"]
    return int(shop_id)


# ── Listing creation ─────────────────────────────────────────────────────

def _parse_price(price_str: str) -> float:
    return float(price_str.replace("$", "").replace("€", "").strip())

def _clean_tags(tags: list) -> list:
    cleaned = []
    for t in tags[:13]:
        t = t.strip()[:20]
        if t:
            cleaned.append(t)
    return cleaned

def create_listing(shop_id: int, cfg: dict, token: dict) -> int:
    price = _parse_price(cfg.get("price", "12"))
    tags  = _clean_tags(cfg.get("tags", []))
    title = cfg.get("listing_title", cfg["name"])[:140]

    body = {
        "quantity":       999,
        "title":          title,
        "description":    _build_description(cfg),
        "price":          price,
        "who_made":       "i_did",
        "when_made":      WHEN_MADE,
        "taxonomy_id":    TAXONOMY_ID,
        "type":           "download",
        "is_supply":      False,
        "is_customizable": False,
        "is_digital":     True,
        "processing_min": 0,
        "processing_max": 0,
        "tags":           tags,
    }
    result = _post(f"/shops/{shop_id}/listings", token, json_body=body)
    return result["listing_id"]


def _build_description(cfg: dict) -> str:
    tabs     = cfg.get("tabs", [])
    features = cfg.get("features", [])
    perfect  = cfg.get("perfect_for", [])
    how      = cfg.get("how_to_use", [])
    emoji    = cfg.get("listing_emoji", "🔵")
    subtitle = cfg.get("subtitle", "")
    intro    = cfg.get("description_intro", "")

    lines = []
    lines.append(f"{emoji} {cfg['name'].upper()}")
    lines.append(subtitle)
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append("━" * 20)
    lines.append("✅ WHAT'S INCLUDED")
    lines.append("━" * 20)
    lines.append("")
    lines.append("📥 Instant Download:")
    lines.append(f"• {cfg['slug']}.xlsx (Google Sheets & Excel)")
    lines.append("• PDF Setup Guide")
    lines.append("")
    if tabs:
        lines.append(f"{len(tabs)} Professional Tabs:")
        for t in tabs:
            lines.append(f"{t.get('emoji','📋')} {t['name']} — {t.get('description','')}")
    lines.append("")
    lines.append("━" * 20)
    lines.append("🎯 PERFECT FOR")
    lines.append("━" * 20)
    for p in perfect:
        lines.append(f"• {p}")
    lines.append("")
    lines.append("━" * 20)
    lines.append("⚡ KEY FEATURES")
    lines.append("━" * 20)
    for f in features:
        lines.append(f"✔ {f}")
    lines.append("")
    lines.append("━" * 20)
    lines.append("🚀 HOW TO USE")
    lines.append("━" * 20)
    for i, step in enumerate(how, 1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("📦 INSTANT DOWNLOAD — yours forever, no subscriptions.")
    lines.append("⭐ Questions? Message us — we respond within 24 hours.")
    return "\n".join(lines)


# ── Image upload ─────────────────────────────────────────────────────────

def upload_images(shop_id: int, listing_id: int, slug: str, token: dict):
    folder = OUTPUT_DIR / slug
    image_files = sorted(folder.glob(f"{slug}_0*.jpg"))
    for rank, img_path in enumerate(image_files[:10], 1):
        print(f"    📸 Uploading image {rank}/{len(image_files)}: {img_path.name}")
        with open(img_path, "rb") as fh:
            _post(
                f"/shops/{shop_id}/listings/{listing_id}/images",
                token,
                files={"image": (img_path.name, fh, "image/jpeg")},
                data={"rank": rank, "overwrite": "true"},
            )
        time.sleep(0.5)


# ── Digital file upload ───────────────────────────────────────────────────

def upload_files(shop_id: int, listing_id: int, slug: str, token: dict):
    folder = OUTPUT_DIR / slug
    to_upload = [
        folder / f"{slug}.xlsx",
        folder / f"{slug}_guide.pdf",
    ]
    for rank, fpath in enumerate(to_upload, 1):
        if not fpath.exists():
            continue
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
               if fpath.suffix == ".xlsx" else "application/pdf"
        print(f"    📎 Uploading file: {fpath.name}")
        with open(fpath, "rb") as fh:
            _post(
                f"/shops/{shop_id}/listings/{listing_id}/files",
                token,
                files={"file": (fpath.name, fh, mime)},
                data={"name": fpath.name, "rank": rank},
            )
        time.sleep(0.5)


# ── Full publish pipeline ─────────────────────────────────────────────────

def publish_product(cfg: dict, shop_id: int, token: dict, db: dict) -> bool:
    slug = cfg["slug"]
    folder = OUTPUT_DIR / slug

    if not folder.exists():
        print(f"  ⚠  output/{slug}/ not found — run factory first.")
        return False

    if slug in db:
        print(f"  ✓  {cfg['name']} already published (listing {db[slug]})")
        return True

    print(f"\n  Publishing: {cfg['name']}")

    try:
        print("    [1/3] Creating listing draft...")
        listing_id = create_listing(shop_id, cfg, token)
        print(f"    ✅ listing_id = {listing_id}")

        print("    [2/3] Uploading images...")
        upload_images(shop_id, listing_id, slug, token)

        print("    [3/3] Uploading digital files...")
        upload_files(shop_id, listing_id, slug, token)

        db[slug] = listing_id
        _save_db(db)
        print(f"    ✅ Published! https://www.etsy.com/listing/{listing_id}")
        return True

    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--list" in args:
        db = _load_db()
        print(f"\n  {'Slug':<30} {'Listing ID':<14} {'URL'}")
        print("  " + "─" * 70)
        for cfg in CATALOG:
            slug = cfg["slug"]
            lid  = db.get(slug)
            url  = f"etsy.com/listing/{lid}" if lid else "—"
            mark = "✓" if lid else "○"
            print(f"  {mark}  {slug:<28} {str(lid or ''):<14} {url}")
        return

    print("\n  Loading token...")
    token = get_token()

    print("  Getting shop ID...")
    shop_id = get_shop_id(token)
    print(f"  Shop ID: {shop_id}")

    db = _load_db()

    if args and args[0] != "--all":
        # Publish specific slug
        slug = args[0]
        cfg  = next((c for c in CATALOG if c["slug"] == slug), None)
        if not cfg:
            print(f"  ✗ '{slug}' not found in catalog.")
            sys.exit(1)
        publish_product(cfg, shop_id, token, db)
    else:
        # Publish all
        total  = len(CATALOG)
        ok     = 0
        skip   = 0
        failed = 0
        for i, cfg in enumerate(CATALOG, 1):
            print(f"\n  [{i}/{total}]", end="")
            if cfg["slug"] in db:
                skip += 1
                continue
            if publish_product(cfg, shop_id, token, db):
                ok += 1
                time.sleep(2)
            else:
                failed += 1

        print(f"\n\n  Done: {ok} published, {skip} skipped, {failed} failed")


if __name__ == "__main__":
    main()
