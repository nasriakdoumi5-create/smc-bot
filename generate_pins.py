"""
generate_pins.py
Creates Pinterest pin images (1000x1500) for top products.
Each pin: product hero image framed in a card + hook + CTA.
Output: pins/<slug>_pin.png + pins/pin_captions.txt
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1000, 1500
ROOT = Path(__file__).parent
OUT  = ROOT / "pins"
OUT.mkdir(exist_ok=True)

ORANGE = (249, 115, 22)
CREAM  = (255, 250, 247)
BLACK  = (17, 17, 17)
GREY   = (110, 104, 98)
WHITE  = (255, 255, 255)
GREEN  = (34, 197, 94)

BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

PINS = [
    {
        "slug": "starter_budget_tracker",
        "hook": "Start Budgeting\nin 5 Minutes",
        "sub":  "The simplest budget template\nyou'll ever use",
        "badge": "ONLY €0.99",
        "caption_title": "Simple Budget Template for Google Sheets — Only €0.99",
        "caption": ("Finally know where your money goes! This starter budget tracker "
                    "takes 5 minutes to set up. Income, spending & savings — all "
                    "auto-calculated. No subscription, yours forever. "
                    "#budgettemplate #googlesheets #budgeting #moneytips #savemoney"),
    },
    {
        "slug": "meal_planner",
        "hook": "Plan a Week of\nMeals in 10 Min",
        "sub":  "Meal planner + auto\ngrocery list in one sheet",
        "badge": "€4.99",
        "caption_title": "Meal Planner Spreadsheet with Auto Grocery List — Google Sheets",
        "caption": ("Never ask 'what's for dinner?' again. Weekly meal planning with "
                    "an automatic grocery list — take it to the store on your phone. "
                    "Buy once, use forever. "
                    "#mealplanning #mealprep #googlesheets #mealplanner #organization"),
    },
    {
        "slug": "content_creator_planner",
        "hook": "Never Miss a\nPosting Day Again",
        "sub":  "Content calendar, idea bank\n& performance tracker",
        "badge": "€4.99",
        "caption_title": "Content Creator Planner — Calendar + Idea Bank | Google Sheets",
        "caption": ("Plan a month of content in one sitting! Calendar for all platforms, "
                    "idea bank so you never run dry, and a tracker that shows what works. "
                    "No subscription — yours forever. "
                    "#contentcreator #contentcalendar #socialmediatips #creatortools"),
    },
]

def rounded(draw, x, y, w, h, r, fill):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill)

def make_pin(cfg):
    img  = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # subtle grid
    for gx in range(0, W, 50):
        draw.line([(gx, 0), (gx, H)], fill=(244, 236, 228), width=1)
    for gy in range(0, H, 50):
        draw.line([(0, gy), (W, gy)], fill=(244, 236, 228), width=1)

    # top & bottom bars
    draw.rectangle([0, 0, W, 14], fill=ORANGE)
    draw.rectangle([0, H-14, W, H], fill=ORANGE)

    fn_hook  = ImageFont.truetype(BOLD, 84)
    fn_sub   = ImageFont.truetype(REG, 40)
    fn_badge = ImageFont.truetype(BOLD, 44)
    fn_cta   = ImageFont.truetype(BOLD, 42)
    fn_brand = ImageFont.truetype(BOLD, 34)
    fn_url   = ImageFont.truetype(REG, 30)

    # hook text
    y = 70
    for line in cfg["hook"].split("\n"):
        tw = draw.textlength(line, font=fn_hook)
        draw.text(((W-tw)//2, y), line, font=fn_hook, fill=BLACK)
        y += 100
    y += 8
    for line in cfg["sub"].split("\n"):
        tw = draw.textlength(line, font=fn_sub)
        draw.text(((W-tw)//2, y), line, font=fn_sub, fill=GREY)
        y += 54

    # product hero image in a card
    hero_path = ROOT / "output" / cfg["slug"] / f"{cfg['slug']}_01_hero.jpg"
    card_y = y + 30
    card_h = 720
    card_w = 840
    card_x = (W - card_w) // 2
    # shadow
    rounded(draw, card_x+8, card_y+10, card_w, card_h, 28, (222, 214, 206))
    rounded(draw, card_x, card_y, card_w, card_h, 28, WHITE)
    if hero_path.exists():
        hero = Image.open(hero_path).convert("RGB")
        hero = hero.resize((card_w-40, card_w-40))
        hero = hero.crop((0, 0, card_w-40, card_h-40))
        mask = Image.new("L", hero.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, hero.size[0], hero.size[1]], radius=20, fill=255)
        img.paste(hero, (card_x+20, card_y+20), mask)

    # price badge
    badge_w, badge_h = 300, 84
    bx, by = W - badge_w - 60, card_y + card_h - badge_h//2
    rounded(draw, bx, by, badge_w, badge_h, 42, GREEN)
    tw = draw.textlength(cfg["badge"], font=fn_badge)
    draw.text((bx + (badge_w-tw)//2, by + 18), cfg["badge"], font=fn_badge, fill=WHITE)

    # CTA
    cta = "INSTANT DOWNLOAD  →"
    cta_w, cta_h = 560, 90
    cx = (W - cta_w) // 2
    cy = card_y + card_h + 80
    rounded(draw, cx, cy, cta_w, cta_h, 45, ORANGE)
    tw = draw.textlength(cta, font=fn_cta)
    draw.text((cx + (cta_w-tw)//2, cy + 22), cta, font=fn_cta, fill=WHITE)

    # brand footer
    brand = "NasriTools"
    tw = draw.textlength(brand, font=fn_brand)
    draw.text(((W-tw)//2, H-120), brand, font=fn_brand, fill=BLACK)
    url = "nasritools.etsy.com"
    tw = draw.textlength(url, font=fn_url)
    draw.text(((W-tw)//2, H-76), url, font=fn_url, fill=GREY)

    out = OUT / f"{cfg['slug']}_pin.png"
    img.save(out, "PNG", optimize=True)
    return out

def main():
    captions = []
    for cfg in PINS:
        out = make_pin(cfg)
        print(f"  ✓ {out.name}")
        captions.append(
            f"── {cfg['slug']} ──\n"
            f"TITLE: {cfg['caption_title']}\n"
            f"DESCRIPTION:\n{cfg['caption']}\n"
            f"LINK: https://nasritools.etsy.com\n"
        )
    (OUT / "pin_captions.txt").write_text("\n".join(captions))
    print(f"  ✓ pin_captions.txt")

if __name__ == "__main__":
    main()
