"""
generate_thumbnails.py
Generates professional 2000x2000 Etsy thumbnails for all Hero Products and Bundles.
Creates PNG files in ./thumbnails/ folder ready to upload to Etsy.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math
from pathlib import Path

OUT_DIR = Path("thumbnails")
OUT_DIR.mkdir(exist_ok=True)

SIZE = 2000

import glob, platform

def _find_font(names):
    """Try font names as bare filenames (PIL searches Windows Fonts dir),
    then full paths, then any .ttf on the system."""
    for name in names:
        # 1. Bare filename — works on Windows where PIL searches C:\Windows\Fonts
        try:
            return ImageFont.truetype(name, 10)  # size 10 just to test; caller passes real size
        except Exception:
            pass
    return None  # will retry with size below

def load_font(size):
    bold_names = [
        "arialbd.ttf", "Arial Bold.ttf",
        "calibrib.ttf", "Calibri Bold.ttf",
        "verdanab.ttf", "Verdana Bold.ttf",
        "trebucbd.ttf", "impact.ttf",
    ]
    full_paths_bold = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
        "C:/Windows/Fonts/trebucbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    # Try bare names first (Windows PIL auto-resolves from Fonts dir)
    for name in bold_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    # Try full paths
    for path in full_paths_bold:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Last resort: scan for any .ttf
    for pattern in ["C:/Windows/Fonts/*.ttf", "/usr/share/fonts/**/*.ttf"]:
        for f in glob.glob(pattern, recursive=True):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    # Absolute fallback — PIL built-in (small but at least shows text)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def load_font_regular(size):
    regular_names = ["arial.ttf", "calibri.ttf", "verdana.ttf"]
    regular_paths  = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in regular_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    for path in regular_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return load_font(size)

# ── Color palettes ─────────────────────────────────────────────────────────────
PALETTES = {
    "finance": {
        "bg": "#F8FAFF",
        "card": "#FFFFFF",
        "accent": "#2563EB",
        "accent2": "#1E40AF",
        "text_main": "#1B2A4A",
        "text_sub": "#475569",
        "badge_bg": "#E63946",
        "badge_text": "#FFFFFF",
        "highlight": "#DBEAFE",
    },
    "business": {
        "bg": "#0F172A",
        "card": "#1E293B",
        "accent": "#38BDF8",
        "accent2": "#0EA5E9",
        "text_main": "#F1F5F9",
        "text_sub": "#94A3B8",
        "badge_bg": "#F59E0B",
        "badge_text": "#0F172A",
        "highlight": "#1E3A5F",
    },
    "health": {
        "bg": "#F0FDF4",
        "card": "#FFFFFF",
        "accent": "#059669",
        "accent2": "#047857",
        "text_main": "#064E3B",
        "text_sub": "#374151",
        "badge_bg": "#059669",
        "badge_text": "#FFFFFF",
        "highlight": "#D1FAE5",
    },
    "productivity": {
        "bg": "#FAF5FF",
        "card": "#FFFFFF",
        "accent": "#7C3AED",
        "accent2": "#6D28D9",
        "text_main": "#3B0764",
        "text_sub": "#6B7280",
        "badge_bg": "#7C3AED",
        "badge_text": "#FFFFFF",
        "highlight": "#EDE9FE",
    },
    "bundle": {
        "bg": "#0D0D1A",
        "card": "#1A1A2E",
        "accent": "#F59E0B",
        "accent2": "#D97706",
        "text_main": "#FFFFFF",
        "text_sub": "#CBD5E1",
        "badge_bg": "#F59E0B",
        "badge_text": "#0D0D1A",
        "highlight": "#2D2D4E",
    },
}

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius*2, y0 + radius*2], fill=fill)
    draw.ellipse([x1 - radius*2, y0, x1, y0 + radius*2], fill=fill)
    draw.ellipse([x0, y1 - radius*2, x0 + radius*2, y1], fill=fill)
    draw.ellipse([x1 - radius*2, y1 - radius*2, x1, y1], fill=fill)

def draw_badge(draw, text, x, y, bg, fg, font):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 40
    h = bbox[3] - bbox[1] + 20
    draw_rounded_rect(draw, (x, y, x + w, y + h), 12, hex2rgb(bg))
    draw.text((x + 20, y + 10 - bbox[1]), text, font=font, fill=hex2rgb(fg))
    return w, h

def draw_stat_card(draw, x, y, w, h, label, value, p, card_font_large, card_font_small):
    draw_rounded_rect(draw, (x, y, x+w, y+h), 20, hex2rgb(p["highlight"]))
    val_bbox = card_font_large.getbbox(value)
    val_w = val_bbox[2] - val_bbox[0]
    draw.text((x + (w - val_w)//2, y + 24), value,
              font=card_font_large, fill=hex2rgb(p["accent"]))
    lbl_bbox = card_font_small.getbbox(label)
    lbl_w = lbl_bbox[2] - lbl_bbox[0]
    draw.text((x + (w - lbl_w)//2, y + h - 52), label,
              font=card_font_small, fill=hex2rgb(p["text_sub"]))

def draw_check_item(draw, x, y, text, p, font):
    draw.ellipse([x, y+4, x+28, y+32], fill=hex2rgb(p["accent"]))
    draw.text((x+7, y+4), "✓", font=font, fill=hex2rgb(p["bg"]))
    draw.text((x+44, y), text, font=font, fill=hex2rgb(p["text_sub"]))

def make_thumbnail(filename, palette_key, badge_text, product_name, tagline,
                   stats, features, cta="⚡ INSTANT DOWNLOAD"):
    p = PALETTES[palette_key]
    img = Image.new("RGB", (SIZE, SIZE), hex2rgb(p["bg"]))
    draw = ImageDraw.Draw(img)

    # Fonts
    f_huge   = load_font(130)
    f_large  = load_font(72)
    f_medium = load_font(52)
    f_small  = load_font(40)
    f_badge  = load_font(38)
    f_stat_v = load_font(80)
    f_stat_l = load_font(34)
    f_check  = load_font(34)

    # ── Background accent stripe ───────────────────────────────────────────────
    if palette_key == "bundle":
        # Gradient-like diagonal stripe
        for i in range(0, 200, 4):
            draw.rectangle([0, i, SIZE, i+2],
                           fill=tuple(min(255, c+10) for c in hex2rgb(p["bg"])))

    # ── Top badge ─────────────────────────────────────────────────────────────
    bw, bh = draw_badge(draw, badge_text, 80, 80, p["badge_bg"], p["badge_text"], f_badge)

    # ── Stats cards ───────────────────────────────────────────────────────────
    if stats:
        card_w = (SIZE - 200 - (len(stats)-1)*40) // len(stats)
        card_h = 220
        card_y = 200
        for i, (val, lbl) in enumerate(stats):
            cx = 100 + i * (card_w + 40)
            draw_stat_card(draw, cx, card_y, card_w, card_h,
                           lbl, val, p, f_stat_v, f_stat_l)

    # ── Product name ──────────────────────────────────────────────────────────
    name_y = 480 if stats else 260
    # Word wrap product name
    words = product_name.upper().split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if f_huge.getbbox(test)[2] < SIZE - 160:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)

    for i, ln in enumerate(lines):
        bbox = f_huge.getbbox(ln)
        x = (SIZE - (bbox[2] - bbox[0])) // 2
        draw.text((x, name_y + i * 148), ln, font=f_huge, fill=hex2rgb(p["text_main"]))

    # ── Tagline ───────────────────────────────────────────────────────────────
    tag_y = name_y + len(lines) * 148 + 30
    bbox = f_medium.getbbox(tagline)
    x = (SIZE - (bbox[2] - bbox[0])) // 2
    draw.text((x, tag_y), tagline, font=f_medium, fill=hex2rgb(p["text_sub"]))

    # ── Accent line ───────────────────────────────────────────────────────────
    line_y = tag_y + 90
    draw.rectangle([100, line_y, SIZE-100, line_y+5], fill=hex2rgb(p["accent"]))

    # ── Features checklist ────────────────────────────────────────────────────
    feat_y = line_y + 50
    for i, feat in enumerate(features[:4]):
        draw_check_item(draw, 100, feat_y + i * 80, feat, p, f_check)

    # ── CTA bar ───────────────────────────────────────────────────────────────
    cta_y = SIZE - 180
    draw_rounded_rect(draw, (80, cta_y, SIZE-80, cta_y+110), 20, hex2rgb(p["accent"]))
    bbox = f_large.getbbox(cta)
    x = (SIZE - (bbox[2] - bbox[0])) // 2
    draw.text((x, cta_y + 18), cta, font=f_large, fill=hex2rgb(p["bg"] if palette_key != "bundle" else "#0D0D1A"))

    # ── Watermark ─────────────────────────────────────────────────────────────
    wm = "nasritools.etsy.com"
    bbox = f_small.getbbox(wm)
    draw.text((SIZE - bbox[2] - bbox[0] - 60, SIZE - 50),
              wm, font=f_small, fill=hex2rgb(p["text_sub"]))

    path = OUT_DIR / filename
    img.save(path, "PNG", quality=95)
    print(f"  [OK] {filename}")
    return path


PRODUCTS = [
    # (filename, palette, badge, name, tagline, stats, features, cta)
    (
        "hero_budget_tracker.png", "finance",
        "🔥 BEST SELLER",
        "Budget Tracker",
        "Know Exactly Where Your Money Goes",
        [("€3,200", "INCOME"), ("€1,847", "EXPENSES"), ("€1,353", "SAVINGS")],
        ["Monthly & Annual Overview", "Auto-Calculating Formulas",
         "Works on Phone, Tablet & Desktop", "Instant Download — Ready in 2 min"],
        "⚡ INSTANT DOWNLOAD — START TODAY",
    ),
    (
        "hero_invoice_tracker.png", "finance",
        "⭐ FREELANCER ESSENTIAL",
        "Invoice & Client Tracker",
        "Never Lose Track of a Payment Again",
        [("24", "CLIENTS"), ("€8,400", "BILLED"), ("6", "PENDING")],
        ["Client & Invoice Dashboard", "Paid / Pending / Overdue Status",
         "Monthly Revenue Summary", "Tax-Ready Income Report"],
        "⚡ INSTANT DOWNLOAD",
    ),
    (
        "hero_kpi_dashboard.png", "business",
        "◆ PREMIUM",
        "KPI Dashboard",
        "Your Entire Business on One Screen",
        [("€42K", "REVENUE"), ("68%", "CONV RATE"), ("127", "LEADS")],
        ["Sales & Revenue Tracking", "Marketing & Lead Metrics",
         "Team Performance Overview", "Auto-Updating Charts & Graphs"],
        "⚡ INSTANT DOWNLOAD",
    ),
    (
        "hero_complete_life.png", "bundle",
        "⭐ COMPLETE SYSTEM — ALL 10 TOOLS",
        "Complete Life System",
        "Budget · Fitness · Habits · Goals · Health",
        [("10", "SYSTEMS"), ("€199", "VALUE"), ("€54.99", "YOUR PRICE")],
        ["Finance + Budget + Debt Tracking", "Workout + Meal + Sleep + Weight",
         "Goals + Habits + Weekly Planner", "One File — Everything Included"],
        "⚡ INSTANT DOWNLOAD — SAVE 72%",
    ),
    (
        "hero_finance_bundle.png", "bundle",
        "⭐ BEST VALUE — SAVE 52%",
        "Finance Bundle",
        "Budget · Invoice · Cash Flow · Profit · Debt",
        [("5", "SYSTEMS"), ("€105", "VALUE"), ("€49.99", "YOUR PRICE")],
        ["Budget & Expense Tracker", "Invoice & Client Manager",
         "Cash Flow Forecast", "Profit & Loss + Debt Payoff"],
        "⚡ INSTANT DOWNLOAD — ALL 5 SYSTEMS",
    ),
    (
        "hero_workout_tracker.png", "health",
        "💪 FITNESS ESSENTIAL",
        "Workout Tracker",
        "Build Your Best Body in 12 Weeks",
        [("12", "WEEKS"), ("90%", "SUCCESS"), ("500+", "USERS")],
        ["12-Week Progressive Program", "Auto-Calculated Reps & Sets",
         "Progress Charts & Body Stats", "Works on Any Device"],
        "⚡ INSTANT DOWNLOAD",
    ),
    (
        "hero_habit_tracker.png", "productivity",
        "🎯 PRODUCTIVITY ESSENTIAL",
        "Habit Tracker",
        "Build Any Habit in 30 Days",
        [("30", "DAYS"), ("8", "HABITS"), ("100%", "VISUAL")],
        ["Daily & Weekly Habit Grid", "Streak Counter & Progress Bar",
         "Monthly Overview Dashboard", "Fully Customizable Habits"],
        "⚡ INSTANT DOWNLOAD",
    ),
    (
        "hero_weekly_planner.png", "productivity",
        "📅 PLANNER ESSENTIAL",
        "Weekly Planner",
        "Plan Your Week — Achieve Your Goals",
        [("7", "DAYS"), ("5", "PRIORITIES"), ("52", "WEEKS")],
        ["Weekly + Daily Planning System", "Priority & Goal Setting",
         "Time Blocking Grid", "Recurring Tasks & Habit Tracker"],
        "⚡ INSTANT DOWNLOAD",
    ),
    # NEW BUNDLES
    (
        "bundle_freelancer_kit.png", "bundle",
        "⭐ FREELANCER COMPLETE KIT",
        "Freelancer OS",
        "Invoice · Time · Social · Content · Income",
        [("5", "SYSTEMS"), ("€86", "VALUE"), ("€39.99", "YOUR PRICE")],
        ["Invoice & Client Tracker", "Time Tracking Timesheet",
         "Content Creator Planner", "Social Media Analytics"],
        "⚡ INSTANT DOWNLOAD — SAVE 53%",
    ),
    (
        "bundle_health_os.png", "health",
        "⭐ COMPLETE HEALTH OS",
        "Health Bundle",
        "Workout · Meal · Habits · Sleep · Weight",
        [("5", "SYSTEMS"), ("€75", "VALUE"), ("€34.99", "YOUR PRICE")],
        ["Workout Tracker (12-Week)", "Meal Planner + Grocery List",
         "Habit Tracker + Sleep Log", "Weight Loss Progress Tracker"],
        "⚡ INSTANT DOWNLOAD — SAVE 53%",
    ),
    (
        "bundle_business_starter.png", "business",
        "⭐ BUSINESS STARTER KIT",
        "Business OS",
        "KPI · Sales · Marketing · Cash Flow · Profit",
        [("5", "SYSTEMS"), ("€110", "VALUE"), ("€54.99", "YOUR PRICE")],
        ["KPI Dashboard + Sales Tracker", "Marketing ROI Tracker",
         "Cash Flow + Profit & Loss", "All Auto-Calculating"],
        "⚡ INSTANT DOWNLOAD — SAVE 50%",
    ),
    (
        "bundle_productivity_os.png", "productivity",
        "⭐ PRODUCTIVITY OS",
        "Productivity Bundle",
        "Weekly · Goals · Student · Project · Annual",
        [("5", "SYSTEMS"), ("€75", "VALUE"), ("€34.99", "YOUR PRICE")],
        ["Weekly Planner System", "90-Day Goals & Action Planner",
         "Student Academic Tracker", "Project & Deadline Manager"],
        "⚡ INSTANT DOWNLOAD — SAVE 53%",
    ),
]


def main():
    print("=" * 65)
    print("  NasriTools — Thumbnail Generator")
    print(f"  Output: {OUT_DIR.resolve()}")
    print("=" * 65 + "\n")

    for args in PRODUCTS:
        try:
            make_thumbnail(*args)
        except Exception as e:
            print(f"  [ERR] {args[0]}: {e}")

    print(f"\n  Generated {len(PRODUCTS)} thumbnails in ./{OUT_DIR}/")
    print("  Upload each file to the matching Etsy listing (Listing Manager → Photos)")
    print("=" * 65)

if __name__ == "__main__":
    main()
