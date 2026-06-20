"""
generate_all_thumbnails.py
Generates + uploads a custom thumbnail for EVERY active listing.
Each thumbnail shows the product name, category colors, and key features.
Generates images in ./thumbnails/all/ then uploads to Etsy.
"""
from PIL import Image, ImageDraw, ImageFont
import json, os, glob, time, re, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/all")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SIZE       = 2000

# ── Palettes ──────────────────────────────────────────────────────────────────
PALETTES = {
    "finance":     {"bg":"#F8FAFF","card":"#FFFFFF","accent":"#2563EB","accent2":"#1E40AF",
                    "text_main":"#1B2A4A","text_sub":"#475569","badge_bg":"#E63946",
                    "badge_text":"#FFFFFF","highlight":"#DBEAFE","bar":"#2563EB"},
    "business":    {"bg":"#0F172A","card":"#1E293B","accent":"#38BDF8","accent2":"#0EA5E9",
                    "text_main":"#F1F5F9","text_sub":"#94A3B8","badge_bg":"#F59E0B",
                    "badge_text":"#0F172A","highlight":"#1E3A5F","bar":"#38BDF8"},
    "health":      {"bg":"#F0FDF4","card":"#FFFFFF","accent":"#059669","accent2":"#047857",
                    "text_main":"#064E3B","text_sub":"#374151","badge_bg":"#059669",
                    "badge_text":"#FFFFFF","highlight":"#D1FAE5","bar":"#059669"},
    "productivity":{"bg":"#FAF5FF","card":"#FFFFFF","accent":"#7C3AED","accent2":"#6D28D9",
                    "text_main":"#3B0764","text_sub":"#6B7280","badge_bg":"#7C3AED",
                    "badge_text":"#FFFFFF","highlight":"#EDE9FE","bar":"#7C3AED"},
    "bundle":      {"bg":"#0D0D1A","card":"#1A1A2E","accent":"#F59E0B","accent2":"#D97706",
                    "text_main":"#FFFFFF","text_sub":"#CBD5E1","badge_bg":"#F59E0B",
                    "badge_text":"#0D0D1A","highlight":"#2D2D4E","bar":"#F59E0B"},
    "default":     {"bg":"#F9FAFB","card":"#FFFFFF","accent":"#4B5563","accent2":"#374151",
                    "text_main":"#111827","text_sub":"#6B7280","badge_bg":"#4B5563",
                    "badge_text":"#FFFFFF","highlight":"#E5E7EB","bar":"#4B5563"},
}

# ── Category detection ─────────────────────────────────────────────────────────
CATEGORY_RULES = [
    ("bundle",      ["bundle", "complete life", "complete finance", "complete health",
                     "freelancer os", "business starter kit", "productivity os"]),
    ("finance",     ["budget", "invoice", "cash flow", "profit", "debt", "finance",
                     "expense", "revenue", "payoff", "tax", "financial", "money"]),
    ("business",    ["kpi", "dashboard", "marketing", "sales", "ecommerce", "dropship",
                     "restaurant", "construction", "law firm", "inventory", "hr",
                     "employee", "supply chain", "etsy shop", "amazon", "real estate",
                     "startup", "nonprofit", "church", "virtual assistant", "freelance"]),
    ("health",      ["workout", "fitness", "gym", "meal", "food", "grocery", "nutrition",
                     "keto", "weight", "sleep", "pregnancy", "marathon", "mental health",
                     "habit", "wellness", "health", "body", "calorie", "bmi"]),
    ("productivity",["planner", "weekly", "student", "goal", "project", "annual",
                     "certification", "skill", "tutor", "online course", "job application",
                     "travel", "event", "family", "car maintenance", "school", "thesis",
                     "pet", "stock", "trading", "youtube", "content", "social media",
                     "time tracking", "timesheet", "artist", "musician", "author"]),
]

BADGE_MAP = {
    "bundle":       "⭐ COMPLETE SYSTEM",
    "finance":      "💰 FINANCE TOOL",
    "business":     "◆ BUSINESS TOOL",
    "health":       "💪 HEALTH TOOL",
    "productivity": "🎯 PRODUCTIVITY",
    "default":      "⚡ DIGITAL TOOL",
}

FEATURES_MAP = {
    "bundle":       ["Multiple Systems in One File", "Instant Download — No Setup",
                     "Works on Phone, Tablet & Desktop", "Fully Customizable",
                     "Lifetime Access — No Subscription"],
    "finance":      ["Auto-Calculating Formulas", "Monthly & Annual Overview",
                     "Works on Phone, Tablet & Desktop", "Fully Customizable",
                     "Instant Download — Ready in 2 Min"],
    "business":     ["Real-Time Dashboard", "Auto-Updating Charts & Reports",
                     "Works on Any Device", "Fully Customizable Fields",
                     "Instant Download — No Setup"],
    "health":       ["Progress Tracking Charts", "Auto-Calculating Results",
                     "Works on Phone, Tablet & Desktop", "Fully Customizable",
                     "Instant Download — Start Today"],
    "productivity": ["Weekly & Monthly Views", "Auto-Calculating Formulas",
                     "Works on Phone, Tablet & Desktop", "Fully Customizable",
                     "Instant Download — Ready in 2 Min"],
    "default":      ["Auto-Calculating Formulas", "Works on Any Device",
                     "Fully Customizable", "Lifetime Access",
                     "Instant Download — Ready in 2 Min"],
}

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
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    for pattern in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(pattern, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def get_category(title):
    tl = title.lower()
    for cat, keywords in CATEGORY_RULES:
        if any(k in tl for k in keywords):
            return cat
    return "default"

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

def make_listing_thumbnail(listing_id, title, category):
    p       = PALETTES[category]
    badge   = BADGE_MAP[category]
    feats   = FEATURES_MAP[category]

    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb(p["bg"]))
    draw = ImageDraw.Draw(img)

    f_title  = load_font(110)
    f_sub    = load_font(58)
    f_badge  = load_font(44)
    f_check  = load_font(56)
    f_cta    = load_font(68)
    f_small  = load_font(38)

    # Badge
    try:
        bbox = f_badge.getbbox(badge)
        bw   = bbox[2]-bbox[0]+48
        bh   = bbox[3]-bbox[1]+24
    except:
        bw, bh = 300, 60
    draw_rounded_rect(draw,(80,80,80+bw,80+bh),14,hex2rgb(p["badge_bg"]))
    draw.text((80+24,80+12-bbox[1]),badge,font=f_badge,fill=hex2rgb(p["badge_text"]))

    # Title (word-wrap)
    clean_title = re.sub(r'\|.*','',title).strip()[:60]
    lines = wrap_text(clean_title.upper(), f_title, SIZE-160)[:2]
    title_y = 200
    for i, ln in enumerate(lines):
        try:
            bbox = f_title.getbbox(ln)
            x = (SIZE-(bbox[2]-bbox[0]))//2
        except:
            x = 80
        draw.text((x, title_y + i*130), ln, font=f_title, fill=hex2rgb(p["text_main"]))

    # Subtitle line
    sub_y = title_y + len(lines)*130 + 30
    sub   = "Google Sheets Template"
    try:
        bbox = f_sub.getbbox(sub)
        x = (SIZE-(bbox[2]-bbox[0]))//2
    except:
        x = 80
    draw.text((x, sub_y), sub, font=f_sub, fill=hex2rgb(p["accent"]))

    # Divider
    div_y = sub_y + 90
    draw.rectangle([80,div_y,SIZE-80,div_y+6], fill=hex2rgb(p["accent"]))

    # Features
    feat_y = div_y + 70
    for i, feat in enumerate(feats[:5]):
        y = feat_y + i*110
        # Bullet circle
        draw.ellipse([80,y+8,80+46,y+54], fill=hex2rgb(p["accent"]))
        try:
            draw.text((93,y+8),"✓",font=f_check,fill=hex2rgb(p["bg"]))
        except:
            pass
        draw.text((146,y), feat, font=f_check, fill=hex2rgb(p["text_sub"]))

    # CTA bar
    cta_y = SIZE-190
    draw_rounded_rect(draw,(80,cta_y,SIZE-80,cta_y+118),22,hex2rgb(p["accent"]))
    cta = "⚡ INSTANT DOWNLOAD"
    try:
        bbox = f_cta.getbbox(cta)
        x = (SIZE-(bbox[2]-bbox[0]))//2
    except:
        x = 200
    draw.text((x,cta_y+22),cta,font=f_cta,fill=hex2rgb(p["bg"] if p["bg"]!="#0F172A" else "#0F172A"))

    # Watermark
    wm = "nasritools.etsy.com"
    try:
        bbox = f_small.getbbox(wm)
        draw.text((SIZE-bbox[2]-bbox[0]-60, SIZE-52), wm, font=f_small, fill=hex2rgb(p["text_sub"]))
    except:
        pass

    path = OUT_DIR / f"listing_{listing_id}.png"
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
    return r.ok,r.status_code

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*65)
    print("  NasriTools — Generate & Upload ALL Thumbnails")
    print("="*65)
    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings found\n")

    ok=fail=0
    for idx,l in enumerate(listings,1):
        lid   = l["listing_id"]
        title = l["title"]
        cat   = get_category(title)

        print(f"  [{idx:3}/{len(listings)}] [{cat:12}] {title[:38]}...", end=" ", flush=True)

        # Generate image
        try:
            img_path = make_listing_thumbnail(lid, title, cat)
        except Exception as e:
            print(f"GEN-FAIL ({e})")
            fail+=1
            continue

        # Delete old + upload new
        token = get_token()
        delete_images(token,lid)
        time.sleep(0.3)
        token = get_token()
        r_ok,code = upload_image(token,lid,img_path)
        if r_ok:
            print("OK")
            ok+=1
        else:
            print(f"UPLOAD-FAIL ({code})")
            fail+=1
        time.sleep(1)

    print(f"\n{'='*65}")
    print(f"  Done: {ok} OK | {fail} failed")
    print(f"  Images saved in: {OUT_DIR.resolve()}")
    print(f"{'='*65}")

if __name__=="__main__":
    main()
