"""
NasriTools - Etsy Product Mockup Generator
Creates laptop-screen mockup images (2000x2000px) for all 10 products
No authentication needed — runs fully offline
Run: python make_mockups.py
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import os

IMAGES_DIR  = Path(os.path.expanduser("~")) / "nasri_hero_images"
MOCKUPS_DIR = Path(os.path.expanduser("~")) / "nasri_mockups"
MOCKUPS_DIR.mkdir(exist_ok=True)

SIZE = 2000  # square for Etsy

PRODUCTS = [
    {"slug": "budget_tracker",             "hero": "budget_tracker_01_hero.jpg",             "label": "Budget Tracker",             "color": (34,139,87)},
    {"slug": "habit_tracker",              "hero": "habit_tracker_01_hero.jpg",              "label": "Habit Tracker",              "color": (108,67,176)},
    {"slug": "meal_planner",               "hero": "meal_planner_01_hero.jpg",               "label": "Meal Planner",               "color": (214,90,49)},
    {"slug": "wedding_planner",            "hero": "wedding_planner_01_hero.jpg",            "label": "Wedding Planner",            "color": (185,50,100)},
    {"slug": "workout_tracker",            "hero": "workout_tracker_01_hero.jpg",            "label": "Workout Tracker",            "color": (30,100,180)},
    {"slug": "content_creator_planner",    "hero": "content_creator_planner_01_hero.jpg",    "label": "Content Creator Planner",    "color": (200,60,60)},
    {"slug": "freelancer_invoice_tracker", "hero": "freelancer_invoice_tracker_01_hero.jpg", "label": "Freelancer Invoice Tracker", "color": (20,120,140)},
    {"slug": "student_planner",            "hero": "student_planner_01_hero.jpg",            "label": "Student Planner",            "color": (50,130,70)},
    {"slug": "goals_planner",              "hero": "goals_planner_01_hero.jpg",              "label": "Goal Planner",               "color": (160,100,20)},
    {"slug": "weekly_planner",             "hero": "weekly_planner_01_hero.jpg",             "label": "Weekly Planner",             "color": (80,80,160)},
]

def load_font(size):
    for f in ["C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibrib.ttf",
              "C:/Windows/Fonts/segoeui.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_laptop(draw, img, screen_img, cx, cy, laptop_w, laptop_h, color):
    """Draw a laptop frame and paste screen_img inside."""
    r, g, b = color

    # ── Body (base of laptop) ──────────────────────────
    body_h = int(laptop_h * 0.07)
    body_y = cy + laptop_h // 2
    body_x0 = cx - int(laptop_w * 0.55)
    body_x1 = cx + int(laptop_w * 0.55)
    draw.rounded_rectangle([body_x0, body_y, body_x1, body_y+body_h],
                            radius=8, fill=(180,180,185))
    # base highlight
    draw.rectangle([body_x0+20, body_y, body_x1-20, body_y+4],
                   fill=(210,210,215))

    # ── Lid frame ──────────────────────────────────────
    lid_x0 = cx - laptop_w // 2
    lid_x1 = cx + laptop_w // 2
    lid_y0 = cy - laptop_h // 2
    lid_y1 = cy + laptop_h // 2
    draw.rounded_rectangle([lid_x0, lid_y0, lid_x1, lid_y1],
                            radius=18, fill=(195,195,200))

    # inner lid (slightly inset)
    pad = 10
    draw.rounded_rectangle([lid_x0+pad, lid_y0+pad, lid_x1-pad, lid_y1-pad],
                            radius=12, fill=(30,30,35))

    # ── Screen area ────────────────────────────────────
    screen_pad = 22
    sx0 = lid_x0 + screen_pad
    sy0 = lid_y0 + screen_pad
    sx1 = lid_x1 - screen_pad
    sy1 = lid_y1 - screen_pad
    sw  = sx1 - sx0
    sh  = sy1 - sy0

    # paste the product screen image
    screen_resized = screen_img.resize((sw, sh), Image.LANCZOS)
    img.paste(screen_resized, (sx0, sy0))

    # screen glare overlay
    glare = Image.new("RGBA", (sw, sh), (0,0,0,0))
    gd = ImageDraw.Draw(glare)
    for i in range(60):
        alpha = max(0, 30 - i)
        gd.line([(0, i), (i, 0)], fill=(255,255,255,alpha), width=1)
    img.paste(glare, (sx0, sy0), glare)

    # screen border glow
    draw.rounded_rectangle([sx0-2, sy0-2, sx1+2, sy1+2],
                            radius=4, outline=(r,g,b,180), width=3)

    # ── Notch / camera dot ─────────────────────────────
    cam_x = cx
    cam_y = lid_y0 + 14
    draw.ellipse([cam_x-4, cam_y-4, cam_x+4, cam_y+4], fill=(50,50,55))

def make_mockup(product):
    hero_path = IMAGES_DIR / product["hero"]
    if not hero_path.exists():
        print(f"  SKIP — image not found: {hero_path}")
        return

    color = product["color"]
    r, g, b = color

    # ── Background gradient ────────────────────────────
    img = Image.new("RGB", (SIZE, SIZE), (250, 250, 252))
    draw = ImageDraw.Draw(img)

    # soft gradient background
    for y in range(SIZE):
        t = y / SIZE
        cr = int(240 + (r/255*30)*t)
        cg = int(240 + (g/255*30)*t)
        cb = int(240 + (b/255*30)*t)
        draw.line([(0,y),(SIZE,y)], fill=(min(cr,255), min(cg,255), min(cb,255)))

    # ── Decorative circles (background) ───────────────
    for cx2, cy2, rad, alpha in [
        (200, 200, 300, 15),
        (1800, 300, 250, 12),
        (1850, 1800, 350, 10),
        (150, 1700, 280, 12),
    ]:
        circle = Image.new("RGBA", (SIZE, SIZE), (0,0,0,0))
        cd = ImageDraw.Draw(circle)
        cd.ellipse([cx2-rad, cy2-rad, cx2+rad, cy2+rad],
                   fill=(r, g, b, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), circle).convert("RGB")
        draw = ImageDraw.Draw(img)

    # ── Laptop ─────────────────────────────────────────
    screen_img = Image.open(hero_path).convert("RGB")
    laptop_w = 1180
    laptop_h = 760
    cx = SIZE // 2
    cy = SIZE // 2 - 60

    draw_laptop(draw, img, screen_img, cx, cy, laptop_w, laptop_h, color)

    # ── Top label ──────────────────────────────────────
    f_label = load_font(52)
    label = product["label"] + " | Google Sheets Template"
    draw.text((SIZE//2, 90), label, font=f_label, fill=(50,50,50), anchor="mm")

    # ── Divider line ───────────────────────────────────
    draw.rectangle([SIZE//2-200, 118, SIZE//2+200, 122], fill=(r,g,b))

    # ── Bottom feature pills ───────────────────────────
    features = ["Instant Download", "Works on Any Device", "100% Customizable"]
    pill_y = SIZE - 200
    pill_w = 380
    gap = 30
    total = len(features) * pill_w + (len(features)-1) * gap
    start_x = (SIZE - total) // 2
    f_feat = load_font(32)

    for i, feat in enumerate(features):
        px = start_x + i * (pill_w + gap)
        draw.rounded_rectangle([px, pill_y, px+pill_w, pill_y+64],
                               radius=32, fill=(r,g,b))
        draw.text((px+pill_w//2, pill_y+32), feat, font=f_feat,
                  fill=(255,255,255), anchor="mm")

    # ── Bottom brand ───────────────────────────────────
    f_brand = load_font(36)
    draw.text((SIZE//2, SIZE-80), "nasritools.etsy.com",
              font=f_brand, fill=(130,130,130), anchor="mm")

    # ── Save ───────────────────────────────────────────
    out = MOCKUPS_DIR / f"{product['slug']}_mockup.jpg"
    img.save(out, "JPEG", quality=93)
    print(f"  Saved: {out.name}")

def main():
    print(f"\n{'='*55}")
    print(f"  NasriTools - Mockup Generator  [{len(PRODUCTS)} products]")
    print(f"  Output: {MOCKUPS_DIR}")
    print(f"{'='*55}\n")

    for i, p in enumerate(PRODUCTS, 1):
        print(f"[{i:02d}/{len(PRODUCTS)}] {p['slug']}")
        make_mockup(p)

    print(f"\n{'='*55}")
    print(f"  Done! {len(PRODUCTS)} mockups saved to:")
    print(f"  {MOCKUPS_DIR}")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    main()
