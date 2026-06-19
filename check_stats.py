"""
NasriTools - Weekly Performance Dashboard
Pulls shop stats, top listings, and saves a weekly report.
Run every Monday: python check_stats.py
"""
import json, os, time, requests
from pathlib import Path
from datetime import datetime

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
REPORT_DIR = Path(os.path.expanduser("~")) / "nasri_reports"


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


def fetch_shop(token):
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}",
        headers=auth_headers(token), timeout=30,
    )
    return r.json() if r.ok else {}


def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


def fetch_receipts(token):
    """Fetch recent orders (receipts)."""
    r = requests.get(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/receipts",
        headers=auth_headers(token),
        params={"limit": 100, "was_paid": "true"},
        timeout=30,
    )
    if r.ok:
        return r.json().get("results", [])
    return []


def main():
    REPORT_DIR.mkdir(exist_ok=True)
    token = get_token()

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n{'='*65}")
    print(f"  NasriTools - Weekly Performance Dashboard")
    print(f"  Generated: {today}")
    print(f"{'='*65}\n")

    # ── Shop overview ──────────────────────────────────────────────────────────
    print("  Fetching shop data…")
    shop = fetch_shop(token)
    token = get_token()

    shop_name = shop.get("shop_name", "NasriTools")
    sale_count = shop.get("transaction_sold_count", 0)
    review_avg = shop.get("review_average", 0)
    review_count = shop.get("review_count", 0)

    print(f"\n  ┌─ SHOP OVERVIEW ─────────────────────────────┐")
    print(f"  │  Shop: {shop_name:<38}│")
    print(f"  │  Total Sales:   {sale_count:<30}│")
    print(f"  │  Reviews:       {review_count} (avg {review_avg:.1f} ⭐){'':16}│")
    print(f"  └─────────────────────────────────────────────┘\n")

    # ── Listings analysis ──────────────────────────────────────────────────────
    print("  Fetching all active listings…")
    listings = fetch_all_listings(token)
    token = get_token()

    total_views = sum(l.get("views", 0) for l in listings)
    total_favs  = sum(l.get("num_favorers", 0) for l in listings)

    top_views = sorted(listings, key=lambda x: x.get("views", 0), reverse=True)[:10]
    top_favs  = sorted(listings, key=lambda x: x.get("num_favorers", 0), reverse=True)[:10]

    print(f"\n  ┌─ LISTING METRICS ───────────────────────────┐")
    print(f"  │  Active listings: {len(listings):<27}│")
    print(f"  │  Total views:     {total_views:<27}│")
    print(f"  │  Total favorites: {total_favs:<27}│")
    print(f"  └─────────────────────────────────────────────┘\n")

    print(f"  ── TOP 10 BY VIEWS ──")
    for i, l in enumerate(top_views, 1):
        v = l.get("views", 0)
        f = l.get("num_favorers", 0)
        t = (l.get("title") or "")[:48]
        print(f"  {i:2}. [{v:5} views | {f:3} ♥] {t}")

    print(f"\n  ── TOP 10 BY FAVORITES ──")
    for i, l in enumerate(top_favs, 1):
        v = l.get("views", 0)
        f = l.get("num_favorers", 0)
        t = (l.get("title") or "")[:48]
        print(f"  {i:2}. [{f:3} ♥ | {v:5} views] {t}")

    # ── Recent orders ──────────────────────────────────────────────────────────
    print(f"\n  Fetching recent orders…")
    receipts = fetch_receipts(token)

    if receipts:
        total_revenue = sum(
            r.get("grandtotal", {}).get("amount", 0) / 100
            for r in receipts
        )
        print(f"\n  ┌─ RECENT ORDERS ─────────────────────────────┐")
        print(f"  │  Orders found:  {len(receipts):<28}│")
        print(f"  │  Total revenue: €{total_revenue:<26.2f}│")
        print(f"  └─────────────────────────────────────────────┘")

        print(f"\n  ── RECENT SALES ──")
        for r in receipts[:15]:
            date  = r.get("create_timestamp", 0)
            total = r.get("grandtotal", {}).get("amount", 0) / 100
            items = r.get("transactions", [])
            prod  = items[0].get("title", "?")[:40] if items else "?"
            print(f"    €{total:.2f}  {prod}")
    else:
        print("  No orders found (or no API access to receipts).")

    # ── Action items ───────────────────────────────────────────────────────────
    print(f"\n  ── WEEKLY ACTION ITEMS ──")
    print(f"  □ Post 7 Pinterest pins this week (from ~/nasri_pinterest_pins/)")
    print(f"  □ Check Etsy Ads spend and ROAS in dashboard")
    print(f"  □ Reply to any unanswered messages/reviews")
    print(f"  □ Check if any listings need image updates")
    if review_count < 10:
        print(f"  □ ⚠  Only {review_count} reviews — ask recent buyers for feedback")

    # ── Save JSON report ───────────────────────────────────────────────────────
    report = {
        "date": today,
        "shop_name": shop_name,
        "total_sales": sale_count,
        "review_avg": review_avg,
        "review_count": review_count,
        "active_listings": len(listings),
        "total_views": total_views,
        "total_favorites": total_favs,
        "top_views": [
            {"id": l["listing_id"], "title": (l.get("title") or "")[:60],
             "views": l.get("views", 0), "favs": l.get("num_favorers", 0)}
            for l in top_views
        ],
    }

    report_path = REPORT_DIR / f"report_{today}.json"
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n{'='*65}")
    print(f"  Report saved: {report_path}")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
