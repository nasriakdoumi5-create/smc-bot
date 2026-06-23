"""
create_free_listing.py
Creates a free Budget Tracker Lite listing on Etsy (€0.20).
Generates thumbnail, uploads file + image, then activates.
"""
import json, os, time, requests, urllib.parse, io, glob, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

TITLE = "Budget Tracker Google Sheets FREE | Monthly Budget & Expense Tracker Starter"

DESCRIPTION = """⚡ FREE DOWNLOAD — No catch, no email required. Just click and use.

★★★★★ WHAT YOU GET (FREE VERSION):
✓ 3-Month Budget Tracker (Jan–Mar)
✓ Income & Expense Categories
✓ Auto-Calculating Totals
✓ Monthly Summary Overview
✓ Works on Google Sheets (free)

─────────────────────────────────
HOW TO USE:
1. Click the file to download
2. Open Google Sheets
3. File → Import → Upload the file
4. Start tracking immediately
─────────────────────────────────

📱 Works on Phone, Tablet & Desktop
🔓 No subscription, no account needed
✏️ Fully editable — change any category

─────────────────────────────────
WANT THE FULL VERSION?
The complete Budget Tracker includes:
✓ Full 12-Month Tracker
✓ Annual Summary Dashboard
✓ Savings & Debt Payoff Tracker
✓ Income vs Expense Charts
✓ Bill Payment Calendar

→ Visit our shop: nasritools.etsy.com
─────────────────────────────────

Questions? Message us — we reply within 24 hours.
© NasriTools — Professional Google Sheets Templates"""

TAGS = [
    "budget tracker", "free budget", "google sheets",
    "expense tracker", "monthly budget", "free template",
    "budget spreadsheet", "free download", "personal finance",
    "money tracker", "free planner", "budget tool", "finance tracker"
]

FREE_FILE_CONTENT = """NASRITOOLS — Budget Tracker Google Sheets (FREE Starter Version)
================================================================

Thank you for downloading! Here's how to get started:

STEP 1: Open this link in your browser (Google Sheets template):
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms/copy
(This opens a pre-built template — click "Make a copy")

STEP 2: Save it to your Google Drive

STEP 3: Start filling in your income and expenses!

================================================================
WHAT'S INCLUDED IN THIS FREE VERSION:
- 3-Month Budget Tracker (January to March)
- Income & Expense categories (fully editable)
- Auto-calculating totals
- Monthly overview summary

================================================================
WANT THE COMPLETE VERSION? (12 months + charts + debt tracker)
→ https://nasritools.etsy.com

We have 118 templates for Finance, Business, Health & Productivity.
Use code WELCOME10 for 10% off your first purchase.

================================================================
NEED HELP?
Message us on Etsy — we reply within 24 hours.
nasritools.etsy.com

© NasriTools — Professional Google Sheets Templates
================================================================
"""

SIZE = 2000
OUT_DIR = Path("thumbnails/free")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(size):
    for c in ["arialbd.ttf","calibrib.ttf","C:/Windows/Fonts/arialbd.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try: return ImageFont.truetype(c, size)
        except: continue
    for p in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(p, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def draw_rounded_rect(draw, xy, r, fill):
    x0,y0,x1,y1 = xy
    draw.rectangle([x0+r,y0,x1-r,y1],fill=fill)
    draw.rectangle([x0,y0+r,x1,y1-r],fill=fill)
    for cx,cy in [(x0,y0),(x1-r*2,y0),(x0,y1-r*2),(x1-r*2,y1-r*2)]:
        draw.ellipse([cx,cy,cx+r*2,cy+r*2],fill=fill)

def make_free_thumbnail(lid):
    bg, accent, card = "#F8FAFF", "#2563EB", "#FFFFFF"
    text_main, text_sub = "#1B2A4A", "#475569"
    star_color = "#F59E0B"

    img  = Image.new("RGB", (SIZE,SIZE), hex2rgb(bg))
    draw = ImageDraw.Draw(img)

    f_badge = load_font(48); f_title = load_font(112)
    f_sub   = load_font(58); f_free  = load_font(160)
    f_check = load_font(58); f_cta   = load_font(68)
    f_small = load_font(38); f_stars = load_font(72)

    # FREE badge (top left)
    badge = "🎁 FREE DOWNLOAD"
    try:
        bb = f_badge.getbbox(badge); bw = bb[2]-bb[0]+56; bh = bb[3]-bb[1]+28
    except: bw,bh = 380,70
    draw_rounded_rect(draw,(80,80,80+bw,80+bh),16,hex2rgb("#059669"))
    draw.text((80+28,80+14-bb[1]),badge,font=f_badge,fill=(255,255,255))

    # Stars (top right)
    try:
        sb = f_stars.getbbox("★★★★★")
        draw.text((SIZE-80-(sb[2]-sb[0]),80),"★★★★★",font=f_stars,fill=hex2rgb(star_color))
        rb = f_small.getbbox("100% Free — No Email")
        draw.text((SIZE-80-(rb[2]-rb[0]),80+90),"100% Free — No Email",font=f_small,fill=hex2rgb(text_sub))
    except: pass

    # Big FREE text
    try:
        fb = f_free.getbbox("FREE")
        draw.text(((SIZE-(fb[2]-fb[0]))//2, 200), "FREE", font=f_free, fill=hex2rgb(accent))
    except: pass

    # Title
    title = "BUDGET TRACKER"
    try:
        tb = f_title.getbbox(title)
        draw.text(((SIZE-(tb[2]-tb[0]))//2, 380), title, font=f_title, fill=hex2rgb(text_main))
    except: pass

    sub = "Google Sheets Template"
    try:
        sb2 = f_sub.getbbox(sub)
        draw.text(((SIZE-(sb2[2]-sb2[0]))//2, 510), sub, font=f_sub, fill=hex2rgb(accent))
    except: pass

    # Divider
    draw.rectangle([80,600,SIZE-80,606],fill=hex2rgb(accent))

    # Features
    feats = ["Monthly Budget & Expense Tracker",
             "Auto-Calculating Formulas",
             "Income vs Expense Overview",
             "Works on Phone & Desktop",
             "No Signup — Instant Access"]
    for i, feat in enumerate(feats):
        y = 640 + i*110
        draw.ellipse([80,y+6,126,y+52],fill=hex2rgb(accent))
        try: draw.text((93,y+6),"✓",font=f_check,fill=hex2rgb(bg))
        except: pass
        draw.text((146,y),feat,font=f_check,fill=hex2rgb(text_sub))

    # CTA
    cta_y = SIZE-188
    draw_rounded_rect(draw,(80,cta_y,SIZE-80,cta_y+116),22,hex2rgb(accent))
    cta = "⬇ DOWNLOAD FOR FREE"
    try:
        cb = f_cta.getbbox(cta)
        draw.text(((SIZE-(cb[2]-cb[0]))//2, cta_y+22), cta, font=f_cta, fill=(255,255,255))
    except: pass

    wm = "nasritools.etsy.com"
    try:
        wb = f_small.getbbox(wm)
        draw.text((SIZE-wb[2]-wb[0]-60,SIZE-52),wm,font=f_small,fill=hex2rgb(text_sub))
    except: pass

    path = OUT_DIR / f"free_{lid}.png"
    img.save(path,"PNG",quality=95)
    return path

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

def get_active_listing_meta(token):
    r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                     headers=auth_headers(token), params={"limit": 1})
    if r.ok:
        results = r.json().get("results", [])
        if results:
            l = results[0]
            return l.get("return_policy_id"), l.get("shipping_profile_id")
    return None, None

def create_listing(token, return_policy_id, shipping_profile_id):
    tags_str = "&".join(f"tags[]={urllib.parse.quote(t, safe='')}" for t in TAGS[:13])
    data = (
        f"title={urllib.parse.quote(TITLE)}"
        f"&description={urllib.parse.quote(DESCRIPTION)}"
        f"&price=0.20"
        f"&quantity=999"
        f"&who_made=i_did"
        f"&when_made=2020_2025"
        f"&taxonomy_id=2078"
        f"&type=download"
        f"&is_digital=true"
        f"&{tags_str}"
    )
    if return_policy_id:
        data += f"&return_policy_id={return_policy_id}"
    if shipping_profile_id:
        data += f"&shipping_profile_id={shipping_profile_id}"

    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data=data, timeout=30,
    )
    return r.ok, r.status_code, r.json() if r.ok else r.text[:300]

def upload_file(token, lid):
    content = FREE_FILE_CONTENT.encode("utf-8")
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
        headers=auth_headers(token),
        files={"file": ("Budget_Tracker_FREE_NasriTools.txt",
                        io.BytesIO(content), "text/plain")},
        data={"name": "Budget_Tracker_FREE_NasriTools.txt", "rank": 1},
        timeout=60,
    )
    return r.ok, r.status_code

def upload_image(token, lid, path):
    with open(path,"rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
            headers=auth_headers(token),
            files={"image":(path.name,f,"image/png")},
            data={"rank":1}, timeout=60,
        )
    return r.ok, r.status_code

def activate_listing(token, lid):
    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
        data="state=active", timeout=30,
    )
    return r.ok, r.status_code, r.text[:200]

def main():
    print("=" * 65)
    print("  NasriTools — Create Free Budget Tracker Listing")
    print("=" * 65)

    token = get_token()

    # Listing 4526750401 already created in previous run — skip creation
    EXISTING_LID = 4526750401

    if EXISTING_LID:
        lid = EXISTING_LID
        print(f"[*] Using existing listing_id={lid}")
    else:
        print("[1] Fetching return policy...")
        rp_id, sp_id = get_active_listing_meta(token)
        print(f"    return_policy_id={rp_id} | shipping_profile_id={sp_id}")

        print("[2] Creating listing...")
        token = get_token()
        ok, code, result = create_listing(token, rp_id, sp_id)
        if not ok:
            print(f"    FAIL ({code}): {result}")
            return
        lid = result["listing_id"]
        print(f"    OK — listing_id={lid}")
        time.sleep(2)

        print("[3] Uploading digital file...")
        token = get_token()
        f_ok, f_code = upload_file(token, lid)
        print(f"    {'OK' if f_ok else f'FAIL ({f_code})'}")
        time.sleep(2)

    print("[4] Generating FREE thumbnail...")
    try:
        img_path = make_free_thumbnail(lid)
        print(f"    OK — {img_path}")
    except Exception as e:
        print(f"    FAIL: {e}")
        return

    print("[5] Uploading image...")
    token = get_token()
    i_ok, i_code = upload_image(token, lid, img_path)
    print(f"    {'OK' if i_ok else f'FAIL ({i_code})'}")
    if not i_ok:
        return
    time.sleep(2)

    print("[6] Activating listing...")
    token = get_token()
    a_ok, a_code, a_text = activate_listing(token, lid)
    if a_ok:
        print(f"    OK ✅ — LIVE!")
        print(f"\n  ✅ Listing URL: https://www.etsy.com/listing/{lid}")
    else:
        print(f"    FAIL ({a_code}): {a_text[:150]}")

    print("=" * 65)

if __name__ == "__main__":
    main()
