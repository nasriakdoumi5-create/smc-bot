"""
NasriTools - Complete Shop Setup
- Updates shop title + announcement
- Creates 10 product sections
- Assigns all 100 listings to their sections

Run: python setup_shop.py
"""
import json, time, os, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"

# ---------- Section → slugs mapping ----------
SECTIONS = {
    "Budget & Finance": [
        "budget_tracker", "debt_payoff_planner", "net_worth_tracker",
        "emergency_fund_tracker", "grocery_budget_tracker", "christmas_budget_planner",
        "school_supply_budget", "subscription_tracker", "tax_prep_organizer",
        "retirement_planner", "dividend_income_tracker", "church_budget_planner",
        "cash_flow_forecast",
    ],
    "Business & Freelance": [
        "freelancer_invoice_tracker", "freelance_client_tracker", "small_business_finances",
        "profit_loss_tracker", "sales_commission_tracker", "lead_tracker",
        "marketing_budget_tracker", "marketing_roi_tracker", "consulting_project_tracker",
        "startup_financial_model", "law_firm_billing", "hr_onboarding_checklist",
        "employee_performance_tracker", "coaching_business_planner", "virtual_assistant_tracker",
        "kpi_dashboard", "nonprofit_budget_tracker",
    ],
    "Investing & Trading": [
        "investment_portfolio_tracker", "crypto_portfolio_tracker", "stock_trading_journal",
        "options_trading_tracker", "real_estate_analyzer", "real_estate_agent_tracker",
        "airbnb_host_tracker",
    ],
    "Health & Wellness": [
        "workout_tracker", "meal_planner", "weight_loss_tracker", "sleep_tracker",
        "mental_health_journal", "keto_diet_tracker", "marathon_training_plan",
        "baby_tracker", "pregnancy_tracker", "pet_expense_tracker",
    ],
    "Productivity & Planning": [
        "habit_tracker", "goals_planner", "travel_planner", "reading_tracker",
        "weekly_planner", "annual_review_planner", "moving_checklist",
        "project_management", "time_tracking_sheet", "skill_development_plan",
        "certification_tracker", "language_learning_tracker", "family_chores_tracker",
    ],
    "E-Commerce & Selling": [
        "etsy_shop_tracker", "amazon_seller_tracker", "dropshipping_tracker",
        "print_on_demand_tracker", "affiliate_marketing_tracker", "ecommerce_product_research",
        "inventory_management", "supply_chain_tracker", "photography_business_tracker",
    ],
    "Content & Social Media": [
        "content_creator_planner", "social_media_analytics", "seo_keyword_tracker",
        "blog_content_tracker", "podcast_planner", "youtube_channel_tracker",
        "social_media_posting_calendar", "email_marketing_tracker",
        "content_repurposing_tracker", "influencer_rate_calculator",
        "influencer_management_tracker",
    ],
    "Home & Lifestyle": [
        "home_renovation_tracker", "home_maintenance_tracker", "car_maintenance_tracker",
        "wedding_planner", "event_planner",
    ],
    "Specialty Business": [
        "restaurant_sales_tracker", "hair_salon_tracker", "musician_booking_tracker",
        "artist_commission_tracker", "author_book_tracker", "construction_estimate",
    ],
    "Education & Career": [
        "teacher_grade_book", "homeschool_planner", "tutor_client_tracker",
        "student_planner", "job_application_tracker", "side_hustle_income_tracker",
        "online_course_planner", "thesis_planner", "scholarship_tracker",
    ],
}

ANNOUNCEMENT = (
    "Welcome to NasriTools! \n\n"
    "We create professional Google Sheets & Excel templates so you can skip the setup "
    "and get straight to results.\n\n"
    "✅ Instant download — yours the moment you purchase\n"
    "📊 Works in Google Sheets AND Excel\n"
    "🔒 No subscriptions, no apps, no recurring fees\n"
    "⚡ Fill in your numbers — dashboard updates automatically\n\n"
    "Browse by category below, or search for what you need. "
    "Questions? Message us anytime — we respond within 24 hours."
)

SALE_MESSAGE = (
    "Thank you for your purchase! Your file is ready to download immediately from "
    "your Etsy account under Purchases & Reviews. "
    "Open it in Google Sheets or Excel, fill the yellow cells, and your dashboard is live. "
    "Need help? Message us — we're happy to assist!"
)


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
        print("  Token refreshed")
    return t


def auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


def main():
    print("\n" + "=" * 55)
    print("  NasriTools - Shop Setup")
    print("=" * 55 + "\n")

    token = get_token()
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}

    # ── 1. Update shop announcement + sale message ─────────────
    print("Step 1: Updating shop announcement...")
    r = requests.put(
        API + "/shops/" + str(SHOP_ID),
        headers={**auth(token), "Content-Type": "application/json"},
        json={
            "announcement": ANNOUNCEMENT,
            "digital_sale_message": SALE_MESSAGE,
        },
    )
    if r.ok:
        print("  announcement: OK")
    else:
        print("  announcement: ERR " + r.text[:150])
    time.sleep(0.5)

    # ── 2. Create sections ─────────────────────────────────────
    print("\nStep 2: Creating shop sections...")
    section_ids = {}
    for name in SECTIONS:
        r = requests.post(
            API + "/shops/" + str(SHOP_ID) + "/sections",
            headers={**auth(token), "Content-Type": "application/json"},
            json={"title": name},
        )
        if r.ok:
            sid = r.json().get("shop_section_id")
            section_ids[name] = sid
            print("  [OK] " + name + " → id=" + str(sid))
        else:
            print("  [ERR] " + name + ": " + r.text[:100])
        time.sleep(0.3)

    # ── 3. Assign listings to sections ────────────────────────
    print("\nStep 3: Assigning listings to sections...")
    assigned = 0
    errors = 0
    for section_name, slugs in SECTIONS.items():
        sid = section_ids.get(section_name)
        if not sid:
            print("  SKIP (no section id): " + section_name)
            continue
        for slug in slugs:
            lid = published.get(slug)
            if not lid:
                print("  SKIP (not published): " + slug)
                continue
            r = requests.patch(
                API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid),
                headers={**auth(token), "Content-Type": "application/json"},
                json={"shop_section_id": sid},
            )
            if r.ok:
                assigned += 1
                print("  OK: " + slug + " → " + section_name)
            else:
                errors += 1
                print("  ERR: " + slug + " → " + r.text[:80])
            time.sleep(0.25)

    print("\n" + "=" * 55)
    print("  Sections created : " + str(len(section_ids)))
    print("  Listings assigned: " + str(assigned))
    print("  Errors           : " + str(errors))
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
