"""
evaluate_store.py
Comprehensive honest store audit with scores per dimension.
"""
import json, os, time, requests
from pathlib import Path
from collections import Counter

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"]})
        r.raise_for_status(); t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def get_shop_info(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}", headers=auth_headers(token), timeout=30)
    return r.json() if r.ok else {}

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                        headers=auth_headers(token),
                        params={"limit": 100, "offset": offset}, timeout=30)
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100; time.sleep(0.4)
    return listings

def get_listing_images(token, lid):
    r = requests.get(f"{API}/listings/{lid}/images",
                    headers=auth_headers(token), timeout=20)
    if r.ok:
        return r.json().get("results", [])
    return []

def score_bar(score, max_score=10):
    filled = int((score / max_score) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {score}/{max_score}"

def main():
    print("=" * 65)
    print("  NasriTools — Honest Store Evaluation")
    print("=" * 65)

    token = get_token()

    # ── Fetch shop info ───────────────────────────────────────────
    print("\n[*] Fetching shop data...")
    shop = get_shop_info(token)
    sale_count    = shop.get("transaction_sold_count", 0)
    review_count  = shop.get("review_count", 0)
    review_avg    = shop.get("review_average_rating", 0)
    shop_title    = shop.get("shop_name", "")
    announcement  = shop.get("announcement", "")

    # ── Fetch all listings ─────────────────────────────────────────
    listings = get_all_listings(token)
    total = len(listings)
    print(f"[*] {total} active listings found")

    # ── Check images for sample (first 10) ────────────────────────
    print("[*] Checking images (sample of 10)...")
    sample = listings[:10]
    img_counts = []
    for l in sample:
        imgs = get_listing_images(token, l["listing_id"])
        img_counts.append(len(imgs))
        time.sleep(0.5)
    avg_images = sum(img_counts) / len(img_counts) if img_counts else 0

    # ── Analyze prices ─────────────────────────────────────────────
    prices = []
    for l in listings:
        try:
            p = float(l["price"]["amount"]) / float(l["price"]["divisor"])
            prices.append(p)
        except: pass
    price_min  = min(prices) if prices else 0
    price_max  = max(prices) if prices else 0
    price_avg  = sum(prices)/len(prices) if prices else 0
    free_count = sum(1 for p in prices if p <= 0.21)

    # ── Analyze tags ───────────────────────────────────────────────
    all_tags = []
    for l in listings:
        all_tags.extend(l.get("tags", []))
    tag_counter = Counter(all_tags)
    most_common = tag_counter.most_common(5)
    unique_tags = len(set(all_tags))
    total_tags  = len(all_tags)

    # ── Analyze titles ─────────────────────────────────────────────
    titles = [l["title"] for l in listings]
    avg_title_len = sum(len(t) for t in titles) / len(titles) if titles else 0
    keyword_first = sum(1 for t in titles if not t.lower().startswith("the ") and len(t) > 10)

    # ── Categories ────────────────────────────────────────────────
    cats = Counter()
    for l in listings:
        t = l["title"].lower()
        if any(k in t for k in ["budget","finance","invoice","cash"]): cats["Finance"] += 1
        elif any(k in t for k in ["kpi","business","sales"]): cats["Business"] += 1
        elif any(k in t for k in ["workout","health","meal","fitness"]): cats["Health"] += 1
        elif any(k in t for k in ["planner","productivity","goal","habit"]): cats["Productivity"] += 1
        else: cats["Other"] += 1

    # ══════════════════════════════════════════════════════════════
    print("\n" + "=" * 65)
    print("  NASRITOOLS STORE EVALUATION — HONEST ASSESSMENT")
    print("=" * 65)

    # ── 1. TRUST & SOCIAL PROOF ───────────────────────────────────
    trust_score = 0
    if review_count >= 10: trust_score = 10
    elif review_count >= 5: trust_score = 6
    elif review_count >= 1: trust_score = 3
    else: trust_score = 0

    print(f"\n① TRUST & SOCIAL PROOF      {score_bar(trust_score)}")
    print(f"   Reviews: {review_count} | Avg rating: {review_avg}/5 | Sales: {sale_count}")
    if review_count == 0:
        print("   ⚠ CRITICAL: 0 reviews = Etsy algorithm ignores the shop")
        print("   → Fix: Set all prices to €0.20 + Reddit posts NOW")

    # ── 2. PRODUCT CATALOG ────────────────────────────────────────
    cat_score = min(10, total // 10 + (3 if len(cats) >= 4 else 0))
    print(f"\n② PRODUCT CATALOG           {score_bar(cat_score)}")
    print(f"   Total listings: {total}")
    print(f"   Categories: {dict(cats)}")
    if total >= 50:
        print("   ✓ Good product volume")
    if len(cats) >= 4:
        print("   ✓ Good category diversity")

    # ── 3. PRICING STRATEGY ───────────────────────────────────────
    price_score = 5  # neutral start
    if free_count > 0: price_score += 2
    if price_min <= 5: price_score += 1
    if price_avg > 10: price_score += 2
    if review_count == 0 and price_avg > 15: price_score -= 3  # too high for new shop

    print(f"\n③ PRICING STRATEGY          {score_bar(min(10,price_score))}")
    print(f"   Min: €{price_min:.2f} | Max: €{price_max:.2f} | Avg: €{price_avg:.2f}")
    print(f"   €0.20 listings: {free_count}")
    if review_count == 0 and price_avg > 15:
        print("   ⚠ Prices too high for a shop with 0 reviews")
        print("   → Buyers don't trust new shops at €30-50")

    # ── 4. SEO (TITLES + TAGS) ────────────────────────────────────
    seo_score = 0
    if avg_title_len > 80: seo_score += 3
    if avg_title_len > 100: seo_score += 1
    if unique_tags > 50: seo_score += 3
    if most_common[0][1] < total * 0.5: seo_score += 2  # no tag used >50% of time
    if announcement: seo_score += 1

    print(f"\n④ SEO (TITLES + TAGS)       {score_bar(min(10,seo_score))}")
    print(f"   Avg title length: {avg_title_len:.0f} chars (ideal: 100-140)")
    print(f"   Unique tags: {unique_tags} across {total} listings")
    print(f"   Most overused tags:")
    for tag, count in most_common:
        pct = count / total * 100
        flag = " ⚠" if pct > 60 else ""
        print(f"     '{tag}': {count}x ({pct:.0f}%){flag}")
    if not announcement:
        print("   ⚠ No shop announcement set")

    # ── 5. VISUAL / IMAGES ────────────────────────────────────────
    visual_score = 0
    if avg_images >= 5: visual_score = 10
    elif avg_images >= 3: visual_score = 7
    elif avg_images >= 2: visual_score = 5
    elif avg_images >= 1: visual_score = 3

    print(f"\n⑤ VISUAL / IMAGES           {score_bar(visual_score)}")
    print(f"   Avg images per listing (sample): {avg_images:.1f}")
    print(f"   Sample image counts: {img_counts}")
    if avg_images < 3:
        print("   ⚠ Etsy recommends 5-10 images per listing")

    # ── 6. EXTERNAL TRAFFIC ───────────────────────────────────────
    traffic_score = 1  # baseline
    print(f"\n⑥ EXTERNAL TRAFFIC          {score_bar(traffic_score)}")
    print(f"   Reddit post: 1 (submitted, pending approval)")
    print(f"   Pinterest: NOT SET UP")
    print(f"   Ads: NOT AVAILABLE (shop too new)")
    print(f"   ⚠ 95%+ of visibility depends on external traffic right now")

    # ── OVERALL ───────────────────────────────────────────────────
    overall = (trust_score + cat_score + min(10,price_score) +
               min(10,seo_score) + visual_score + traffic_score) / 6

    print(f"\n{'='*65}")
    print(f"  OVERALL SCORE:  {overall:.1f}/10")
    print(f"{'='*65}")

    print("\n  TOP 3 ACTIONS (highest ROI):")
    print("  1. python set_price_020.py  → removes price barrier (5 min)")
    print("  2. Reddit post approved     → wait & reply to comments")
    print("  3. Pinterest account        → passive traffic source")
    print()

    # Save
    report = {
        "trust": trust_score, "catalog": cat_score,
        "pricing": min(10,price_score), "seo": min(10,seo_score),
        "visual": visual_score, "traffic": traffic_score,
        "overall": round(overall,1),
        "reviews": review_count, "sales": sale_count, "listings": total
    }
    Path("evaluation_report.json").write_text(json.dumps(report, indent=2))
    print(f"  Report saved to evaluation_report.json")

if __name__ == "__main__":
    main()
