"""
generate_listing_videos.py

Creates 5-12 second animated videos for hero listings.
Each video = 7 frames showing: brand intro → title → spreadsheet data → features → CTA
Tries MP4 via imageio, falls back to animated GIF.
Uploads to Etsy at rank 1 (replaces as video slot).
"""
import json, os, glob, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
OUT_DIR    = Path("thumbnails/videos")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SZ         = 1080   # 1080x1080 square

TARGET_KEYWORDS = [
    "budget tracker", "invoice tracker", "kpi dashboard",
    "workout tracker", "weekly planner",
]

CATEGORY_DATA = {
    "finance":      {"accent":"#2563EB","label":"Finance & Budget",
                     "rows":[("INCOME","3,200"),("Rent","1,200"),("Food","420"),
                              ("Bills","95"),("Savings","420"),("BALANCE","1,305")]},
    "invoice":      {"accent":"#0EA5E9","label":"Invoice Tracker",
                     "rows":[("Client A","2,500"),("Client B","1,800"),("Client C","900"),
                              ("Client D","3,200"),("Pending","1,200"),("TOTAL","9,600")]},
    "kpi":          {"accent":"#0EA5E9","label":"Business KPIs",
                     "rows":[("Revenue","+24%"),("Leads","340"),("Conv Rate","4.2%"),
                              ("Avg Deal","€420"),("Pipeline","€18k"),("GROWTH","24%")]},
    "fitness":      {"accent":"#059669","label":"Health & Fitness",
                     "rows":[("Workouts","4/week"),("Calories","1,850"),("Weight","-4.2kg"),
                              ("Sleep","7.2h"),("Steps","9,400"),("STREAK","21 days")]},
    "productivity": {"accent":"#7C3AED","label":"Planners & Goals",
                     "rows":[("Tasks Done","94%"),("Goals","3/3"),("Focus","6.2h"),
                              ("Meetings","4"),("Deep Work","3h"),("WEEK","7/7")]},
}

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def load_font(size):
    for c in ["arialbd.ttf","calibrib.ttf","arial.ttf",
              "C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(c, size)
        except: continue
    for p in ["C:/Windows/Fonts/*.ttf","/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(p, recursive=True):
            try: return ImageFont.truetype(f, size)
            except: continue
    try: return ImageFont.load_default(size=size)
    except: return ImageFont.load_default()

def ctext(draw, text, font, y, color, width=SZ):
    try:
        bb = font.getbbox(text)
        x = max(20, (width-(bb[2]-bb[0]))//2)
        draw.text((x, y-bb[1]), text, font=font, fill=color)
    except: pass

def dark_bg(draw, accent):
    ac = hex2rgb(accent)
    for i in range(SZ):
        t = i/SZ
        draw.rectangle([0,i,SZ,i+1], fill=(int(10+t*15), int(20+t*22), int(38+t*32)))
    # subtle glow
    for r in range(400, 0, -30):
        t2 = 1 - r/400
        shade = (int(ac[0]*t2*0.1), int(ac[1]*t2*0.12), int(10+ac[2]*t2*0.22))
        draw.ellipse([SZ//2-r, SZ//2-r, SZ//2+r, SZ//2+r], fill=shade)

def make_frames(title, data):
    accent = data["accent"]
    label  = data["label"]
    rows   = data["rows"]
    clean  = title.split("|")[0].strip()
    if len(clean) > 28: clean = clean[:26]+"..."

    f_brand = load_font(52)
    f_title = load_font(88)
    f_sub   = load_font(46)
    f_hdr   = load_font(34)
    f_row   = load_font(38)
    f_feat  = load_font(42)
    f_cta   = load_font(58)
    f_wm    = load_font(32)

    frames = []

    # ── Frame 1: Brand intro ──────────────────────────────────────
    img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
    dark_bg(d, accent)
    d.rectangle([0,0,SZ,8], fill=hex2rgb(accent))
    ctext(d, "NASRITOOLS", f_brand, SZ//2-80, hex2rgb(accent))
    ctext(d, "Google Sheets Templates", f_sub, SZ//2+20, hex2rgb("#94A3B8"))
    frames.extend([img]*3)  # hold 1.5s at 2fps

    # ── Frame 2: Product title ────────────────────────────────────
    img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
    dark_bg(d, accent)
    d.rectangle([0,0,SZ,8], fill=hex2rgb(accent))
    ctext(d, label.upper(), f_sub, SZ//2-140, hex2rgb(accent))
    ctext(d, clean.upper(), f_title, SZ//2-40, (255,255,255))
    ctext(d, "Google Sheets Template", f_sub, SZ//2+110, hex2rgb("#94A3B8"))
    frames.extend([img]*3)  # 1.5s

    # ── Frame 3: Spreadsheet header only ─────────────────────────
    img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
    dark_bg(d, accent)
    sx,sy,sw,sh = 60,100,SZ-120,720
    d.rectangle([sx,sy,sx+sw,sy+sh], fill=(255,255,255))
    d.rectangle([sx,sy,sx+sw,sy+52], fill=hex2rgb(accent))
    ctext(d, "CATEGORY", f_hdr, sy+12, (255,255,255))
    try: d.text((sx+sw-240, sy+12), "AMOUNT", font=f_hdr, fill=(255,255,255))
    except: pass
    frames.extend([img]*2)  # 1s

    # ── Frames 4-6: Rows fill in progressively ────────────────────
    for n_rows in [2, 4, len(rows)]:
        img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
        dark_bg(d, accent)
        d.rectangle([sx,sy,sx+sw,sy+sh], fill=(255,255,255))
        d.rectangle([sx,sy,sx+sw,sy+52], fill=hex2rgb(accent))
        ctext(d, "CATEGORY", f_hdr, sy+12, (255,255,255))
        try: d.text((sx+sw-240, sy+12), "AMOUNT", font=f_hdr, fill=(255,255,255))
        except: pass

        rh = 96
        for i, (cat, val) in enumerate(rows[:n_rows]):
            ry = sy + 52 + i*rh
            is_total = i == len(rows)-1
            row_bg = hex2rgb("#D1FAE5") if is_total else (
                     hex2rgb("#F1F5F9") if i%2==0 else (255,255,255))
            d.rectangle([sx,ry,sx+sw,ry+rh], fill=row_bg)
            d.rectangle([sx,ry+rh-1,sx+sw,ry+rh], fill=hex2rgb("#E2E8F0"))
            try:
                d.text((sx+16, ry+28), cat, font=f_row,
                      fill=hex2rgb(accent) if is_total else hex2rgb("#1E293B"))
                vb = f_row.getbbox(val)
                d.text((sx+sw-(vb[2]-vb[0])-16, ry+28), val, font=f_row,
                      fill=hex2rgb(accent) if is_total else hex2rgb("#1E293B"))
            except: pass
        frames.extend([img]*2)  # 1s each

    # ── Frame 7: Feature highlights ───────────────────────────────
    img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
    dark_bg(d, accent)
    d.rectangle([0,0,SZ,8], fill=hex2rgb(accent))
    ctext(d, "WHAT YOU GET", f_sub, 80, hex2rgb(accent))

    feats = [
        "Auto-Calculating Formulas",
        "Works on Any Device",
        "Instant Download",
        "Fully Customizable",
    ]
    for i, feat in enumerate(feats):
        fy = 200 + i*180
        d.ellipse([80,fy,148,fy+68], fill=hex2rgb(accent))
        try: d.text((98,fy+10), "v", font=f_feat, fill=(255,255,255))
        except: pass
        try: d.text((168,fy+12), feat, font=f_feat, fill=(255,255,255))
        except: pass
    frames.extend([img]*3)  # 1.5s

    # ── Frame 8: CTA ──────────────────────────────────────────────
    img = Image.new("RGB", (SZ,SZ)); d = ImageDraw.Draw(img)
    dark_bg(d, accent)
    d.rectangle([0,0,SZ,8], fill=hex2rgb(accent))
    ctext(d, clean.upper(), f_sub, 200, hex2rgb("#94A3B8"))
    ctext(d, "EUR 0.20", f_title, 340, (255,255,255))
    ctext(d, "INSTANT DOWNLOAD", f_cta, 520, hex2rgb(accent))
    d.rectangle([80,650,SZ-80,720], fill=hex2rgb(accent))
    ctext(d, "Download Now  |  nasritools.etsy.com", f_sub, 668, (255,255,255))
    ctext(d, "nasritools.etsy.com", f_wm, SZ-50, hex2rgb("#334155"))
    frames.extend([img]*4)  # 2s

    return frames  # Total at 2fps ≈ (3+3+2+2+2+2+3+4)/2 = 10.5s ✓


def save_as_gif(frames, path):
    """Save frames as animated GIF."""
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=500,   # 500ms per frame = 2fps
        loop=0,
        optimize=False,
    )

def save_as_mp4(frames, path):
    """Try to save as MP4 using imageio. Returns True if successful."""
    try:
        import imageio
        import numpy as np
        mp4_path = str(path).replace(".gif",".mp4")
        writer = imageio.get_writer(mp4_path, fps=2, quality=8, macro_block_size=None)
        for frame in frames:
            writer.append_data(np.array(frame.convert("RGB")))
        writer.close()
        return Path(mp4_path), True
    except Exception as e:
        print(f"    MP4 failed ({e}) — using GIF")
        return path, False


# ── API ───────────────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at",0)-60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token",data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,
            "refresh_token":t["refresh_token"]})
        r.raise_for_status(); t=r.json()
        t["expires_at"]=time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t,indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],"x-api-key":CLIENT_ID+":"+SECRET}

def get_all_listings(token):
    listings,offset=[],0
    while True:
        r=requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                      headers=auth_headers(token),params={"limit":100,"offset":offset})
        if not r.ok: break
        results=r.json().get("results",[])
        listings.extend(results)
        if len(results)<100: break
        offset+=100; time.sleep(0.3)
    return listings

def upload_video(token, lid, path):
    """Upload MP4 or GIF as listing video."""
    mime = "video/mp4" if str(path).endswith(".mp4") else "image/gif"
    try:
        with open(path,"rb") as f:
            r = requests.post(
                f"{API}/shops/{SHOP_ID}/listings/{lid}/videos",
                headers=auth_headers(token),
                files={"video":(path.name,f,mime)},
                timeout=120)
        return r.ok, r.status_code, r.text[:100]
    except Exception as e:
        return False, 0, str(e)

def get_category(title):
    tl = title.lower()
    if any(k in tl for k in ["budget","expense","finance","cash"]): return "finance"
    if any(k in tl for k in ["invoice","billing","freelancer"]):    return "invoice"
    if any(k in tl for k in ["kpi","dashboard","business"]):        return "kpi"
    if any(k in tl for k in ["workout","fitness","health","meal"]):  return "fitness"
    return "productivity"

def match_listing(listings, keyword):
    for l in listings:
        if keyword.lower() in l["title"].lower(): return l
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("="*60)
    print("  NasriTools — Listing Videos")
    print("  7-frame animation | 10-11 seconds | MP4 or GIF")
    print("="*60)

    token    = get_token()
    listings = get_all_listings(token)
    print(f"[*] {len(listings)} listings\n")

    ok = fail = 0
    for kw in TARGET_KEYWORDS:
        l = match_listing(listings, kw)
        if not l:
            print(f"  [SKIP] '{kw}' not found"); continue

        lid   = l["listing_id"]
        title = l["title"]
        cat   = get_category(title)
        data  = CATEGORY_DATA[cat]
        print(f"  [{kw}] {title[:42]}...")

        # Generate frames
        try:
            frames = make_frames(title, data)
            print(f"    {len(frames)} frames generated", end=" ")
        except Exception as e:
            print(f"    GEN-FAIL: {e}")
            fail += 1; continue

        # Try MP4, fall back to GIF
        gif_path = OUT_DIR / f"video_{lid}.gif"
        video_path, is_mp4 = save_as_mp4(frames, gif_path)
        if not is_mp4:
            save_as_gif(frames, gif_path)
            video_path = gif_path
        fmt = "MP4" if is_mp4 else "GIF"
        print(f"→ {fmt}", end=" ")

        # Upload to Etsy
        token = get_token()
        v_ok, code, txt = upload_video(token, lid, video_path)
        if v_ok:
            print(f"→ Uploaded ✅")
            ok += 1
        else:
            print(f"→ Upload FAIL ({code}): {txt}")
            fail += 1
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"  Done: {ok} OK | {fail} failed")
    print(f"  Saved in: {OUT_DIR.resolve()}")
    if fail > 0:
        print(f"\n  If upload failed, manually upload GIF/MP4 files from:")
        print(f"  Shop Manager → Edit Listing → Add Video")
    print(f"{'='*60}")

if __name__=="__main__":
    main()
