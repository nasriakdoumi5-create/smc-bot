"""
NasriTools - Auto Mockup Generator for ALL Hero Images
Scans ~/nasri_hero_images/ and creates a laptop mockup for every product found
Run: python make_all_mockups.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os, hashlib, re

IMAGES_DIR  = Path(os.path.expanduser("~")) / "nasri_hero_images"
MOCKUPS_DIR = Path(os.path.expanduser("~")) / "nasri_mockups"
MOCKUPS_DIR.mkdir(exist_ok=True)
SIZE = 2000

# 12 professional color palettes — assigned deterministically from slug hash
PALETTES = [
    ((34, 139, 87),  (220, 247, 233)),
    ((108, 67, 176), (237, 228, 252)),
    ((214, 90, 49),  (252, 232, 224)),
    ((185, 50, 100), (252, 225, 237)),
    ((30, 100, 180), (220, 235, 252)),
    ((200, 60, 60),  (252, 225, 225)),
    ((20, 120, 140), (215, 242, 246)),
    ((50, 130, 70),  (220, 245, 225)),
    ((160, 100, 20), (252, 243, 218)),
    ((80, 80, 160),  (230, 230, 252)),
    ((120, 40, 120), (245, 220, 245)),
    ((40, 100, 140), (215, 235, 250)),
]

STOP_WORDS = {
    "google", "sheets", "template", "spreadsheet", "and", "the",
    "a", "an", "for", "to", "with", "in", "of", "your", "my",
    "free", "best", "simple", "easy", "complete",
}


def slug_from_filename(filename):
    """'profit_loss_tracker_01_hero.jpg' → 'profit_loss_tracker'"""
    name = Path(filename).stem
    name = re.sub(r'_0\d_hero$', '', name)
    name = re.sub(r'_hero$', '', name)
    return name


def label_from_slug(slug):
    """'profit_loss_tracker' → 'Profit Loss Tracker'"""
    words = [w.capitalize() for w in slug.split("_") if w not in STOP_WORDS]
    return " ".join(words)


def palette_for_slug(slug):
    idx = int(hashlib.md5(slug.encode()).hexdigest()[:4], 16) % len(PALETTES)
    return PALETTES[idx]


def load_font(size):
    for f in ["C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/arial.ttf",
              "C:/Windows/Fonts/calibrib.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_laptop(draw, img, screen_img, cx, cy, lw, lh, color):
    r, g, b = color
    body_h = int(lh * 0.07)
    body_y = cy + lh // 2
    bx0 = cx - int(lw * 0.55); bx1 = cx + int(lw * 0.55)
    draw.rounded_rectangle([bx0, body_y, bx1, body_y + body_h], radius=8, fill=(180, 180, 185))
    draw.rectangle([bx0 + 20, body_y, bx1 - 20, body_y + 4], fill=(210, 210, 215))
    lx0 = cx - lw // 2; lx1 = cx + lw // 2
    ly0 = cy - lh // 2; ly1 = cy + lh // 2
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=18, fill=(195, 195, 200))
    pad = 10
    draw.rounded_rectangle([lx0 + pad, ly0 + pad, lx1 - pad, ly1 - pad], radius=12, fill=(30, 30, 35))
    sp = 22
    sx0 = lx0 + sp; sy0 = ly0 + sp; sx1 = lx1 - sp; sy1 = ly1 - sp
    sw = sx1 - sx0; sh = sy1 - sy0
    screen_resized = screen_img.resize((sw, sh), Image.LANCZOS)
    img.paste(screen_resized, (sx0, sy0))
    glare = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glare)
    for i in range(60):
        alpha = max(0, 30 - i)
        gd.line([(0, i), (i, 0)], fill=(255, 255, 255, alpha), width=1)
    img.paste(glare, (sx0, sy0), glare)
    draw.rounded_rectangle([sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2], radius=4,
                            outline=(r, g, b, 180), width=3)
    draw.ellipse([cx - 4, ly0 + 14 - 4, cx + 4, ly0 + 14 + 4], fill=(50, 50, 55))


def make_mockup(hero_path, slug, label, color):
    r, g, b = color
    img = Image.new("RGB", (SIZE, SIZE), (250, 250, 252))
    draw = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / SIZE
        cr = int(240 + (r / 255 * 25) * t)
        cg = int(240 + (g / 255 * 25) * t)
        cb = int(240 + (b / 255 * 25) * t)
        draw.line([(0, y), (SIZE, y)], fill=(min(cr, 255), min(cg, 255), min(cb, 255)))
    for cx2, cy2, rad, alpha in [(200, 200, 300, 15), (1800, 300, 250, 12),
                                   (1850, 1800, 350, 10), (150, 1700, 280, 12)]:
        circle = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        cd = ImageDraw.Draw(circle)
        cd.ellipse([cx2 - rad, cy2 - rad, cx2 + rad, cy2 + rad], fill=(r, g, b, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), circle).convert("RGB")
        draw = ImageDraw.Draw(img)
    screen_img = Image.open(hero_path).convert("RGB")
    draw_laptop(draw, img, screen_img, SIZE // 2, SIZE // 2 - 60, 1180, 760, color)
    f_label = load_font(52)
    draw.text((SIZE // 2, 90), label + " | Google Sheets Template",
              font=f_label, fill=(50, 50, 50), anchor="mm")
    draw.rectangle([SIZE // 2 - 200, 118, SIZE // 2 + 200, 122], fill=(r, g, b))
    features = ["Instant Download", "Works on Any Device", "100% Customizable"]
    pill_y = SIZE - 200; pill_w = 380; gap = 30
    total_w = len(features) * pill_w + (len(features) - 1) * gap
    start_x = (SIZE - total_w) // 2
    f_feat = load_font(32)
    for i, feat in enumerate(features):
        px = start_x + i * (pill_w + gap)
        draw.rounded_rectangle([px, pill_y, px + pill_w, pill_y + 64], radius=32, fill=(r, g, b))
        draw.text((px + pill_w // 2, pill_y + 32), feat, font=f_feat,
                  fill=(255, 255, 255), anchor="mm")
    f_brand = load_font(36)
    draw.text((SIZE // 2, SIZE - 80), "nasritools.etsy.com",
              font=f_brand, fill=(130, 130, 130), anchor="mm")
    out = MOCKUPS_DIR / f"{slug}_mockup.jpg"
    img.save(out, "JPEG", quality=93)
    return out.name


def main():
    hero_files = sorted(IMAGES_DIR.glob("*_hero.jpg")) + \
                 sorted(IMAGES_DIR.glob("*_01_hero.jpg"))
    hero_files = list({f.name: f for f in hero_files}.values())  # deduplicate

    print(f"\n{'='*60}")
    print(f"  NasriTools - Auto Mockup Generator")
    print(f"  Found {len(hero_files)} hero images in {IMAGES_DIR.name}")
    print(f"{'='*60}\n")

    done = 0; skipped = 0
    for i, hero_path in enumerate(hero_files, 1):
        slug  = slug_from_filename(hero_path.name)
        label = label_from_slug(slug)
        color, _ = palette_for_slug(slug)
        out_path = MOCKUPS_DIR / f"{slug}_mockup.jpg"

        if out_path.exists():
            print(f"[{i:03d}/{len(hero_files)}] SKIP (exists): {slug}")
            skipped += 1
            continue

        print(f"[{i:03d}/{len(hero_files)}] {slug}")
        saved = make_mockup(hero_path, slug, label, color)
        print(f"    Saved: {saved}")
        done += 1

    print(f"\n{'='*60}")
    print(f"  Done! {done} new mockups created, {skipped} skipped")
    print(f"  Output: {MOCKUPS_DIR}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
