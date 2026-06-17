"""
NasriTools - Rebuild Hero Images with Lifestyle Photos
- Downloads relevant photos from Pexels for each product
- Generates professional lifestyle hero images (2000x2000px)
- Uploads to Etsy replacing the existing rank-1 image

Run: python rebuild_hero_images.py
"""
import json, os, time, io, requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ────────────────────────────────────────────
PEXELS_KEY = "3knaJZ5siP0O6slMAB155JTlieDugObexgHpTlJFPnLkBui2MKBJas38"
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DATA_FILE  = Path(os.path.expanduser("~")) / "smc-bot" / "nasritools" / "listings_data.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_hero_rebuilt.json"
IMG_DIR    = Path(os.path.expanduser("~")) / "nasri_hero_images"
IMG_DIR.mkdir(exist_ok=True)

SIZE = (2000, 2000)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
BLACK  = (0, 0, 0)

# ── Windows Fonts ─────────────────────────────────────
def _font(size, bold=False):
    candidates = []
    if bold:
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/Arial Bold.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/Arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()

# ── Category Data ─────────────────────────────────────
CATEGORY_COLORS = {
    "Budget & Finance":       (41,  128, 185),
    "Business & Freelance":   (39,  174, 96),
    "Investing & Trading":    (22,  160, 133),
    "Health & Wellness":      (231, 76,  60),
    "Productivity & Planning":(155, 89,  182),
    "E-Commerce & Selling":   (230, 126, 34),
    "Content & Social Media": (52,  152, 219),
    "Home & Lifestyle":       (200, 160, 40),
    "Specialty Business":     (26,  188, 156),
    "Education & Career":     (192, 57,  43),
}

SLUG_CATEGORY = {
    "budget_tracker":"Budget & Finance","debt_payoff_planner":"Budget & Finance",
    "net_worth_tracker":"Budget & Finance","emergency_fund_tracker":"Budget & Finance",
    "grocery_budget_tracker":"Budget & Finance","christmas_budget_planner":"Budget & Finance",
    "school_supply_budget":"Budget & Finance","subscription_tracker":"Budget & Finance",
    "tax_prep_organizer":"Budget & Finance","retirement_planner":"Budget & Finance",
    "dividend_income_tracker":"Budget & Finance","church_budget_planner":"Budget & Finance",
    "cash_flow_forecast":"Budget & Finance",
    "freelancer_invoice_tracker":"Business & Freelance","freelance_client_tracker":"Business & Freelance",
    "small_business_finances":"Business & Freelance","profit_loss_tracker":"Business & Freelance",
    "sales_commission_tracker":"Business & Freelance","lead_tracker":"Business & Freelance",
    "marketing_budget_tracker":"Business & Freelance","marketing_roi_tracker":"Business & Freelance",
    "consulting_project_tracker":"Business & Freelance","startup_financial_model":"Business & Freelance",
    "law_firm_billing":"Business & Freelance","hr_onboarding_checklist":"Business & Freelance",
    "employee_performance_tracker":"Business & Freelance","coaching_business_planner":"Business & Freelance",
    "virtual_assistant_tracker":"Business & Freelance","kpi_dashboard":"Business & Freelance",
    "nonprofit_budget_tracker":"Business & Freelance",
    "investment_portfolio_tracker":"Investing & Trading","crypto_portfolio_tracker":"Investing & Trading",
    "stock_trading_journal":"Investing & Trading","options_trading_tracker":"Investing & Trading",
    "real_estate_analyzer":"Investing & Trading","real_estate_agent_tracker":"Investing & Trading",
    "airbnb_host_tracker":"Investing & Trading",
    "workout_tracker":"Health & Wellness","meal_planner":"Health & Wellness",
    "weight_loss_tracker":"Health & Wellness","sleep_tracker":"Health & Wellness",
    "mental_health_journal":"Health & Wellness","keto_diet_tracker":"Health & Wellness",
    "marathon_training_plan":"Health & Wellness","baby_tracker":"Health & Wellness",
    "pregnancy_tracker":"Health & Wellness","pet_expense_tracker":"Health & Wellness",
    "habit_tracker":"Productivity & Planning","goals_planner":"Productivity & Planning",
    "travel_planner":"Productivity & Planning","reading_tracker":"Productivity & Planning",
    "weekly_planner":"Productivity & Planning","annual_review_planner":"Productivity & Planning",
    "moving_checklist":"Productivity & Planning","project_management":"Productivity & Planning",
    "time_tracking_sheet":"Productivity & Planning","skill_development_plan":"Productivity & Planning",
    "certification_tracker":"Productivity & Planning","language_learning_tracker":"Productivity & Planning",
    "family_chores_tracker":"Productivity & Planning",
    "etsy_shop_tracker":"E-Commerce & Selling","amazon_seller_tracker":"E-Commerce & Selling",
    "dropshipping_tracker":"E-Commerce & Selling","print_on_demand_tracker":"E-Commerce & Selling",
    "affiliate_marketing_tracker":"E-Commerce & Selling","ecommerce_product_research":"E-Commerce & Selling",
    "inventory_management":"E-Commerce & Selling","supply_chain_tracker":"E-Commerce & Selling",
    "photography_business_tracker":"E-Commerce & Selling",
    "content_creator_planner":"Content & Social Media","social_media_analytics":"Content & Social Media",
    "seo_keyword_tracker":"Content & Social Media","blog_content_tracker":"Content & Social Media",
    "podcast_planner":"Content & Social Media","youtube_channel_tracker":"Content & Social Media",
    "social_media_posting_calendar":"Content & Social Media","email_marketing_tracker":"Content & Social Media",
    "content_repurposing_tracker":"Content & Social Media","influencer_rate_calculator":"Content & Social Media",
    "influencer_management_tracker":"Content & Social Media",
    "home_renovation_tracker":"Home & Lifestyle","home_maintenance_tracker":"Home & Lifestyle",
    "car_maintenance_tracker":"Home & Lifestyle","wedding_planner":"Home & Lifestyle",
    "event_planner":"Home & Lifestyle",
    "restaurant_sales_tracker":"Specialty Business","hair_salon_tracker":"Specialty Business",
    "musician_booking_tracker":"Specialty Business","artist_commission_tracker":"Specialty Business",
    "author_book_tracker":"Specialty Business","construction_estimate":"Specialty Business",
    "teacher_grade_book":"Education & Career","homeschool_planner":"Education & Career",
    "tutor_client_tracker":"Education & Career","student_planner":"Education & Career",
    "job_application_tracker":"Education & Career","side_hustle_income_tracker":"Education & Career",
    "online_course_planner":"Education & Career","thesis_planner":"Education & Career",
    "scholarship_tracker":"Education & Career",
}

SEARCH_TERMS = {
    "budget_tracker":"budget money planning desk",
    "debt_payoff_planner":"money saving debt",
    "net_worth_tracker":"wealth investment finance",
    "emergency_fund_tracker":"savings bank money jar",
    "grocery_budget_tracker":"grocery shopping food market",
    "christmas_budget_planner":"christmas shopping gifts holiday",
    "school_supply_budget":"school supplies backpack",
    "subscription_tracker":"digital streaming subscription",
    "tax_prep_organizer":"tax documents office",
    "retirement_planner":"retirement couple happy",
    "dividend_income_tracker":"stock market investment",
    "church_budget_planner":"church community",
    "cash_flow_forecast":"business finance cash",
    "freelancer_invoice_tracker":"freelancer laptop coffee",
    "freelance_client_tracker":"business meeting handshake",
    "small_business_finances":"small business entrepreneur",
    "profit_loss_tracker":"business growth profit",
    "sales_commission_tracker":"sales team office",
    "lead_tracker":"sales business professional",
    "marketing_budget_tracker":"marketing team strategy",
    "marketing_roi_tracker":"marketing analytics",
    "consulting_project_tracker":"consulting professional meeting",
    "startup_financial_model":"startup team office",
    "law_firm_billing":"law office professional",
    "hr_onboarding_checklist":"human resources team",
    "employee_performance_tracker":"employee performance review",
    "coaching_business_planner":"business coaching mentor",
    "virtual_assistant_tracker":"remote work laptop",
    "kpi_dashboard":"business analytics data",
    "nonprofit_budget_tracker":"nonprofit community volunteering",
    "investment_portfolio_tracker":"stock market investment chart",
    "crypto_portfolio_tracker":"cryptocurrency bitcoin",
    "stock_trading_journal":"stock trading chart",
    "options_trading_tracker":"financial trading",
    "real_estate_analyzer":"real estate property house",
    "real_estate_agent_tracker":"real estate agent",
    "airbnb_host_tracker":"vacation rental property",
    "workout_tracker":"gym workout fitness",
    "meal_planner":"healthy meal prep food",
    "weight_loss_tracker":"fitness weight loss",
    "sleep_tracker":"sleep rest wellness",
    "mental_health_journal":"mental health mindfulness",
    "keto_diet_tracker":"keto diet healthy food",
    "marathon_training_plan":"marathon running athlete",
    "baby_tracker":"baby newborn mother",
    "pregnancy_tracker":"pregnancy mother expecting",
    "pet_expense_tracker":"dog cat pet cute",
    "habit_tracker":"habit planning productivity",
    "goals_planner":"goal setting success",
    "travel_planner":"travel vacation adventure",
    "reading_tracker":"reading books library",
    "weekly_planner":"planning desk calendar",
    "annual_review_planner":"year planning goals",
    "moving_checklist":"moving home boxes",
    "project_management":"project team collaboration",
    "time_tracking_sheet":"time management productivity",
    "skill_development_plan":"learning skills development",
    "certification_tracker":"professional certification",
    "language_learning_tracker":"language learning study",
    "family_chores_tracker":"family home chores",
    "etsy_shop_tracker":"handmade craft creative shop",
    "amazon_seller_tracker":"ecommerce selling online",
    "dropshipping_tracker":"ecommerce online store",
    "print_on_demand_tracker":"print creative products",
    "affiliate_marketing_tracker":"affiliate marketing online",
    "ecommerce_product_research":"ecommerce research laptop",
    "inventory_management":"inventory warehouse storage",
    "supply_chain_tracker":"logistics shipping supply",
    "photography_business_tracker":"photography camera professional",
    "content_creator_planner":"content creator social media",
    "social_media_analytics":"social media phone analytics",
    "seo_keyword_tracker":"seo digital marketing",
    "blog_content_tracker":"blogging writing desk",
    "podcast_planner":"podcast microphone recording",
    "youtube_channel_tracker":"youtube creator filming",
    "social_media_posting_calendar":"social media planning",
    "email_marketing_tracker":"email marketing laptop",
    "content_repurposing_tracker":"content marketing",
    "influencer_rate_calculator":"influencer social media",
    "influencer_management_tracker":"influencer brand collaboration",
    "home_renovation_tracker":"home renovation interior design",
    "home_maintenance_tracker":"home maintenance tools",
    "car_maintenance_tracker":"car mechanic vehicle",
    "wedding_planner":"wedding bride flowers",
    "event_planner":"event party decoration",
    "restaurant_sales_tracker":"restaurant cafe food",
    "hair_salon_tracker":"hair salon beauty",
    "musician_booking_tracker":"musician music performance",
    "artist_commission_tracker":"artist studio painting",
    "author_book_tracker":"writer author book",
    "construction_estimate":"construction building",
    "teacher_grade_book":"teacher classroom students",
    "homeschool_planner":"homeschool learning home",
    "tutor_client_tracker":"tutoring student learning",
    "student_planner":"student studying university",
    "job_application_tracker":"job search career interview",
    "side_hustle_income_tracker":"side hustle income",
    "online_course_planner":"online course learning",
    "thesis_planner":"research university library",
    "scholarship_tracker":"scholarship education graduation",
}

# ── Etsy helpers ──────────────────────────────────────
def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def etsy_auth(t):
    return {"Authorization": "Bearer " + t["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

# ── Pexels helper ─────────────────────────────────────
def get_photo(query):
    r = requests.get("https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": 5, "orientation": "square"},
        timeout=15)
    if not r.ok:
        return None
    photos = r.json().get("photos", [])
    if not photos:
        return None
    for photo in photos:
        url = photo["src"]["large2x"]
        ir = requests.get(url, timeout=30)
        if ir.ok:
            return Image.open(io.BytesIO(ir.content)).convert("RGB")
    return None

# ── Image builder ─────────────────────────────────────
def crop_square(img):
    w, h = img.size
    m = min(w, h)
    return img.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))

def draw_centered(d, text, y, font, fill, shadow=True):
    bb = d.textbbox((0,0), text, font=font)
    w = bb[2]-bb[0]
    x = max(60, (2000-w)//2)
    if shadow:
        d.text((x+3, y+3), text, font=font, fill=(0,0,0))
    d.text((x, y), text, font=font, fill=fill)

def wrap_text(d, text, font, max_w):
    words = text.split()
    lines, line = [], []
    for word in words:
        test = ' '.join(line + [word])
        bb = d.textbbox((0,0), test, font=font)
        if bb[2]-bb[0] > max_w and line:
            lines.append(' '.join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(' '.join(line))
    return lines

def build_hero(photo, slug, title, price):
    category = SLUG_CATEGORY.get(slug, "Productivity & Planning")
    color    = CATEGORY_COLORS.get(category, (74, 144, 217))

    # Background: crop + blur + darken
    bg = crop_square(photo).resize(SIZE, Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=4))
    dark = Image.new("RGB", SIZE, (0, 0, 0))
    img  = Image.blend(bg, dark, 0.58)
    d    = ImageDraw.Draw(img)

    # Top color bar
    d.rectangle([0, 0, 2000, 10], fill=color)

    # Category badge (top-left)
    cat_text = category.upper()
    cf = _font(32, bold=True)
    cb = d.textbbox((0,0), cat_text, font=cf)
    cw, ch = cb[2]-cb[0]+32, cb[3]-cb[1]+18
    d.rounded_rectangle([28, 24, 28+cw, 24+ch], radius=9, fill=color)
    d.text((44, 32), cat_text, font=cf, fill=WHITE)

    # INSTANT DOWNLOAD badge (top-right)
    bf = _font(30, bold=True)
    bt = "INSTANT DOWNLOAD"
    bb = d.textbbox((0,0), bt, font=bf)
    bw, bh = bb[2]-bb[0]+32, bb[3]-bb[1]+18
    d.rounded_rectangle([1972-bw, 24, 1972, 24+bh], radius=9, fill=(15, 185, 80))
    d.text((1972-bw+16, 32), bt, font=bf, fill=WHITE)

    # Main title
    tf = _font(90, bold=True)
    clean_title = title.split("|")[0].strip()
    lines = wrap_text(d, clean_title, tf, 1840)
    total_h = len(lines) * 108
    title_y = max(480, 940 - total_h // 2)
    for i, line in enumerate(lines):
        draw_centered(d, line, title_y + i*108, tf, WHITE)

    # Subtitle
    sub_y = title_y + total_h + 45
    sf = _font(46)
    draw_centered(d, "Google Sheets & Excel Template", sub_y, sf, (200, 200, 200))

    # Bottom dark panel
    panel_y = 1490
    panel = Image.new("RGB", (2000, 510), (8, 12, 26))
    img.paste(panel, (0, panel_y))
    d = ImageDraw.Draw(img)
    d.rectangle([0, panel_y, 2000, panel_y+5], fill=color)

    # 3 features
    features = ["Auto-calculating dashboard", "Fill yellow cells only", "Works in Google Sheets & Excel"]
    ff = _font(36, bold=True)
    positions = [80, 720, 1360]
    for feat, px in zip(features, positions):
        d.text((px, panel_y+50), f"✓  {feat}", font=ff, fill=color)

    # Price
    pf = _font(58, bold=True)
    draw_centered(d, f"${price:.2f}  —  One-Time Purchase", panel_y+140, pf, YELLOW, shadow=False)

    # Compatibility
    cf2 = _font(36)
    draw_centered(d, "No subscription  •  Instant Download  •  Use Forever", panel_y+230, cf2, (170,170,200), shadow=False)

    # Stars
    stf = _font(44, bold=True)
    draw_centered(d, "★  ★  ★  ★  ★", panel_y+305, stf, YELLOW, shadow=False)

    # Brand
    brf = _font(28)
    d.text((40, panel_y+390), "nasritools.etsy.com", font=brf, fill=(80,80,110))

    # Bottom strip
    d.rectangle([0, 1988, 2000, 2000], fill=color)

    return img

# ── Main ──────────────────────────────────────────────
def main():
    listings  = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token = get_token()
    total = len(listings)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Rebuild Hero Images")
    print(f"  Products: {total}  |  Already done: {len(done)}")
    print(f"{'='*60}\n")

    ok_count = 0
    category_photos = {}

    for i, item in enumerate(listings, 1):
        slug  = item["slug"]
        price = item["price"]
        title = item["title"]
        lid   = published.get(slug)

        if slug in done:
            print(f"[{i:03d}/{total}] SKIP (done): {slug}")
            continue
        if not lid:
            print(f"[{i:03d}/{total}] SKIP (not published): {slug}")
            continue

        print(f"[{i:03d}/{total}] {slug}")

        # 1. Get photo from Pexels
        category = SLUG_CATEGORY.get(slug, "Productivity & Planning")
        query = SEARCH_TERMS.get(slug, category.lower())
        photo = None

        try:
            photo = get_photo(query)
            time.sleep(0.4)
        except Exception as e:
            print(f"    photo error: {e}")

        if not photo and category in category_photos:
            photo = category_photos[category]
        elif photo and category not in category_photos:
            category_photos[category] = photo

        if not photo:
            print(f"    SKIP: no photo")
            continue

        # 2. Build image
        try:
            img = build_hero(photo, slug, title, price)
        except Exception as e:
            print(f"    build error: {e}")
            continue

        # 3. Save locally
        img_path = IMG_DIR / f"{slug}_01_hero.jpg"
        img.save(str(img_path), quality=95)

        # 4. Get existing images for this listing
        r = requests.get(
            API + f"/shops/{SHOP_ID}/listings/{lid}/images",
            headers=etsy_auth(token), timeout=15)
        time.sleep(0.3)

        if r.ok:
            images = r.json().get("results", [])
            rank1_ids = [im["listing_image_id"] for im in images if im.get("rank") == 1]
            for img_id in rank1_ids:
                rd = requests.delete(
                    API + f"/shops/{SHOP_ID}/listings/{lid}/images/{img_id}",
                    headers=etsy_auth(token), timeout=15)
                time.sleep(0.3)
                print(f"    deleted old rank1 image: {'OK' if rd.ok else rd.text[:60]}")

        # 5. Upload new image
        with open(img_path, "rb") as f:
            ru = requests.post(
                API + f"/shops/{SHOP_ID}/listings/{lid}/images",
                headers=etsy_auth(token),
                data={"rank": 1, "overwrite": "true"},
                files={"image": (f"{slug}_01_hero.jpg", f, "image/jpeg")},
                timeout=60,
            )
        time.sleep(0.5)

        if ru.ok:
            ok_count += 1
            done[slug] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    uploaded: OK")
        else:
            print(f"    upload ERR: {ru.text[:100]}")

        # Refresh token periodically
        if i % 20 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok_count} hero images rebuilt")
    print(f"  Images saved to: {IMG_DIR}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
