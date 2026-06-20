"""
audit_store.py
Pulls real store data from Etsy API for technical audit.
Outputs: titles, tags, images count, shop info, sections.
"""
import json, os, time, requests, statistics
from pathlib import Path
from collections import Counter

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at",0)-60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token",data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,
            "refresh_token":t["refresh_token"]})
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t,indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],
            "x-api-key":CLIENT_ID+":"+SECRET}

def get_all_listings(token):
    listings,offset = [],0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token),
                         params={"limit":100,"offset":offset,
                                 "includes":["images","tags"]})
        if not r.ok:
            print(f"  ERROR {r.status_code}: {r.text[:200]}")
            break
        results = r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100
        time.sleep(0.5)
    return listings

def get_shop_info(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}", headers=auth_headers(token))
    return r.json() if r.ok else {}

def get_shop_sections(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/sections", headers=auth_headers(token))
    return r.json().get("results",[]) if r.ok else []

def get_shop_policies(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/policies", headers=auth_headers(token))
    return r.json() if r.ok else {}

def main():
    token = get_token()
    print("Fetching store data...\n")

    shop      = get_shop_info(token)
    sections  = get_shop_sections(token)
    policies  = get_shop_policies(token)
    listings  = get_all_listings(token)

    print(f"=== SHOP INFO ===")
    print(f"Name:          {shop.get('shop_name','?')}")
    print(f"Title:         {shop.get('title','(empty)')}")
    print(f"About (chars): {len(shop.get('sale_message','') or '')}")
    ann = shop.get('announcement','') or ''
    print(f"Announcement:  {ann[:120] if ann else '(empty)'}")
    icon = shop.get('icon_url_fullxfull','')
    banner = shop.get('banner_image','')
    print(f"Icon URL:      {'SET' if icon else 'MISSING'}")
    print(f"Banner:        {'SET' if banner else 'MISSING'}")
    print(f"Sections ({len(sections)}):")
    for s in sections:
        print(f"  - [{s.get('rank',0)}] {s.get('title','?')} (active_listing_count={s.get('active_listing_count',0)})")

    print(f"\n=== POLICIES ===")
    for k in ['has_online_only_returns','privacy_policy','refunds','shipping_info']:
        v = policies.get(k,'N/A')
        if isinstance(v,str): v = v[:60]
        print(f"  {k}: {v}")

    print(f"\n=== LISTINGS ANALYSIS ({len(listings)} active) ===")

    title_lengths, tag_counts, desc_lengths, has_image, prices = [],[],[],[],[]
    tag_frequency = Counter()
    title_has_pipe = 0
    title_too_long = 0   # >140 chars
    title_too_short = 0  # <60 chars
    no_tags = 0
    tags_under_13 = 0
    short_desc = 0       # <500 chars
    keyword_in_title_not_in_tags = 0

    for l in listings:
        title = l.get("title","")
        tags  = l.get("tags",[])
        desc  = l.get("description","") or ""
        imgs  = l.get("images",[])
        price_data = l.get("price",{})
        price = price_data.get("amount",0) / max(price_data.get("divisor",100),1)

        title_lengths.append(len(title))
        tag_counts.append(len(tags))
        desc_lengths.append(len(desc))
        has_image.append(1 if imgs else 0)
        prices.append(price)

        if "|" in title: title_has_pipe += 1
        if len(title)>140: title_too_long += 1
        if len(title)<60: title_too_short += 1
        if not tags: no_tags += 1
        if len(tags)<13: tags_under_13 += 1
        if len(desc)<500: short_desc += 1

        for t in tags:
            tag_frequency[t.lower()] += 1

    print(f"\nTitle length:  avg={statistics.mean(title_lengths):.0f} | min={min(title_lengths)} | max={max(title_lengths)}")
    print(f"  > 140 chars: {title_too_long} listings")
    print(f"  < 60 chars:  {title_too_short} listings")
    print(f"  Uses | pipe: {title_has_pipe} listings")

    print(f"\nTags per listing: avg={statistics.mean(tag_counts):.1f} | min={min(tag_counts)} | max={max(tag_counts)}")
    print(f"  No tags:     {no_tags} listings")
    print(f"  < 13 tags:   {tags_under_13} listings")

    print(f"\nDescription:  avg={statistics.mean(desc_lengths):.0f} chars")
    print(f"  < 500 chars: {short_desc} listings")

    print(f"\nImages:  {sum(has_image)}/{len(listings)} have at least 1 image")

    print(f"\nPrice range: €{min(prices):.2f} – €{max(prices):.2f} | avg €{statistics.mean(prices):.2f}")

    print(f"\nTop 20 most used tags:")
    for tag,count in tag_frequency.most_common(20):
        print(f"  [{count:3}x] {tag}")

    print(f"\nTop 20 OVERUSED tags (same tag on many listings = low differentiation):")
    for tag,count in tag_frequency.most_common(20):
        if count >= 10:
            print(f"  OVERUSED [{count}x]: {tag}")

    # Sample 5 listings for title+tags spot check
    print(f"\n=== SPOT CHECK: 5 sample listings ===")
    for l in listings[:5]:
        print(f"\n  TITLE: {l.get('title','')[:100]}")
        print(f"  TAGS ({len(l.get('tags',[]))}): {', '.join(l.get('tags',[])[:7])}")
        print(f"  PRICE: €{l.get('price',{}).get('amount',0)/max(l.get('price',{}).get('divisor',100),1):.2f}")
        print(f"  IMAGES: {len(l.get('images',[]))}")

    # Save full data
    with open("audit_data.json","w") as f:
        json.dump({
            "shop": shop,
            "sections": sections,
            "policies": policies,
            "listings_summary": [
                {"id":l["listing_id"],"title":l["title"],"tags":l.get("tags",[]),
                 "images":len(l.get("images",[])),"price":l.get("price",{}).get("amount",0)/max(l.get("price",{}).get("divisor",100),1),
                 "desc_len":len(l.get("description","") or "")}
                for l in listings
            ]
        }, f, indent=2)
    print(f"\n[*] Full data saved to audit_data.json")

if __name__=="__main__":
    main()
