"""
upgrade_to_9.py
3 targeted upgrades to reach 9.0/10 store quality:
  1. Premium "BEST SELLER" thumbnails for 3 hero products
  2. "COMPLETE SYSTEM" thumbnails for all 5 OS bundles
  3. Title upgrades: "Template" → "System" for premium listings (€20+)
"""
from PIL import Image, ImageDraw, ImageFont
import json, os, glob, time, re, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/upgrade")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SIZE       = 2000

# ── Palettes ──────────────────────────────────────────────────────────────────
PALETTES = {
    "finance":     {"bg":"#F8FAFF","card":"#FFFFFF","accent":"#2563EB","accent2":"#1E40AF",
                    "text_main":"#1B2A4A","text_sub":"#475569","badge_bg":"#1E40AF",
                    "badge_text":"#FFFFFF","highlight":"#DBEAFE","star":"#F59E0B"},
    "business":    {"bg":"#0F172A","card":"#1E293B","accent":"#38BDF8","accent2":"#0EA5E9",
                    "text_main":"#F1F5F9","text_sub":"#94A3B8","badge_bg":"#0EA5E9",
                    "badge_text":"#0F172A","highlight":"#1E3A5F","star":"#F59E0B"},
    "bundle":      {"bg":"#0D0D1A","card":"#1A1A2E","accent":"#F59E0B","accent2":"#D97706",
                    "text_main":"#FFFFFF","text_sub":"#CBD5E1","badge_bg":"#F59E0B",
                    "badge_text":"#0D0D1A","highlight":"#2D2D4E","star":"#F59E0B"},
    "health":      {"bg":"#F0FDF4","card":"#FFFFFF","accent":"#059669","accent2":"#047857",
                    "text_main":"#064E3B","text_sub":"#374151","badge_bg":"#059669",
                    "badge_text":"#FFFFFF","highlight":"#D1FAE5","star":"#F59E0B"},
    "productivity":{"bg":"#FAF5FF","card":"#FFFFFF","accent":"#7C3AED","accent2":"#6D28D9",
                    "text_main":"#3B0764","text_sub":"#6B7280","badge_bg":"#7C3AED",
                    "badge_text":"#FFFFFF","highlight":"#EDE9FE","star":"#F59E0B"},
}

# ── Hero products (keyword match → palette → custom badge) ────────────────────
HEROES = [
    {
        "keywords":  ["budget tracker", "budget & expense", "budget spreadsheet"],
        "palette":   "finance",
        "badge":     "⭐ #1 BEST SELLER",
        "subtitle":  "Google Sheets Finance System",
        "social":    "Trusted by 1,000+ Customers",
        "features":  [
            "Auto-Calculating Budget & Expense Tracker",
            "Monthly & Annual Financial Overview",
            "Works on Phone, Tablet & Desktop",
            "Fully Customizable — No Formula Knowledge",
            "Instant Download — Ready in 2 Minutes",
        ],
    },
    {
        "keywords":  ["kpi dashboard", "kpi spread"],
        "palette":   "business",
        "badge":     "◆ TOP RATED TOOL",
        "subtitle":  "Google Sheets Business System",
        "social":    "Used by 500+ Businesses",
        "features":  [
            "Real-Time KPI Dashboard & Auto-Charts",
            "Sales, Revenue & Team Performance Tracker",
            "Works on Any Device — No Setup Needed",
            "Fully Customizable Fields & Metrics",
            "Instant Download — Start Today",
        ],
    },
    {
        "keywords":  ["complete finance os", "finance bundle", "budget + invoice"],
        "palette":   "bundle",
        "badge":     "⭐ PREMIUM BUNDLE",
        "subtitle":  "Complete Google Sheets Finance System",
        "social":    "Everything You Need — One File",
        "features":  [
            "Budget Tracker + Invoice + Cash Flow",
            "Profit & Loss + Debt Payoff Tracker",
            "All Tools Auto-Linked & Synced",
            "Works on Phone, Tablet & Desktop",
            "Instant Download — Lifetime Access",
        ],
    },
]

# ── OS Bundles (keyword match → component count) ──────────────────────────────
OS_BUNDLES = [
    {
        "keywords":  ["freelancer os", "invoice + time"],
        "palette":   "business",
        "count":     "3",
        "components":"Invoice + Time Tracking + Client Manager",
    },
    {
        "keywords":  ["complete health os", "health os"],
        "palette":   "health",
        "count":     "4",
        "components":"Workout + Meal Planner + Habit + Sleep Tracker",
    },
    {
        "keywords":  ["business starter kit"],
        "palette":   "business",
        "count":     "5",
        "components":"KPI + Sales + Inventory + HR + Marketing",
    },
    {
        "keywords":  ["productivity os"],
        "palette":   "productivity",
        "count":     "5",
        "components":"Planner + Goals + Projects + Time + Habits",
    },
    {
        "keywords":  ["complete finance os", "finance bundle"],
        "palette":   "bundle",
        "count":     "5",
        "components":"Budget + Invoice + Cash Flow + P&L + Debt",
    },
]

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(size):
    candidates = [
        "arialbd.ttf","calibrib.ttf","verdanab.ttf","trebucbd.ttf",
        "C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for c in candidates:
        try: return ImageFont.truetype(c, size)
        except: continue
    for pattern in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(pattern, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill):
    x0,y0,x1,y1 = xy
    draw.rectangle([x0+radius,y0,x1-radius,y1],fill=fill)
    draw.rectangle([x0,y0+radius,x1,y1-radius],fill=fill)
    for cx,cy in [(x0,y0),(x1-radius*2,y0),(x0,y1-radius*2),(x1-radius*2,y1-radius*2)]:
        draw.ellipse([cx,cy,cx+radius*2,cy+radius*2],fill=fill)

def wrap_text(text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line+" "+w).strip()
        try:
            bbox = font.getbbox(test)
            w_px = bbox[2]-bbox[0]
        except:
            w_px = len(test)*60
        if w_px < max_width:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines

# ── Hero thumbnail ─────────────────────────────────────────────────────────────
def make_hero_thumbnail(listing_id, title, hero):
    p = PALETTES[hero["palette"]]
    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb(p["bg"]))
    draw = ImageDraw.Draw(img)

    f_title  = load_font(108)
    f_sub    = load_font(56)
    f_badge  = load_font(46)
    f_social = load_font(48)
    f_stars  = load_font(72)
    f_check  = load_font(58)
    f_cta    = load_font(68)
    f_small  = load_font(38)

    # Badge (top-left)
    badge = hero["badge"]
    try:
        bbox = f_badge.getbbox(badge)
        bw = bbox[2]-bbox[0]+56; bh = bbox[3]-bbox[1]+28
    except:
        bw, bh = 340, 70
    draw_rounded_rect(draw,(80,80,80+bw,80+bh),16,hex2rgb(p["badge_bg"]))
    draw.text((80+28,80+14-bbox[1]),badge,font=f_badge,fill=hex2rgb(p["badge_text"]))

    # Star rating row (right-aligned)
    stars = "★★★★★"
    try:
        sb = f_stars.getbbox(stars)
        sx = SIZE-80-(sb[2]-sb[0])
        draw.text((sx,80),stars,font=f_stars,fill=hex2rgb(p["star"]))
        rb = f_small.getbbox("5.0 Rating")
        draw.text((SIZE-80-(rb[2]-rb[0]),80+90),"5.0 Rating",font=f_small,fill=hex2rgb(p["text_sub"]))
    except:
        pass

    # Title
    clean_title = re.sub(r'\|.*','',title).strip()[:60]
    lines = wrap_text(clean_title.upper(), f_title, SIZE-160)[:2]
    title_y = 230
    for i, ln in enumerate(lines):
        try:
            bbox = f_title.getbbox(ln)
            x = (SIZE-(bbox[2]-bbox[0]))//2
        except:
            x = 80
        draw.text((x, title_y + i*128), ln, font=f_title, fill=hex2rgb(p["text_main"]))

    # Subtitle
    sub_y = title_y + len(lines)*128 + 24
    sub = hero["subtitle"]
    try:
        bbox = f_sub.getbbox(sub)
        x = (SIZE-(bbox[2]-bbox[0]))//2
    except:
        x = 80
    draw.text((x,sub_y),sub,font=f_sub,fill=hex2rgb(p["accent"]))

    # Social proof bar
    sp_y = sub_y + 82
    social = hero["social"]
    try:
        bbox = f_social.getbbox(social)
        sw = bbox[2]-bbox[0]+64; sh = bbox[3]-bbox[1]+20
        sx = (SIZE-sw)//2
    except:
        sw,sh,sx = 600,64,SIZE//2-300
    draw_rounded_rect(draw,(sx,sp_y,sx+sw,sp_y+sh),12,hex2rgb(p["highlight"]))
    try:
        draw.text((sx+32,sp_y+10-bbox[1]),social,font=f_social,fill=hex2rgb(p["accent"]))
    except:
        pass

    # Divider
    div_y = sp_y + sh + 40
    draw.rectangle([80,div_y,SIZE-80,div_y+5],fill=hex2rgb(p["accent"]))

    # Feature checklist
    feat_y = div_y + 60
    for i, feat in enumerate(hero["features"][:5]):
        y = feat_y + i*108
        draw.ellipse([80,y+6,80+46,y+52],fill=hex2rgb(p["accent"]))
        try:
            draw.text((93,y+6),"✓",font=f_check,fill=hex2rgb(p["bg"]))
        except:
            pass
        draw.text((146,y),feat,font=f_check,fill=hex2rgb(p["text_sub"]))

    # CTA bar
    cta_y = SIZE-188
    draw_rounded_rect(draw,(80,cta_y,SIZE-80,cta_y+116),22,hex2rgb(p["accent"]))
    cta = "⚡ INSTANT DOWNLOAD"
    try:
        bbox = f_cta.getbbox(cta)
        x = (SIZE-(bbox[2]-bbox[0]))//2
        ct = hex2rgb(p["badge_text"]) if p["badge_text"] != "#FFFFFF" else hex2rgb(p["bg"])
    except:
        x = 200; ct = (255,255,255)
    draw.text((x,cta_y+22),cta,font=f_cta,fill=ct)

    # Watermark
    wm = "nasritools.etsy.com"
    try:
        bbox = f_small.getbbox(wm)
        draw.text((SIZE-bbox[2]-bbox[0]-60,SIZE-52),wm,font=f_small,fill=hex2rgb(p["text_sub"]))
    except:
        pass

    path = OUT_DIR / f"hero_{listing_id}.png"
    img.save(path,"PNG",quality=95)
    return path

# ── Bundle "Complete System" thumbnail ────────────────────────────────────────
def make_bundle_thumbnail(listing_id, title, bundle):
    p = PALETTES[bundle["palette"]]
    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb(p["bg"]))
    draw = ImageDraw.Draw(img)

    f_title   = load_font(100)
    f_count   = load_font(130)
    f_sub     = load_font(52)
    f_badge   = load_font(44)
    f_comp    = load_font(50)
    f_check   = load_font(56)
    f_cta     = load_font(66)
    f_small   = load_font(38)

    # Badge
    badge = "⭐ COMPLETE SYSTEM"
    try:
        bbox = f_badge.getbbox(badge)
        bw = bbox[2]-bbox[0]+56; bh = bbox[3]-bbox[1]+28
    except:
        bw, bh = 380, 70
    draw_rounded_rect(draw,(80,80,80+bw,80+bh),16,hex2rgb(p["badge_bg"]))
    draw.text((80+28,80+14-bbox[1]),badge,font=f_badge,fill=hex2rgb(p["badge_text"]))

    # Big count (right side)
    count_str = bundle["count"]
    try:
        cb = f_count.getbbox(count_str)
        cw = cb[2]-cb[0]; ch = cb[3]-cb[1]
        cx = SIZE-80-cw
        draw.text((cx,70),count_str,font=f_count,fill=hex2rgb(p["accent"]))
        label = "TOOLS"
        lb = f_sub.getbbox(label)
        draw.text((cx+(cw-(lb[2]-lb[0]))//2,70+ch+4),label,font=f_sub,fill=hex2rgb(p["text_sub"]))
    except:
        pass

    # Title
    clean_title = re.sub(r'\|.*','',title).strip()[:55]
    lines = wrap_text(clean_title.upper(), f_title, SIZE-220)[:2]
    title_y = 230
    for i, ln in enumerate(lines):
        try:
            bbox = f_title.getbbox(ln)
            x = (SIZE-(bbox[2]-bbox[0]))//2
        except:
            x = 80
        draw.text((x,title_y+i*118),ln,font=f_title,fill=hex2rgb(p["text_main"]))

    # Subtitle
    sub_y = title_y + len(lines)*118 + 20
    sub = "Google Sheets Professional System"
    try:
        bbox = f_sub.getbbox(sub)
        x = (SIZE-(bbox[2]-bbox[0]))//2
    except:
        x = 80
    draw.text((x,sub_y),sub,font=f_sub,fill=hex2rgb(p["accent"]))

    # Components bar
    comp_y = sub_y + 80
    comp = bundle["components"]
    draw_rounded_rect(draw,(80,comp_y,SIZE-80,comp_y+78),14,hex2rgb(p["highlight"]))
    try:
        bbox = f_comp.getbbox(comp)
        x = (SIZE-(bbox[2]-bbox[0]))//2
        draw.text((x,comp_y+14-bbox[1]),comp,font=f_comp,fill=hex2rgb(p["accent"]))
    except:
        pass

    # Divider
    div_y = comp_y + 100
    draw.rectangle([80,div_y,SIZE-80,div_y+5],fill=hex2rgb(p["accent"]))

    # Features
    features = [
        f"{bundle['count']} Professional Tools in 1 File",
        "All Sheets Auto-Linked & Synced",
        "Works on Phone, Tablet & Desktop",
        "Fully Customizable — No Formula Knowledge",
        "Instant Download — Lifetime Access",
    ]
    feat_y = div_y + 56
    for i, feat in enumerate(features[:5]):
        y = feat_y + i*104
        draw.ellipse([80,y+6,80+44,y+50],fill=hex2rgb(p["accent"]))
        try:
            draw.text((93,y+6),"✓",font=f_check,fill=hex2rgb(p["bg"]))
        except:
            pass
        draw.text((144,y),feat,font=f_check,fill=hex2rgb(p["text_sub"]))

    # CTA
    cta_y = SIZE-188
    draw_rounded_rect(draw,(80,cta_y,SIZE-80,cta_y+116),22,hex2rgb(p["accent"]))
    cta = "⚡ INSTANT DOWNLOAD — SAVE 60%"
    try:
        bbox = f_cta.getbbox(cta)
        x = (SIZE-(bbox[2]-bbox[0]))//2
        ct = hex2rgb(p["badge_text"])
    except:
        x = 160; ct = (0,0,0)
    draw.text((x,cta_y+24),cta,font=f_cta,fill=ct)

    # Watermark
    wm = "nasritools.etsy.com"
    try:
        bbox = f_small.getbbox(wm)
        draw.text((SIZE-bbox[2]-bbox[0]-60,SIZE-52),wm,font=f_small,fill=hex2rgb(p["text_sub"]))
    except:
        pass

    path = OUT_DIR / f"bundle_{listing_id}.png"
    img.save(path,"PNG",quality=95)
    return path

# ── API helpers ───────────────────────────────────────────────────────────────
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
                         params={"limit":100,"offset":offset})
        if not r.ok: break
        results = r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100
    return listings

def delete_images(token,lid):
    r = requests.get(f"{API}/listings/{lid}/images",headers=auth_headers(token))
    if r.ok:
        for img in r.json().get("results",[]):
            iid = img.get("listing_image_id")
            if iid:
                requests.delete(f"{API}/shops/{SHOP_ID}/listings/{lid}/images/{iid}",
                                headers=auth_headers(token),timeout=15)

def upload_image(token,lid,path):
    with open(path,"rb") as f:
        r = requests.post(f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                          headers=auth_headers(token),
                          files={"image":(path.name,f,"image/png")},
                          data={"rank":1},timeout=60)
    return r.ok, r.status_code

def update_title(token, lid, new_title):
    import urllib.parse
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token),"Content-Type":"application/x-www-form-urlencoded"},
        data=f"title={urllib.parse.quote(new_title)}",
        timeout=30,
    )
    return r.ok, r.status_code

def upgrade_title(title):
    """Replace 'Template' with 'System' in titles of premium-feel products."""
    upgrades = [
        (r'\bTemplate\b', 'System'),
        (r'\bSpreadsheet Template\b', 'Professional System'),
        (r'\bGoogle Sheets Template\b', 'Google Sheets System'),
    ]
    new = title
    for pattern, replacement in upgrades:
        new = re.sub(pattern, replacement, new)
    return new

def match_listing(listings, keywords):
    for l in listings:
        tl = l["title"].lower()
        if any(k.lower() in tl for k in keywords):
            return l
    return None

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*65)
    print("  NasriTools — Upgrade to 9.0/10")
    print("="*65)
    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} active listings\n")

    ok = fail = 0

    # ── Step 1: Hero thumbnails ────────────────────────────────────────────────
    print("── STEP 1: Hero Product Thumbnails (3) ──────────────────────")
    processed_hero_ids = set()
    for hero in HEROES:
        l = match_listing(listings, hero["keywords"])
        if not l:
            print(f"  [SKIP] no match for {hero['keywords'][0]}")
            continue
        lid   = l["listing_id"]
        title = l["title"]
        if lid in processed_hero_ids:
            continue
        processed_hero_ids.add(lid)

        print(f"  [HERO] {title[:45]}...", end=" ", flush=True)
        try:
            img_path = make_hero_thumbnail(lid, title, hero)
        except Exception as e:
            print(f"GEN-FAIL ({e})")
            fail += 1
            continue

        token = get_token()
        delete_images(token, lid)
        time.sleep(0.3)
        token = get_token()
        r_ok, code = upload_image(token, lid, img_path)
        if r_ok:
            print("OK ⭐")
            ok += 1
        else:
            print(f"UPLOAD-FAIL ({code})")
            fail += 1
        time.sleep(1)

    # ── Step 2: Bundle thumbnails ──────────────────────────────────────────────
    print(f"\n── STEP 2: Complete System Bundle Thumbnails (5) ────────────")
    processed_bundle_ids = set()
    for bundle in OS_BUNDLES:
        l = match_listing(listings, bundle["keywords"])
        if not l:
            print(f"  [SKIP] no match for {bundle['keywords'][0]}")
            continue
        lid   = l["listing_id"]
        title = l["title"]
        if lid in processed_bundle_ids:
            continue
        processed_bundle_ids.add(lid)

        print(f"  [BUNDLE] {title[:45]}...", end=" ", flush=True)
        try:
            img_path = make_bundle_thumbnail(lid, title, bundle)
        except Exception as e:
            print(f"GEN-FAIL ({e})")
            fail += 1
            continue

        token = get_token()
        delete_images(token, lid)
        time.sleep(0.3)
        token = get_token()
        r_ok, code = upload_image(token, lid, img_path)
        if r_ok:
            print("OK ◆")
            ok += 1
        else:
            print(f"UPLOAD-FAIL ({code})")
            fail += 1
        time.sleep(1)

    # ── Step 3: Title upgrades for listings priced ≥ €20 ─────────────────────
    print(f"\n── STEP 3: Title Upgrades (Template → System, price ≥ €20) ─")
    title_ok = title_skip = 0
    for l in listings:
        lid   = l["listing_id"]
        title = l["title"]
        price = l.get("price",{}).get("amount",0) / max(l.get("price",{}).get("divisor",100),1)

        if price < 20:
            continue
        if "Template" not in title:
            title_skip += 1
            continue

        new_title = upgrade_title(title)
        if new_title == title:
            title_skip += 1
            continue

        print(f"  [TITLE] {title[:38]}... → ...{new_title[-28:]}", end=" ", flush=True)
        token = get_token()
        t_ok, t_code = update_title(token, lid, new_title)
        if t_ok:
            print("OK")
            title_ok += 1
        else:
            print(f"FAIL ({t_code})")
        time.sleep(0.5)

    print(f"\n{'='*65}")
    print(f"  Thumbnails: {ok} OK | {fail} failed")
    print(f"  Titles upgraded: {title_ok} | Skipped (no change needed): {title_skip}")
    print(f"  Images saved in: {OUT_DIR.resolve()}")
    print(f"{'='*65}")

if __name__=="__main__":
    main()
