"""
analyze_store.py — Full NasriTools Etsy store audit
Fetches all listings and outputs a JSON report.
"""
import json, os, time, requests
from pathlib import Path
from collections import defaultdict

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

def get_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit": 100, "offset": offset,
                                 "includes": ["images","tags"]}, timeout=30)
        if not r.ok:
            print(f"Error: {r.status_code} {r.text[:200]}")
            break
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        print(f"  Fetched {len(listings)} listings...")
        if len(results) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings

def get_shop_info(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}", headers=auth_headers(token), timeout=30)
    return r.json() if r.ok else {}

def analyze(listings):
    issues_critical = []
    issues_medium   = []
    issues_low      = []

    # Per-listing analysis
    by_type = defaultdict(list)
    price_dist = []
    tag_counts = []
    title_lengths = []
    no_images = []
    short_desc = []
    generic_titles = []

    GENERIC_STARTS = ["google sheets", "spreadsheet", "template", "tracker", "planner"]
    PRIME_KEYWORDS = {
        "budget":      "Budget Tracker Spreadsheet",
        "invoice":     "Invoice Template Google Sheets",
        "kpi":         "Business Dashboard Google Sheets",
        "fitness":     "Workout Tracker Spreadsheet",
        "meal":        "Meal Planner Spreadsheet",
        "habit":       "Habit Tracker Spreadsheet",
        "goals":       "Goal Planner Spreadsheet",
        "student":     "Student Planner Spreadsheet",
        "event":       "Event Planner Spreadsheet",
        "content":     "Content Calendar Spreadsheet",
        "project":     "Project Tracker Spreadsheet",
        "inventory":   "Inventory Tracker Spreadsheet",
        "realestate":  "Real Estate Spreadsheet",
        "hr":          "HR Template Google Sheets",
        "restaurant":  "Restaurant Spreadsheet Template",
        "travel":      "Travel Planner Spreadsheet",
        "planner":     "Planner Spreadsheet Template",
        "bundle":      "Google Sheets Bundle",
        "productivity":"Productivity Tracker Spreadsheet",
    }

    for l in listings:
        lid   = l["listing_id"]
        title = l.get("title","")
        price = float(l.get("price",{}).get("amount",0)) / max(1, l.get("price",{}).get("divisor",100))
        tags  = l.get("tags",[])
        desc  = l.get("description","")
        imgs  = l.get("images",[])

        price_dist.append(price)
        tag_counts.append(len(tags))
        title_lengths.append(len(title))

        if len(imgs) == 0:
            no_images.append({"id": lid, "title": title})
        if len(tags) < 13:
            issues_medium.append(f"TAGS < 13: '{title[:50]}' has only {len(tags)} tags")
        if len(title) < 80:
            issues_medium.append(f"TITLE SHORT ({len(title)} chars): '{title[:50]}'")
        if len(desc) < 300:
            short_desc.append({"id": lid, "title": title[:50], "desc_len": len(desc)})
        if len(imgs) < 3:
            issues_low.append(f"FEW IMAGES ({len(imgs)}): '{title[:50]}'")

        # type detection (simplified)
        t = title.lower()
        ptype = "productivity"
        if any(x in t for x in ["bundle","complete system","kit","pack","all-in-one"]):
            ptype = "bundle"
        elif any(x in t for x in ["budget","expense","spending","financial","cash flow"]):
            ptype = "budget"
        elif any(x in t for x in ["invoice","billing","freelanc"]):
            ptype = "invoice"
        elif any(x in t for x in ["kpi","dashboard","sales tracker","pipeline","crm"]):
            ptype = "kpi"
        elif any(x in t for x in ["workout","fitness","gym","exercise","weight loss"]):
            ptype = "fitness"
        elif any(x in t for x in ["meal","food","recipe","nutrition","grocery"]):
            ptype = "meal"
        elif any(x in t for x in ["habit","routine"]):
            ptype = "habit"
        elif any(x in t for x in ["goal","vision","achievement"]):
            ptype = "goals"
        elif any(x in t for x in ["student","school","study","college","grade"]):
            ptype = "student"
        elif any(x in t for x in ["wedding","event planner","party","birthday"]):
            ptype = "event"
        elif any(x in t for x in ["content","social media","instagram","youtube","tiktok"]):
            ptype = "content"
        elif any(x in t for x in ["project","task manager","agile","sprint","gantt"]):
            ptype = "project"
        elif any(x in t for x in ["inventory","stock","ecommerce","etsy shop"]):
            ptype = "inventory"
        elif any(x in t for x in ["real estate","property","rental"]):
            ptype = "realestate"
        elif any(x in t for x in ["hr ","employee","hiring","recruitment"]):
            ptype = "hr"
        elif any(x in t for x in ["restaurant","cafe","food business"]):
            ptype = "restaurant"
        elif any(x in t for x in ["travel","trip","vacation","itinerary"]):
            ptype = "travel"
        elif any(x in t for x in ["weekly planner","monthly planner","daily planner"]):
            ptype = "planner"

        by_type[ptype].append({"id": lid, "title": title, "price": price, "tags": len(tags), "images": len(imgs)})

    avg_price = sum(price_dist)/len(price_dist) if price_dist else 0
    avg_tags  = sum(tag_counts)/len(tag_counts) if tag_counts else 0
    avg_title = sum(title_lengths)/len(title_lengths) if title_lengths else 0

    return {
        "total": len(listings),
        "avg_price": round(avg_price, 2),
        "avg_tags": round(avg_tags, 1),
        "avg_title_len": round(avg_title, 1),
        "no_images": no_images,
        "short_desc": short_desc[:20],
        "issues_critical": issues_critical[:30],
        "issues_medium": issues_medium[:50],
        "issues_low": issues_low[:30],
        "by_type": {k: {"count": len(v), "items": v[:3]} for k, v in by_type.items()},
        "price_min": min(price_dist) if price_dist else 0,
        "price_max": max(price_dist) if price_dist else 0,
        "raw_listings": listings,
    }

def main():
    print("Fetching store data...")
    token    = get_token()
    shop     = get_shop_info(token)
    listings = get_all_listings(token)

    print(f"\nAnalyzing {len(listings)} listings...")
    report = analyze(listings)
    report["shop"] = {
        "name": shop.get("shop_name",""),
        "title": shop.get("title",""),
        "about": shop.get("sale_message",""),
        "announcement": shop.get("announcement",""),
        "num_favorites": shop.get("num_favorers",0),
    }

    with open("store_audit.json","w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"\n{'='*60}")
    print(f"  NASRITOOLS STORE AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"  Total listings : {report['total']}")
    print(f"  Avg price      : €{report['avg_price']}")
    print(f"  Avg tags       : {report['avg_tags']}/13")
    print(f"  Avg title len  : {report['avg_title_len']}/140 chars")
    print(f"  No images      : {len(report['no_images'])}")
    print(f"  Short desc     : {len(report['short_desc'])}")
    print(f"\n  Products by type:")
    for k, v in report["by_type"].items():
        print(f"    {k:15} {v['count']:3} products")
    print(f"\n  Issues (medium): {len(report['issues_medium'])}")
    print(f"  Issues (low)   : {len(report['issues_low'])}")
    print(f"\n  Full report → store_audit.json")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
