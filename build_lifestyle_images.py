"""
Build lifestyle hero images using Pexels stock photos.
Replaces _01_hero.jpg for all 100 products.
Run: python3 build_lifestyle_images.py
"""
import json, requests, time, io, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PEXELS_KEY = "3knaJZ5siP0O6slMAB155JTlieDugObexgHpTlJFPnLkBui2MKBJas38"
DATA_FILE  = Path("/home/user/smc-bot/nasritools/listings_data.json")
OUT_DIR    = Path("/home/user/smc-bot/output")
FONT_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SIZE       = (2000, 2000)

WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
BLACK  = (0, 0, 0)

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
    "budget_tracker":"budget planning money notebook desk",
    "debt_payoff_planner":"money saving debt freedom",
    "net_worth_tracker":"wealth investment portfolio finance",
    "emergency_fund_tracker":"savings bank piggy money",
    "grocery_budget_tracker":"grocery shopping food market",
    "christmas_budget_planner":"christmas shopping gifts holiday",
    "school_supply_budget":"school supplies education backpack",
    "subscription_tracker":"digital subscription streaming",
    "tax_prep_organizer":"tax documents office paperwork",
    "retirement_planner":"retirement senior couple happy",
    "dividend_income_tracker":"stock market dividend investment",
    "church_budget_planner":"church community faith",
    "cash_flow_forecast":"business cash flow finance",
    "freelancer_invoice_tracker":"freelancer laptop coffee work",
    "freelance_client_tracker":"client business meeting handshake",
    "small_business_finances":"small business owner entrepreneur",
    "profit_loss_tracker":"business profit growth chart",
    "sales_commission_tracker":"sales team business success",
    "lead_tracker":"sales leads business professional",
    "marketing_budget_tracker":"marketing team office strategy",
    "marketing_roi_tracker":"marketing analytics dashboard",
    "consulting_project_tracker":"consulting business professional meeting",
    "startup_financial_model":"startup office team collaboration",
    "law_firm_billing":"law office professional legal",
    "hr_onboarding_checklist":"human resources team onboarding",
    "employee_performance_tracker":"employee team performance review",
    "coaching_business_planner":"business coaching mentor",
    "virtual_assistant_tracker":"remote work laptop home office",
    "kpi_dashboard":"business analytics dashboard data",
    "nonprofit_budget_tracker":"nonprofit community volunteering",
    "investment_portfolio_tracker":"stock market investment chart",
    "crypto_portfolio_tracker":"cryptocurrency bitcoin digital",
    "stock_trading_journal":"stock trading market chart",
    "options_trading_tracker":"financial trading market",
    "real_estate_analyzer":"real estate property house",
    "real_estate_agent_tracker":"real estate agent property",
    "airbnb_host_tracker":"vacation rental property host",
    "workout_tracker":"gym workout fitness training",
    "meal_planner":"healthy meal prep food kitchen",
    "weight_loss_tracker":"fitness weight loss healthy lifestyle",
    "sleep_tracker":"sleep rest wellness bed night",
    "mental_health_journal":"mental health wellness mindfulness meditation",
    "keto_diet_tracker":"keto diet healthy food",
    "marathon_training_plan":"marathon running athlete sport",
    "baby_tracker":"baby newborn mother infant",
    "pregnancy_tracker":"pregnancy mother expecting",
    "pet_expense_tracker":"dog cat pet animal cute",
    "habit_tracker":"habit planning productivity desk",
    "goals_planner":"goal setting success planning",
    "travel_planner":"travel planning vacation adventure",
    "reading_tracker":"reading books library",
    "weekly_planner":"planning desk organization calendar",
    "annual_review_planner":"year planning goals new year",
    "moving_checklist":"moving home boxes packing",
    "project_management":"project management team collaboration",
    "time_tracking_sheet":"time management productivity clock",
    "skill_development_plan":"learning skills professional development",
    "certification_tracker":"professional certification diploma",
    "language_learning_tracker":"language learning study books",
    "family_chores_tracker":"family home chores cleaning",
    "etsy_shop_tracker":"handmade craft shop creative",
    "amazon_seller_tracker":"ecommerce selling online business",
    "dropshipping_tracker":"dropshipping ecommerce online store",
    "print_on_demand_tracker":"print on demand creative products",
    "affiliate_marketing_tracker":"affiliate marketing online income",
    "ecommerce_product_research":"ecommerce product research laptop",
    "inventory_management":"inventory warehouse storage shelves",
    "supply_chain_tracker":"supply chain logistics shipping",
    "photography_business_tracker":"photography business camera professional",
    "content_creator_planner":"content creator social media filming",
    "social_media_analytics":"social media analytics phone",
    "seo_keyword_tracker":"seo digital marketing laptop",
    "blog_content_tracker":"blogging writing content desk",
    "podcast_planner":"podcast recording microphone studio",
    "youtube_channel_tracker":"youtube video creator filming",
    "social_media_posting_calendar":"social media planning calendar",
    "email_marketing_tracker":"email marketing laptop office",
    "content_repurposing_tracker":"content marketing strategy",
    "influencer_rate_calculator":"influencer social media phone",
    "influencer_management_tracker":"influencer collaboration brand",
    "home_renovation_tracker":"home renovation interior design",
    "home_maintenance_tracker":"home maintenance repair tools",
    "car_maintenance_tracker":"car maintenance mechanic vehicle",
    "wedding_planner":"wedding planning bride flowers",
    "event_planner":"event planning party decoration",
    "restaurant_sales_tracker":"restaurant cafe food service",
    "hair_salon_tracker":"hair salon beauty stylist",
    "musician_booking_tracker":"musician music concert performance",
    "artist_commission_tracker":"artist studio painting creative",
    "author_book_tracker":"writer author book writing",
    "construction_estimate":"construction building architect",
    "teacher_grade_book":"teacher classroom education students",
    "homeschool_planner":"homeschool education home learning",
    "tutor_client_tracker":"tutoring education student learning",
    "student_planner":"student studying university campus",
    "job_application_tracker":"job search career interview professional",
    "side_hustle_income_tracker":"side hustle income entrepreneur",
    "online_course_planner":"online course learning laptop",
    "thesis_planner":"thesis research university library",
    "scholarship_tracker":"scholarship education graduation",
}

def fnt(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()


def get_pexels_photo(query):
    headers = {"Authorization": PEXELS_KEY}
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers=headers,
        params={"query": query, "per_page": 3, "orientation": "square"},
        timeout=15,
    )
    if not r.ok:
        print(f"    Pexels API error: {r.status_code}")
        return None
    photos = r.json().get("photos", [])
    if not photos:
        return None
    url = photos[0]["src"]["large2x"]
    img_r = requests.get(url, timeout=30)
    if img_r.ok:
        return Image.open(io.BytesIO(img_r.content)).convert("RGB")
    return None


def crop_square(img):
    w, h = img.size
    m = min(w, h)
    return img.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))


def wrap_text(d, text, font, max_width):
    words = text.split()
    lines, line = [], []
    for word in words:
        test = ' '.join(line + [word])
        bb = d.textbbox((0,0), test, font=font)
        if bb[2]-bb[0] > max_width and line:
            lines.append(' '.join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(' '.join(line))
    return lines


def draw_centered(d, text, y, font, fill, max_width=1900):
    bb = d.textbbox((0,0), text, font=font)
    w = bb[2]-bb[0]
    x = max(50, (2000-w)//2)
    d.text((x+2, y+2), text, font=font, fill=(0,0,0))
    d.text((x, y), text, font=font, fill=fill)


def build_hero(photo, item, category, color):
    slug = item["slug"]
    title = item["title"].split("|")[0].strip()
    price = item["price"]

    # Background
    bg = crop_square(photo).resize(SIZE, Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=3))

    # Dark overlay layers
    overlay = Image.new("RGB", SIZE, (0,0,0))
    img = Image.blend(bg, overlay, 0.55)
    d = ImageDraw.Draw(img)

    # Top color bar
    d.rectangle([0, 0, 2000, 10], fill=color)

    # Category badge (top left)
    cat = SLUG_CATEGORY.get(slug, "").upper()
    cf = fnt(FONT_BOLD, 30)
    cb = d.textbbox((0,0), cat, font=cf)
    cw, ch = cb[2]-cb[0]+30, cb[3]-cb[1]+16
    d.rounded_rectangle([30, 25, 30+cw, 25+ch], radius=8, fill=color)
    d.text((45, 33), cat, font=cf, fill=WHITE)

    # INSTANT DOWNLOAD badge (top right)
    bf = fnt(FONT_BOLD, 30)
    bt = "⬇  INSTANT DOWNLOAD"
    bb = d.textbbox((0,0), bt, font=bf)
    bw, bh = bb[2]-bb[0]+30, bb[3]-bb[1]+16
    d.rounded_rectangle([1940-bw, 25, 1940, 25+bh], radius=8, fill=(15,200,80))
    d.text((1940-bw+15, 33), bt, font=bf, fill=WHITE)

    # Main title
    tf = fnt(FONT_BOLD, 92)
    lines = wrap_text(d, title, tf, 1800)
    total_h = len(lines) * 108
    title_y = max(500, 950 - total_h // 2)
    for i, line in enumerate(lines):
        draw_centered(d, line, title_y + i*108, tf, WHITE)

    # Subtitle
    subtitle_y = title_y + total_h + 40
    sf = fnt(FONT_REG, 46)
    sub = "Google Sheets & Excel Template  •  Instant Digital Download"
    draw_centered(d, sub, subtitle_y, sf, (200, 200, 200))

    # Bottom dark panel
    panel_top = 1480
    panel = Image.new("RGB", (2000, 520), (8, 12, 25))
    img.paste(panel, (0, panel_top))
    d = ImageDraw.Draw(img)

    # Panel top accent
    d.rectangle([0, panel_top, 2000, panel_top+5], fill=color)

    # 3 feature checkmarks
    features = [
        "Auto-calculating dashboard",
        "Fill yellow cells only",
        "Works offline & on mobile",
    ]
    feat_f = fnt(FONT_BOLD, 36)
    positions = [100, 750, 1380]
    for i, (feat, px) in enumerate(zip(features, positions)):
        d.text((px, panel_top+50), f"✓  {feat}", font=feat_f, fill=color)

    # Price
    pf = fnt(FONT_BOLD, 60)
    price_text = f"${price:.2f}  —  One-Time Purchase"
    draw_centered(d, price_text, panel_top+140, pf, YELLOW)

    # Compatibility
    cf2 = fnt(FONT_REG, 38)
    compat = "Google Sheets  ·  Microsoft Excel 2016+  ·  No subscription"
    draw_centered(d, compat, panel_top+230, cf2, (170, 170, 200))

    # Stars
    stf = fnt(FONT_BOLD, 44)
    draw_centered(d, "★  ★  ★  ★  ★", panel_top+310, stf, YELLOW)

    # Brand
    brf = fnt(FONT_REG, 28)
    d.text((40, panel_top+390), "nasritools.etsy.com", font=brf, fill=(80,80,110))

    # Bottom color strip
    d.rectangle([0, 1990, 2000, 2000], fill=color)

    return img


def main():
    listings = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    total = len(listings)
    done = 0

    # Cache one photo per category to save API calls
    category_photos = {}

    print(f"\n{'='*60}")
    print(f"  Building {total} lifestyle hero images")
    print(f"{'='*60}\n")

    for i, item in enumerate(listings, 1):
        slug = item["slug"]
        category = SLUG_CATEGORY.get(slug, "Productivity & Planning")
        color = CATEGORY_COLORS.get(category, (74, 144, 217))
        out_path = OUT_DIR / slug / f"{slug}_01_hero.jpg"

        print(f"[{i:03d}/{total}] {slug}")

        # Get photo
        query = SEARCH_TERMS.get(slug, category.lower())
        photo = None

        # Try product-specific search first
        try:
            photo = get_pexels_photo(query)
            time.sleep(0.3)
        except Exception as e:
            print(f"    photo error: {e}")

        # Fallback to category photo
        if not photo:
            if category in category_photos:
                photo = category_photos[category]
            else:
                try:
                    photo = get_pexels_photo(category.lower() + " professional")
                    if photo:
                        category_photos[category] = photo
                    time.sleep(0.3)
                except:
                    pass

        if not photo:
            print(f"    SKIP: no photo found")
            continue

        # Cache for same category
        if category not in category_photos:
            category_photos[category] = photo

        try:
            img = build_hero(photo, item, category, color)
            img.save(str(out_path), quality=95, optimize=True)
            done += 1
            print(f"    OK → {out_path.name}")
        except Exception as e:
            print(f"    BUILD ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"  Done: {done}/{total} images built")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
