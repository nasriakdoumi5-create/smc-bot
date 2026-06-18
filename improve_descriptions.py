"""
NasriTools - Improve Descriptions for All 100 Products
Adds professional SEO-optimized descriptions via Etsy PATCH API
Run: python improve_descriptions.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_desc_improved.json"

# ── Descriptions for all 100 products ─────────────────
FOOTER = """

———————————————————————
INSTANT DOWNLOAD — No waiting, no shipping.
Compatible with Google Sheets (free) — works on PC, Mac, tablet & phone.
After purchase, you receive a link to copy the template to your Google Drive.
———————————————————————
Questions? Message me anytime — happy to help!"""

DESCRIPTIONS = {
    "budget_tracker": """Take full control of your finances with this easy-to-use Budget Tracker Google Sheets template.

WHAT'S INCLUDED:
✔ Monthly income & expense tracker
✔ Automatic balance calculation
✔ Bill payment tracker with due dates
✔ Savings goal progress bar
✔ Spending by category breakdown
✔ Annual summary dashboard

PERFECT FOR:
→ Anyone wanting to stop overspending
→ Couples managing household budgets
→ Students tracking living expenses
→ Freelancers monitoring income vs costs

HOW IT WORKS:
Simply enter your income and expenses — the spreadsheet calculates everything automatically. Color-coded categories make it easy to see where your money goes at a glance.""" + FOOTER,

    "habit_tracker": """Build powerful habits and break bad ones with this Habit Tracker Google Sheets template. Track streaks, monitor progress, and stay accountable every day.

WHAT'S INCLUDED:
✔ Daily habit tracking grid (up to 30 habits)
✔ Automatic streak counter
✔ Monthly completion percentage
✔ Weekly review section
✔ Habit categories (health, productivity, wellness)
✔ Visual progress charts

PERFECT FOR:
→ Building morning/evening routines
→ Fitness & health goals
→ Reading, meditation, journaling habits
→ 30-day challenges

HOW IT WORKS:
Check off each habit daily — the tracker automatically calculates your streaks and completion rates. Start small, stay consistent, see results.""" + FOOTER,

    "meal_planner": """Plan your meals for the entire week in minutes with this Meal Planner Google Sheets template. Save money, eat healthier, and stop the "what's for dinner?" stress forever.

WHAT'S INCLUDED:
✔ 7-day meal planning grid (breakfast, lunch, dinner, snacks)
✔ Automatic grocery list generator
✔ Pantry inventory tracker
✔ Nutritional notes section
✔ Monthly meal calendar view
✔ Recipe link organizer

PERFECT FOR:
→ Families meal prepping on weekends
→ Anyone trying to eat healthier
→ Reducing food waste & grocery bills
→ Batch cooking & meal prep

HOW IT WORKS:
Plan your meals for the week — the template auto-generates your shopping list by category so grocery trips are fast and efficient.""" + FOOTER,

    "wedding_planner": """Plan your perfect wedding without the stress using this comprehensive Wedding Planner Google Sheets template. Everything in one place — budget, guests, vendors, timeline.

WHAT'S INCLUDED:
✔ Full wedding budget tracker (all categories)
✔ Guest list manager with RSVP tracking
✔ Vendor contact & payment tracker
✔ Wedding day timeline / schedule
✔ Seating chart helper
✔ To-do checklist (12 months before to wedding day)

PERFECT FOR:
→ Engaged couples planning their big day
→ Brides & grooms on any budget
→ Destination & intimate weddings
→ Wedding coordinators

HOW IT WORKS:
Enter your budget, add vendors and guests — the planner tracks everything automatically so you can focus on enjoying your engagement.""" + FOOTER,

    "workout_tracker": """Track every workout, measure every gain with this Workout Tracker Google Sheets template. See your strength progress week by week and stay motivated to hit the gym.

WHAT'S INCLUDED:
✔ Weekly workout log (sets, reps, weight)
✔ Personal record (PR) tracker
✔ Body measurements tracker
✔ Cardio & cardio session log
✔ Monthly fitness goals section
✔ Progress comparison charts

PERFECT FOR:
→ Weight training & powerlifting
→ CrossFit & functional fitness
→ Home gym workouts
→ Anyone tracking fitness progress

HOW IT WORKS:
Log your exercises after each session — the tracker automatically highlights personal records and shows your strength progress over time.""" + FOOTER,

    "content_creator_planner": """Grow your audience faster with this Content Creator Planner Google Sheets template. Plan YouTube videos, Instagram posts, TikToks, and blog content — all in one organized dashboard.

WHAT'S INCLUDED:
✔ Monthly content calendar (all platforms)
✔ Video/post idea bank
✔ Publishing schedule tracker
✔ Analytics tracking (views, followers, engagement)
✔ Brand deal & sponsorship tracker
✔ Content pillars planning section

PERFECT FOR:
→ YouTubers planning video schedules
→ Instagram & TikTok creators
→ Bloggers & podcasters
→ Social media managers

HOW IT WORKS:
Plan your content weeks ahead, track performance metrics, and stay consistent — consistency is the #1 growth factor for creators.""" + FOOTER,

    "freelancer_invoice_tracker": """Get paid on time, every time with this Freelancer Invoice Tracker Google Sheets template. Track clients, invoices, payments, and income all in one professional dashboard.

WHAT'S INCLUDED:
✔ Invoice log with status (paid/pending/overdue)
✔ Client database & contact tracker
✔ Monthly & annual income summary
✔ Project tracker with hours & rates
✔ Tax preparation summary
✔ Late payment alert system

PERFECT FOR:
→ Freelancers & independent contractors
→ Graphic designers, writers, developers
→ Consultants & coaches
→ Anyone self-employed

HOW IT WORKS:
Add each invoice when sent — the tracker shows you what's paid, what's pending, and automatically calculates your monthly income. Never chase a payment without knowing the full history.""" + FOOTER,

    "student_planner": """Ace your semester with this Student Planner Google Sheets template. Track assignments, manage your schedule, monitor grades, and stay on top of every deadline.

WHAT'S INCLUDED:
✔ Weekly class schedule
✔ Assignment & homework tracker with due dates
✔ Grade calculator per subject
✔ GPA tracker
✔ Exam preparation checklist
✔ Semester overview calendar

PERFECT FOR:
→ High school & college students
→ Graduate & PhD students
→ Online course students
→ Anyone managing multiple classes

HOW IT WORKS:
Add your classes and assignments at the start of each week — the planner sends visual reminders through color coding so nothing slips through the cracks.""" + FOOTER,

    "goals_planner": """Turn your dreams into real, measurable achievements with this Goal Planner Google Sheets template. Set annual goals, break them into milestones, and track your progress every week.

WHAT'S INCLUDED:
✔ Annual goal setting framework (12 goals)
✔ 90-day action plan breakdown
✔ Weekly milestone tracker
✔ Habit alignment section
✔ Vision board notes & inspiration
✔ Monthly review & reflection prompts

PERFECT FOR:
→ New Year goal setting
→ Personal development & self-improvement
→ Career & business goals
→ Health, fitness & lifestyle goals

HOW IT WORKS:
Set your big goals for the year, break them into 90-day milestones, then track weekly actions. The planner shows you exactly how close you are to each goal.""" + FOOTER,

    "weekly_planner": """Start every week with clarity and end it with results using this Weekly Planner Google Sheets template. Organize tasks, schedule appointments, set priorities — all in one clean view.

WHAT'S INCLUDED:
✔ Week-at-a-glance daily schedule
✔ Priority task list (Top 3 of the week)
✔ Time blocking grid
✔ Notes & ideas section
✔ Weekly goals & intentions
✔ Habit check-in tracker

PERFECT FOR:
→ Busy professionals & managers
→ Entrepreneurs & freelancers
→ Students balancing multiple responsibilities
→ Anyone who wants more productive weeks

HOW IT WORKS:
Fill in your schedule every Sunday — block time for your most important tasks first, then fit in everything else. Simple, powerful, effective.""" + FOOTER,

    "expense_tracker": """Never lose track of a single dollar with this Expense Tracker Google Sheets template. Log every expense, categorize spending, and see exactly where your money goes.

WHAT'S INCLUDED:
✔ Daily expense log
✔ Auto-categorization (food, transport, bills, etc.)
✔ Monthly spending summary
✔ Budget vs actual comparison
✔ Receipt notes section
✔ Annual expense overview

PERFECT FOR:
→ Anyone wanting to reduce spending
→ Travel expense tracking
→ Business expense reimbursements
→ Tax-deductible expense logging""" + FOOTER,

    "project_planner": """Deliver projects on time and on budget with this Project Planner Google Sheets template. Manage tasks, timelines, team members, and milestones with ease.

WHAT'S INCLUDED:
✔ Project timeline / Gantt-style view
✔ Task list with owner & status
✔ Milestone tracker
✔ Budget tracker per project phase
✔ Risk & issue log
✔ Project completion dashboard

PERFECT FOR:
→ Project managers & team leads
→ Freelancers managing client projects
→ Small business owners
→ Event planners""" + FOOTER,

    "business_plan": """Build a solid foundation for your business with this Business Plan Google Sheets template. Covers financials, market analysis, goals, and strategy in a clear, professional format.

WHAT'S INCLUDED:
✔ Executive summary section
✔ Revenue & expense projections (3 years)
✔ Market analysis framework
✔ Competitive analysis matrix
✔ Business goals & KPIs tracker
✔ Cash flow forecast

PERFECT FOR:
→ New entrepreneurs & startup founders
→ Small business owners seeking loans
→ Side hustle to full business transitions
→ Business plan competitions""" + FOOTER,

    "kpi_dashboard": """Monitor your business performance in real-time with this KPI Dashboard Google Sheets template. Track your most important metrics and make data-driven decisions every week.

WHAT'S INCLUDED:
✔ Customizable KPI tracker (20+ metrics)
✔ Weekly & monthly trend charts
✔ Revenue, sales & growth tracking
✔ Team performance metrics
✔ Traffic & conversion rate tracking
✔ Executive-style summary view

PERFECT FOR:
→ Business owners & CEOs
→ Marketing managers
→ Sales team leaders
→ E-commerce store owners""" + FOOTER,

    "social_media_tracker": """Grow your social media presence with data using this Social Media Tracker Google Sheets template. Track followers, engagement, and growth across all platforms.

WHAT'S INCLUDED:
✔ Multi-platform tracker (Instagram, YouTube, TikTok, Pinterest)
✔ Follower growth chart
✔ Engagement rate calculator
✔ Best performing content log
✔ Posting frequency tracker
✔ Monthly growth summary

PERFECT FOR:
→ Content creators & influencers
→ Social media managers
→ Brand accounts
→ Small business owners""" + FOOTER,

    "invoice_template": """Send professional invoices in seconds with this Invoice Template Google Sheets. Clean, customizable, and ready to print or send as PDF.

WHAT'S INCLUDED:
✔ Professional invoice layout
✔ Auto-calculated totals & tax
✔ Client & service details section
✔ Invoice number tracking
✔ Payment terms section
✔ Multiple currency support

PERFECT FOR:
→ Freelancers & consultants
→ Small business owners
→ Service providers
→ Anyone billing clients""" + FOOTER,

    "crm_tracker": """Manage your customers and leads like a pro with this CRM Tracker Google Sheets template. Track contacts, follow-ups, deals, and sales pipeline without expensive software.

WHAT'S INCLUDED:
✔ Contact database with full details
✔ Lead status pipeline (cold → closed)
✔ Follow-up reminder system
✔ Deal value tracker
✔ Customer notes & history
✔ Monthly sales summary

PERFECT FOR:
→ Sales professionals
→ Real estate agents
→ Coaches & consultants
→ Small business owners""" + FOOTER,

    "time_tracker": """Know exactly where your time goes with this Time Tracker Google Sheets template. Log hours by project, client, or task — and boost your productivity.

WHAT'S INCLUDED:
✔ Daily time log by project/task
✔ Automatic hour totals
✔ Billable vs non-billable hours
✔ Client time summary
✔ Weekly & monthly reports
✔ Productivity score calculator

PERFECT FOR:
→ Freelancers billing by the hour
→ Remote workers tracking productivity
→ Consultants & lawyers
→ Anyone wanting more from their day""" + FOOTER,

    "rental_property": """Manage your rental properties like a pro with this Rental Property Tracker Google Sheets template. Track rent, expenses, maintenance, and profitability.

WHAT'S INCLUDED:
✔ Rent collection tracker (paid/unpaid)
✔ Property expense log
✔ Maintenance request tracker
✔ Tenant information database
✔ Monthly cash flow summary
✔ Annual profit/loss report

PERFECT FOR:
→ Landlords with 1-20 properties
→ Airbnb & short-term rental hosts
→ Real estate investors
→ Property management""" + FOOTER,

    "event_planner": """Plan perfect events every time with this Event Planner Google Sheets template. From small parties to large corporate events — manage budget, guests, vendors, and timeline.

WHAT'S INCLUDED:
✔ Event budget tracker
✔ Guest list & RSVP manager
✔ Vendor contact sheet
✔ Event day timeline
✔ Task checklist with deadlines
✔ Post-event debrief notes

PERFECT FOR:
→ Birthday parties & celebrations
→ Corporate events & conferences
→ Baby showers & bridal showers
→ Community events""" + FOOTER,
}

# Generic description for products not in the custom list
GENERIC_DESC_TEMPLATE = """{name} Google Sheets Template — professional, easy-to-use, and fully customizable.

WHAT'S INCLUDED:
✔ Ready-to-use Google Sheets template
✔ Clean, professional design
✔ Automatic calculations & formulas
✔ Fully customizable to your needs
✔ Easy to follow — no experience required

HOW IT WORKS:
Make a copy to your Google Drive and start using immediately. Works on any device — PC, Mac, tablet, or phone.

INSTANT DOWNLOAD — No waiting, no shipping.
Compatible with Google Sheets (free).
After purchase, you receive a link to copy the template to your Google Drive.

Questions? Message me anytime — happy to help!"""

# ── Auth ───────────────────────────────────────────────
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
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
        "Content-Type": "application/json"
    }

# ── Main ───────────────────────────────────────────────
def main():
    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    done      = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}

    token = get_token()
    total = len(published)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Description Improvement  [{total} products]")
    print(f"  Already done: {len(done)}")
    print(f"{'='*60}\n")

    ok = 0
    for i, (slug, lid) in enumerate(published.items(), 1):
        if slug in done:
            print(f"[{i:02d}/{total}] SKIP (done): {slug}")
            ok += 1
            continue

        # Get description — custom or generic
        if slug in DESCRIPTIONS:
            desc = DESCRIPTIONS[slug]
        else:
            name = slug.replace("_", " ").title()
            desc = GENERIC_DESC_TEMPLATE.format(name=name)

        print(f"[{i:02d}/{total}] {slug}")

        payload = {"description": desc[:65000]}

        r = requests.patch(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
            headers=etsy_auth(token),
            json=payload,
            timeout=30,
        )
        time.sleep(0.6)

        if r.ok:
            ok += 1
            done[slug] = lid
            DONE_FILE.write_text(json.dumps(done, indent=2))
            print(f"    updated: OK")
        else:
            print(f"    ERROR: {r.text[:120]}")

        if i % 5 == 0:
            token = get_token()

    print(f"\n{'='*60}")
    print(f"  Done: {ok}/{total} descriptions updated")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
