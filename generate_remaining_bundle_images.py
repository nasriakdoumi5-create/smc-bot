"""
generate_remaining_bundle_images.py
Adds rank 2, 3, 4 images to the 3 bundle listings that still have only 1 photo:
  4524283886  Finance Bundle   (blue)
  4524724758  Productivity Bundle (purple)
  4524724798  Business Bundle  (gold)
"""
import io, json, os, time, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

BUNDLES = [
    {
        "listing_id": 4524283886,
        "label":  "FINANCE BUNDLE",
        "badge":  "3 SYSTEMS  ·  SAVE 33%",
        "price":  "€19.99",
        "worth":  "worth €37",
        "color":  (30, 100, 200),
        "light":  (214, 234, 248),
        "dark":   (10, 50, 120),
        "items":  ["Budget & Expense Tracker", "Invoice & Client Manager", "Goals & 90-Day Planner"],
    },
    {
        "listing_id": 4524724758,
        "label":  "PRODUCTIVITY BUNDLE",
        "badge":  "3 SYSTEMS  ·  SAVE 50%",
        "price":  "€17.99",
        "worth":  "worth €36",
        "color":  (108, 52, 131),
        "light":  (237, 228, 252),
        "dark":   (55, 20, 75),
        "items":  ["Weekly Productivity System", "Student Academic Planner", "Goals & 90-Day Planner"],
    },
    {
        "listing_id": 4524724798,
        "label":  "BUSINESS BUNDLE",
        "badge":  "3 SYSTEMS  ·  SAVE 50%",
        "price":  "€21.99",
        "worth":  "worth €43",
        "color":  (195, 130, 20),
        "light":  (254, 243, 214),
        "dark":   (110, 70, 5),
        "items":  ["Content Creator System", "Invoice & Client Manager", "Budget & Expense Tracker"],
    },
]

_BOLD = [
    "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf",
    "C:/Windows/Fonts/verdanab.ttf", "C:/Windows/Fonts/trebucbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_REG = [
    "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/trebuc.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _f(p, s):
    for path in p:
        if Path(path).exists():
            return ImageFont.truetype(path, s)
    return ImageFont.load_default()

def fb(s): return _f(_BOLD, s)
def fr(s): return _f(_REG, s)
def mix(c1, c2, t): return tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
def tw(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font); return bb[2]-bb[0]
def th(draw, text, font):
    bb = draw.textbbox((0,0), text, font=font); return bb[3]-bb[1]

def pill(draw, x0, y0, x1, y1, fill, r=None):
    r = r or (y1-y0)//2
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)

def buf_out(img):
    buf = io.BytesIO(); img.save(buf, format="JPEG", quality=95); buf.seek(0); return buf

# ── Image 1: What's Included (rank 2) ─────────────────────────────────────────
def gen_whats_included(b):
    W, H = 2000, 2000
    color = b["color"]
    bg = mix(color, (0,0,0), 0.85)
    img = Image.new("RGB", (W,H), bg); draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,8], fill=color)
    draw.text((100,40), "NASRITOOLS", font=fb(36), fill=(255,255,255))
    draw.text((100,110), "WHAT'S INSIDE", font=fb(110), fill=(255,255,255))
    draw.rectangle([100,430,800,438], fill=color)

    font_label = fb(44); lbl = b["label"]
    lw_ = tw(draw, lbl, font_label); lh_ = th(draw, lbl, font_label)
    px0, py0 = 100, 450; px1, py1 = px0+lw_+72, py0+lh_+36
    pill(draw, px0, py0, px1, py1, fill=color)
    draw.text((px0+36, py0+18), lbl, font=font_label, fill=(255,255,255))

    font_price = fb(52); ptxt = b["price"]+" ("+b["worth"]+")"
    pw_ = tw(draw, ptxt, font_price)
    ppx0, ppy0 = W-pw_-136, py0; ppx1, ppy1 = W-100, py1
    pill(draw, ppx0, ppy0, ppx1, ppy1, fill=(255,255,255))
    draw.text((ppx0+36, ppy0+10), ptxt, font=font_price, fill=b["dark"])

    start_y = 590; row_h = 175; circle_d = 52; font_feat = fr(52)
    for i, item in enumerate(b["items"]):
        y = start_y + i*row_h; cx = 100+circle_d//2; cy = y+circle_d//2
        draw.ellipse([cx-circle_d//2, cy-circle_d//2, cx+circle_d//2, cy+circle_d//2], fill=color)
        ck = "✓"; font_ck = fb(36); cw = tw(draw, ck, font_ck); ch_ = th(draw, ck, font_ck)
        draw.text((cx-cw//2, cy-ch_//2), ck, font=font_ck, fill=(255,255,255))
        fh = th(draw, item, font_feat)
        draw.text((200, cy-fh//2), item, font=font_feat, fill=(255,255,255))

    draw.text(((W-tw(draw,"Instant Download  ·  Lifetime Access  ·  Free Updates",fr(38)))//2, 1900),
              "Instant Download  ·  Lifetime Access  ·  Free Updates", font=fr(38), fill=(200,200,200))
    url = "nasritools.etsy.com"; uw = tw(draw, url, fr(34))
    draw.text(((W-uw)//2, 1950), url, font=fr(34), fill=mix(color,(255,255,255),0.3))
    return buf_out(img)

# ── Image 2: Compatibility (rank 3) ───────────────────────────────────────────
def gen_compatibility(b):
    W, H = 2000, 2000; color = b["color"]; light = b["light"]
    img = Image.new("RGB", (W,H), (247,249,252)); draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,12], fill=color)
    draw.text((100,40), "WORKS ON EVERYTHING", font=fb(100), fill=(28,30,38))
    draw.text((100,195), "No software to install. Open your browser — you're ready.", font=fr(50), fill=(90,95,110))

    card_w, card_h, icon_h = 900, 500, 140
    positions = [(100,320),(1060,320),(100,880),(1060,880)]
    cards = [
        {"abbr":"GS","title":"Google Sheets","desc":"100% FREE — all features work"},
        {"abbr":"XL","title":"Microsoft Excel","desc":"Fully compatible"},
        {"abbr":"\U0001f4bb","title":"Mac & PC","desc":"Works in any browser"},
        {"abbr":"\U0001f4f1","title":"iPhone & Android","desc":"Free Google Sheets app"},
    ]
    for (cx,cy), card in zip(positions, cards):
        draw.rectangle([cx,cy,cx+card_w,cy+card_h], fill=(255,255,255))
        for off in range(4):
            draw.rectangle([cx+off,cy+off,cx+card_w-off,cy+card_h-off], outline=color)
        draw.rectangle([cx,cy,cx+card_w,cy+icon_h], fill=light)
        abw = tw(draw, card["abbr"], fb(56)); abh = th(draw, card["abbr"], fb(56))
        draw.text((cx+(card_w-abw)//2, cy+(icon_h-abh)//2), card["abbr"], font=fb(56), fill=color)
        tw_ = tw(draw, card["title"], fb(52))
        draw.text((cx+(card_w-tw_)//2, cy+icon_h+24), card["title"], font=fb(52), fill=(28,30,38))
        dw = tw(draw, card["desc"], fr(44)); tit_h = th(draw, card["title"], fb(52))
        draw.text((cx+(card_w-dw)//2, cy+icon_h+24+tit_h+20), card["desc"], font=fr(44), fill=(90,95,110))

    bby = 1440
    pill(draw, 100, bby, W-100, bby+130, color, 30)
    badge_txt = b["badge"]+"  —  "+b["price"]+" (retail "+b["worth"]+")"
    btw = tw(draw, badge_txt, fb(52))
    draw.text(((W-btw)//2, bby+32), badge_txt, font=fb(52), fill=(255,255,255))
    url = "nasritools.etsy.com"; uw = tw(draw, url, fr(38))
    draw.text(((W-uw)//2, 1900), url, font=fr(38), fill=color)
    return buf_out(img)

# ── Image 3: How It Works (rank 4) ────────────────────────────────────────────
def gen_how_it_works(b):
    W, H = 2000, 2000; color = b["color"]; darker = mix(color,(0,0,0),0.30)
    img = Image.new("RGB", (W,H), color); draw = ImageDraw.Draw(img)
    draw.polygon([(W,0),(W-600,0),(W,600)], fill=darker)
    draw.text((100,80), "READY IN 2 MINUTES", font=fb(100), fill=(255,255,255))
    draw.text((100,225), "From purchase to using it — in under 120 seconds.",
              font=fr(52), fill=mix((255,255,255),color,0.20))

    steps = [
        {"num":"1","title":"PURCHASE","desc":["Click buy — instant","confirmation"]},
        {"num":"2","title":"OPEN LINK","desc":["PDF arrives instantly with","your Google Sheets link"]},
        {"num":"3","title":"START","desc":["File → Make a Copy","→ yours forever"]},
    ]
    col_w = 620; lm = 70; step_top = 400; cr = 90
    for i, step in enumerate(steps):
        col_cx = lm + i*col_w + col_w//2; cir_y = step_top+40
        draw.ellipse([col_cx-cr, cir_y, col_cx+cr, cir_y+2*cr], fill=(255,255,255))
        nw = tw(draw, step["num"], fb(100)); nh = th(draw, step["num"], fb(100))
        draw.text((col_cx-nw//2, cir_y+cr-nh//2), step["num"], font=fb(100), fill=color)
        title_y = cir_y+2*cr+40; stw = tw(draw, step["title"], fb(72))
        draw.text((col_cx-stw//2, title_y), step["title"], font=fb(72), fill=(255,255,255))
        desc_col = mix((255,255,255), color, 0.15)
        desc_y = title_y + th(draw, step["title"], fb(72)) + 20
        for line in step["desc"]:
            lw_ = tw(draw, line, fr(50))
            draw.text((col_cx-lw_//2, desc_y), line, font=fr(50), fill=desc_col)
            desc_y += th(draw, line, fr(50)) + 10

    box_y = 1100; box_bg = mix(color,(255,255,255),0.12)
    draw.rectangle([100,box_y,W-100,box_y+280], fill=box_bg)
    draw.rectangle([100,box_y,W-100,box_y+6], fill=(255,255,255))
    sv_txt = b["badge"]; svw = tw(draw, sv_txt, fb(88))
    draw.text(((W-svw)//2, box_y+20), sv_txt, font=fb(88), fill=(255,255,255))
    pr_txt = b["price"]+"   (retail "+b["worth"]+")"
    prw = tw(draw, pr_txt, fr(56))
    draw.text(((W-prw)//2, box_y+140), pr_txt, font=fr(56),
              fill=mix((255,255,255),color,0.20))

    draw.rectangle([100,1440,W-100,1442], fill=(255,255,255))
    badges = ["✓ Instant Delivery","✓ Lifetime Access","✓ Free Updates","✓ 24h Support"]
    font_tr = fr(52); gap = 60
    bws = [tw(draw, bx, font_tr) for bx in badges]
    total_w = sum(bws)+gap*(len(badges)-1); bx_cur = (W-total_w)//2; by_cur = 1490
    for bdg, bw in zip(badges, bws):
        draw.text((bx_cur, by_cur), bdg, font=font_tr, fill=(255,255,255)); bx_cur += bw+gap

    url = "nasritools.etsy.com"; uw = tw(draw, url, fr(42))
    draw.text(((W-uw)//2, 1880), url, font=fr(42), fill=mix((255,255,255),color,0.40))
    return buf_out(img)

# ── Etsy API ───────────────────────────────────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type":"refresh_token","client_id":CLIENT_ID,"refresh_token":t["refresh_token"],
        }); r.raise_for_status()
        t = r.json(); t["expires_at"] = time.time()+t.get("expires_in",3600)-60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization":"Bearer "+token["access_token"],"x-api-key":CLIENT_ID+":"+SECRET}

def upload_image(token, lid, buf, rank):
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}/images",
        headers=auth_headers(token),
        files={"image":("image.jpg", buf, "image/jpeg")},
        data={"rank":rank,"overwrite":"true"}, timeout=60,
    ); return r.ok, r.status_code

def main():
    print("="*65); print("  NasriTools — Remaining Bundle Extra Images (rank 2,3,4)")
    print("="*65)
    token = get_token(); print("[*] Token OK\n")
    generators = [(2,"What's Included",gen_whats_included),(3,"Compatibility",gen_compatibility),(4,"How It Works",gen_how_it_works)]
    ok_total = 0; fail_total = 0
    for b in BUNDLES:
        lid = b["listing_id"]
        print(f"Bundle: {b['label']}  [{lid}]")
        token = get_token()
        for rank, label, gen_fn in generators:
            print(f"  rank {rank} ({label}) ...", end=" ", flush=True)
            buf = gen_fn(b)
            ok, code = upload_image(token, lid, buf, rank)
            if ok: print(f"OK (HTTP {code})"); ok_total += 1
            else:  print(f"FAILED (HTTP {code})"); fail_total += 1
            time.sleep(1.5)
        print(f"  → https://www.etsy.com/listing/{lid}\n")
    print("="*65); print(f"  Done: {ok_total} OK, {fail_total} failed"); print("="*65)

if __name__ == "__main__":
    main()
