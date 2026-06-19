"""
NasriTools - Complete Store Repositioning
Rewrites ALL titles, tags, and descriptions with outcome-focused, system-based copy.
Also updates shop announcement with new positioning.
Run: python reposition_all.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_reposition_done.json"

# ─── Products — Outcome-Focused Repositioning ────────────────────────────────

PRODUCTS = [
    {
        "search_kw": ["budget", "expense"],
        "title": "Monthly Budget & Expense System | Track Every Euro Automatically | Google Sheets | Instant Download",
        "tags": [
            "budget tracker", "expense tracker", "google sheets budget",
            "monthly budget", "personal finance", "money management",
            "budget planner", "finance system", "savings tracker",
            "income tracker", "budget spreadsheet", "financial planner",
            "money tracker"
        ],
        "description": """Stop wondering where your money went. Know exactly — automatically.

Most people check their bank account and feel shocked. They have no idea where their money goes because they have no system. This changes that.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💸 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You check your balance and it's lower than expected — again
✗ You "try to save" but end the month with nothing
✗ You have no idea if you overspent on food, subscriptions, or going out
✗ Budget apps feel complicated and you give up after a week

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ See exactly where every euro went — categories auto-calculated
✔ Know your spending limits before you overspend (not after)
✔ Hit your savings goal every month with automatic tracking
✔ See your net worth grow month by month
✔ Prepare for bills before they come — zero surprises
✔ Feel confident about your financial future for the first time

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Monthly Budget Dashboard (all categories auto-calculated)
✔ Income & Expense Tracker (50+ customizable categories)
✔ Savings Goal Tracker (target + progress + timeline)
✔ Bill Payment Tracker (never miss a payment)
✔ Annual Overview (all 12 months compared side by side)
✔ Net Worth Calculator (assets vs liabilities)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start tracking in under 5 minutes
✔ FREE to use — works on Google Sheets (no subscription ever)
✔ Works on your phone during shopping
✔ No complicated setup — enter data, it calculates everything
✔ Lifetime access — update it year after year
✔ 100% editable — change any category to match your life

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO START (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → download link arrives in your Etsy inbox instantly
2. Click the link → opens in Google Sheets automatically
3. File → Make a Copy → saved to your Google Drive forever
4. Enter your income and categories → it calculates everything

That's it. You're now running your finances like a system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR FINANCE SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Bundle the Budget Tracker with Invoice Tracker + Goals Planner → search "Finance Control System" in our shop for 33% off.

━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ COMMON QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Do I need to pay for Google Sheets?
A: No. Google Sheets is 100% free. You just need a Google account.

Q: Can I use this on my phone?
A: Yes — Google Sheets app is free on iOS and Android.

Q: Can I change the categories?
A: Absolutely. Everything is fully editable.

Q: Is there a recurring fee?
A: Never. Pay once, own it forever.

Q: What if I need help?
A: Message us on Etsy — we reply within 24 hours.

nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["habit", "building"],
        "title": "30-Day Habit Building System | Track 30 Habits with Auto Streaks | Google Sheets | Instant Download",
        "tags": [
            "habit tracker", "30 day challenge", "google sheets habit",
            "daily habit tracker", "streak tracker", "routine planner",
            "habit planner", "productivity tracker", "self improvement",
            "morning routine", "habit system", "daily tracker",
            "wellness tracker"
        ],
        "description": """The reason your habits fail isn't willpower. It's the lack of a system.

Research shows that tracking your habits makes you 2× more likely to stick with them. Seeing your streak is the single most powerful motivator to keep going.

━━━━━━━━━━━━━━━━━━━━━━━━━━
😤 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You start a new habit and give up after 4-5 days
✗ You forget your daily habits until it's too late at night
✗ You don't know if you've improved month over month
✗ You have zero streak to protect — so breaking it feels easy

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Track up to 30 habits simultaneously — all in one place
✔ See your streak every single day (breaking it becomes painful)
✔ Know your weekly completion rate without any calculations
✔ Review your entire month visually in 10 seconds
✔ Identify which habits you actually keep vs which you skip
✔ Build a morning routine and actually follow it

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ 30-Habit Monthly Grid (check off each habit per day)
✔ Auto Streak Counter (your longest and current streak)
✔ Weekly Completion Rate (% automatically calculated)
✔ Monthly Progress Dashboard (visual overview)
✔ Annual Habit Review (which habits survived all 12 months)
✔ Habit Notes Section (why you skipped, what to improve)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start tracking tonight
✔ Google Sheets (free) — no app, no subscription
✔ Works on your phone to check off habits on the go
✔ Auto-calculates streaks — no manual counting
✔ Lifetime access — use it for years

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO START (3 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → instant download in your Etsy inbox
2. Open in Google Sheets → File → Make a Copy
3. Add your habits in column A (exercise, read, meditate, etc.)
4. Check off each day and watch your streaks build

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR HEALTH SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair this with Workout Tracker + Meal Planner → search "Health Transformation System" in our shop for 29% off.

━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ COMMON QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: How many habits can I track?
A: Up to 30 habits simultaneously per month.

Q: Can I track the same habits month after month?
A: Yes — each month is a new grid but the habits carry over.

Q: Does it work offline?
A: Yes, Google Sheets has an offline mode.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["meal", "planning"],
        "title": "Weekly Meal Planning System | Plan 7 Days of Meals in 15 Min | Grocery List | Google Sheets | Instant Download",
        "tags": [
            "meal planner", "weekly meal plan", "google sheets meal",
            "grocery list planner", "meal prep system", "nutrition tracker",
            "food planner", "healthy eating planner", "meal planning template",
            "weekly food plan", "diet planner", "recipe planner",
            "family meal planner"
        ],
        "description": """Planning your meals for the week takes 15 minutes. Not planning costs you €80+ every week.

Most people spend more on groceries than they need to, eat unhealthily during the week, and throw away food they forgot to use. The solution isn't willpower — it's a system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🛒 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You buy groceries without a plan and overspend every time
✗ You end up ordering takeout because "there's nothing to eat"
✗ You throw away food that went bad before you used it
✗ You have no idea how many calories or protein you're eating

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Plan 7 days of meals (breakfast, lunch, dinner, snacks) in 15 minutes
✔ Generate your full grocery list automatically — no forgetting anything
✔ Track calories, protein, carbs, and fat automatically
✔ Save €80+ per week by shopping with a plan
✔ Prep efficiently — everything organized by meal category
✔ Build a recipe library you can pull from every week

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ 7-Day Meal Planner (all meals and snacks)
✔ Auto-Generated Grocery List (organized by category)
✔ Nutrition Tracker (calories, protein, carbs, fat — auto-totaled)
✔ Monthly Meal Calendar (plan the full month)
✔ Recipe Database Sheet (save your favorite recipes)
✔ Grocery Budget Tracker (spend less, eat better)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this week's meals today
✔ Google Sheets (free) — works on any device
✔ Nutrition auto-calculated — no manual math
✔ Printable grocery list for shopping
✔ Lifetime access — use it every week

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR HEALTH SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Workout Tracker + Habit Tracker → search "Health Transformation System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["wedding", "planning"],
        "title": "Complete Wedding Planning System | Budget Guests Vendors Timeline | Google Sheets | Instant Download",
        "tags": [
            "wedding planner", "wedding budget tracker", "google sheets wedding",
            "guest list manager", "wedding checklist", "vendor tracker",
            "wedding organizer", "bridal planner", "wedding spreadsheet",
            "wedding timeline", "wedding budget", "bride planner",
            "wedding planning template"
        ],
        "description": """Your wedding day should be magical. The planning doesn't have to be overwhelming.

The average couple loses track of their wedding budget, forgets to follow up with vendors, and feels constantly stressed. It doesn't have to be that way.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💍 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You have vendor details scattered across 5 apps, emails, and notes
✗ The budget keeps "growing" without realizing where
✗ You're not sure who RSVP'd and who hasn't responded yet
✗ You lie awake worrying about things you might have forgotten

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Track your complete wedding budget — what's planned vs actual vs paid
✔ See your RSVP status at a glance — who's confirmed, who hasn't responded
✔ Keep all vendor contacts, contracts, deposits in one place
✔ Follow your month-by-month checklist so nothing gets missed
✔ Share with your partner or wedding planner instantly
✔ Wake up knowing you haven't forgotten anything

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Wedding Budget Tracker (planned vs actual vs paid — auto-calculated)
✔ Guest List Manager (RSVP status, dietary needs, seating)
✔ Vendor Database (contact info, contracts, deposit dates)
✔ Master Checklist (month-by-month tasks for 12 months out)
✔ Wedding Day Timeline (hour-by-hour schedule)
✔ Budget Summary Dashboard (total spend at a glance)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start organizing today
✔ Google Sheets (free) — share with partner or planner
✔ 100% customizable for your style and scale
✔ Lifetime access — use for as long as you plan

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["workout", "tracking"],
        "title": "Gym & Workout Tracking System | Log Sessions Track PRs See Progress | Google Sheets | Instant Download",
        "tags": [
            "workout tracker", "gym tracker", "google sheets workout",
            "fitness tracker", "exercise log", "strength tracker",
            "gym log template", "training log", "pr tracker",
            "weight lifting tracker", "bodybuilding tracker", "fitness system",
            "workout journal"
        ],
        "description": """If you're not tracking your workouts, you're just exercising randomly. You need a system.

The people who get results don't just "go to the gym." They track what they lift, compare it to last week, and make deliberate progress. This is the system that makes that possible.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You don't remember what you lifted last week, so you guess
✗ You've been training for months but can't tell if you're stronger
✗ You don't have a structured training plan — you decide at the gym
✗ Your personal records are stuck because you have no progression system

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Log every session: exercise, sets, reps, weight, notes
✔ See your personal records update automatically — no tracking manually
✔ View auto-generated progress charts showing your strength over time
✔ Follow a structured weekly training plan
✔ Track your body measurements alongside your lifts
✔ Know exactly what to do at the gym before you arrive

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Workout Session Log (exercise, sets, reps, weight, notes)
✔ Personal Record (PR) Tracker (auto-updated per exercise)
✔ Weekly Training Schedule Template
✔ Progress Charts (auto-generated from your data)
✔ Exercise Database (100+ exercises pre-loaded)
✔ Body Measurements Tracker (weight, body fat, measurements)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — log your next session tonight
✔ Google Sheets (free) — use on phone at the gym
✔ Auto-charts your progress — see it visually
✔ No gym subscription app needed
✔ Lifetime access — add years of training data

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR HEALTH SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Meal Planner + Habit Tracker → search "Health Transformation System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["content", "creator"],
        "title": "Content Creator Business System | Plan Content Track Growth Manage Deals | Google Sheets | Instant Download",
        "tags": [
            "content creator planner", "social media system", "content calendar google sheets",
            "content strategy planner", "instagram planner", "youtube planner",
            "content creator tools", "influencer planner", "brand deal tracker",
            "content schedule", "creator business", "social media planner",
            "content analytics tracker"
        ],
        "description": """Posting without a strategy is just making noise. A system is what separates creators who grow from those who burn out.

The biggest creators don't just create more — they create smarter. They have a system for planning, analyzing, and improving. Now you can too.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You post when you feel like it — no consistent schedule
✗ You have no idea which content actually drives growth
✗ You've missed brand deal deadlines or forgotten to follow up
✗ You have no record of what you've earned from your content

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Plan 3 months of content in one sitting — across all platforms
✔ Track your engagement and growth metrics weekly
✔ Never miss a brand deal deadline or deliverable
✔ See exactly how much you've earned (and from what)
✔ Build a content ideas bank so you never run dry
✔ Identify your top-performing content and replicate it

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Monthly Content Calendar (all platforms: IG, YouTube, TikTok, Blog)
✔ Content Ideas Bank (categorized, never run out of ideas)
✔ Platform Analytics Tracker (followers, engagement, reach per week)
✔ Brand Collaboration Tracker (deals, deadlines, rates, payments)
✔ Revenue Dashboard (income by source: sponsorships, affiliates, products)
✔ Content Performance Log (what worked, what didn't)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this month's content today
✔ Google Sheets (free) — accessible on any device anywhere
✔ Multi-platform: Instagram + YouTube + TikTok + Blog + LinkedIn
✔ No complicated tool to learn — you know how spreadsheets work
✔ Lifetime access — it grows with your creator business

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR BUSINESS SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Invoice Tracker + Budget Tracker → search "Creator Business System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["invoice", "client"],
        "title": "Freelancer Invoice & Client System | Get Paid on Time Every Time | Google Sheets | Instant Download",
        "tags": [
            "freelancer invoice tracker", "client management system", "invoice google sheets",
            "freelancer finance", "invoice tracker", "self employed planner",
            "client tracker", "payment tracker", "freelance business",
            "tax prep spreadsheet", "income tracker freelance", "overdue invoice tracker",
            "small business finance"
        ],
        "description": """Every unpaid invoice is money you've already earned sitting in someone else's account. This system gets it back.

Freelancers lose an average of 14% of their income to disorganized invoicing. Late payments, forgotten follow-ups, and unprepared tax seasons cost you real money.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You have invoices that are 30, 60, 90 days overdue
✗ You send a follow-up email and immediately forget about it
✗ Tax season is a nightmare of searching through old emails
✗ You can't quickly answer "how much have I earned this year?"

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ See every invoice status (paid/pending/overdue) in one view
✔ Know exactly which clients owe you money — and how much
✔ Track all client contact info, project history, and rates
✔ Calculate your total monthly and annual revenue automatically
✔ Have your tax deductible expenses already organized
✔ Follow up on overdue invoices confidently with full history

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Invoice Tracker (number, client, amount, due date, status, notes)
✔ Client Database (contact info, rates, project history)
✔ Payment Status Dashboard (paid / pending / overdue at a glance)
✔ Monthly & Annual Revenue Summary (auto-calculated)
✔ Tax Prep Sheet (income + deductible expenses organized)
✔ Project Time Tracker (log hours per project)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — track your open invoices today
✔ Google Sheets (free) — no accounting software subscription
✔ Auto-calculates outstanding balance and revenue
✔ Simpler than QuickBooks — made specifically for freelancers
✔ Lifetime access — your complete financial history in one file

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR FINANCE SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Budget Tracker + Goals Planner → search "Finance Control System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["student", "academic"],
        "title": "Student Academic Success System | Grades GPA Assignments Study Schedule | Google Sheets | Instant Download",
        "tags": [
            "student planner", "gpa calculator google sheets", "grade tracker",
            "study planner", "assignment tracker", "college planner",
            "study schedule template", "student organizer", "homework tracker",
            "academic planner", "university planner", "exam planner",
            "student success system"
        ],
        "description": """Most students don't fail because they're not smart. They fail because they have no system.

Missing deadlines, surprise exam grades, and a GPA you can't explain — these aren't intelligence problems. They're organization problems. This system fixes that.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You miss assignment deadlines because you forgot they existed
✗ Your GPA is lower than expected but you don't know why
✗ You study the wrong things before exams and panic
✗ You balance classes, work, and social life with no structure

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ See every assignment, deadline, and submission status at a glance
✔ Watch your GPA calculate automatically as you add grades
✔ Know exactly how many days until each exam — with a countdown
✔ Build a weekly study schedule that actually works
✔ Identify which subjects need the most attention
✔ Start each week knowing exactly what needs to be done

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Assignment Tracker (subject, task, due date, priority, status)
✔ Grade Tracker with Auto GPA Calculator (real-time GPA)
✔ Weekly Study Schedule (time-blocked by subject)
✔ Exam Countdown Calendar (days remaining per exam)
✔ Semester Overview Dashboard (all classes at a glance)
✔ Study Hours Log (track time spent per subject)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — organize this semester today
✔ Google Sheets (free) — works on phone between classes
✔ GPA calculates automatically — no formulas to figure out
✔ No expensive planner app needed
✔ Lifetime access — use every semester

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR STUDENT SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Weekly Planner + Habit Tracker → search "Student Success System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["annual", "goal"],
        "title": "Annual Goals & 90-Day Action System | Break Big Goals Into Weekly Steps | Google Sheets | Instant Download",
        "tags": [
            "goals planner", "90 day plan google sheets", "annual goal tracker",
            "goal setting system", "life planner", "vision board alternative",
            "milestone tracker", "goal achievement", "quarterly planner",
            "productivity planner", "new year planner", "success planner",
            "action plan template"
        ],
        "description": """Setting goals is easy. Having a system to achieve them is the hard part most people skip.

Research shows that people who write down their goals and break them into specific actions are 42% more likely to achieve them. This is the system that makes that happen.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You set goals in January and forget them by February
✗ Your goals feel too big and overwhelming to start
✗ You have no idea if you're on track to hit your goals this year
✗ You write goals in a notebook and never look at them again

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ See all your life goals (finance, health, career, relationships) in one view
✔ Break each goal into 90-day sprints with clear milestones
✔ Know the specific weekly actions needed to hit each goal
✔ Track your progress percentage — see it grow every week
✔ Complete monthly reviews to adjust and stay on track
✔ Connect your daily habits to your bigger life goals

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Annual Goals Dashboard (all life areas, all goals, one view)
✔ 90-Day Sprint Planner (quarterly goals broken into milestones)
✔ Weekly Action Tracker (what specifically to do this week)
✔ Monthly Review & Reflection (what's working, what to adjust)
✔ Progress Percentage Calculator (auto-tracks your journey)
✔ Habit-to-Goal Connector (link daily habits to annual goals)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — set your 90-day plan today
✔ Google Sheets (free) — review weekly on any device
✔ Covers all life areas — not just career
✔ Proven goal-setting framework built in
✔ Lifetime access — set new goals every quarter

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR PRODUCTIVITY SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Weekly Planner + Habit Tracker → search "Productivity System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["weekly", "productivity"],
        "title": "Weekly Productivity System | Time Blocking Priorities Energy Management | Google Sheets | Instant Download",
        "tags": [
            "weekly planner", "time blocking google sheets", "productivity system",
            "weekly schedule template", "priority planner", "deep work planner",
            "time management system", "work planner", "daily schedule organizer",
            "task management planner", "weekly review template", "focus planner",
            "work life balance planner"
        ],
        "description": """Most people don't have a time problem. They have a priority problem. This system fixes both.

Busy ≠ productive. The difference between people who get results and those who stay stuck is that high performers plan their week with intention — before it starts.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 DOES THIS SOUND FAMILIAR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ You end every week feeling like you did a lot but achieved nothing
✗ Your most important tasks keep getting pushed to "next week"
✗ You react to whatever comes up instead of working on your priorities
✗ By Friday you can't remember what you did on Monday

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHAT YOU'LL BE ABLE TO DO
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Plan your entire week in 15 minutes every Sunday
✔ Protect blocks of deep focus time from meetings and distractions
✔ Identify your top 3 priorities and schedule them first
✔ Match your hardest tasks to your highest energy times of day
✔ End every week knowing you moved the needle on what matters
✔ Have a clear record of what you did and what you planned

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Weekly Time-Block Schedule (30-minute intervals, 7 days)
✔ Top 3 Priority Task List (your non-negotiables for the week)
✔ Daily Task Lists (morning, afternoon, evening)
✔ Weekly Goals & Review (plan Sunday, review Friday)
✔ Meeting & Appointment Tracker
✔ Energy Level Planner (schedule hard tasks at peak energy)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY NASRITOOLS?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this week right now
✔ Google Sheets (free) — open on laptop Monday morning
✔ Based on time-blocking proven by top performers
✔ Works for remote workers, students, and entrepreneurs
✔ Lifetime access — your weekly ritual, every week

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 COMPLETE YOUR PRODUCTIVITY SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
Pair with Goals Planner + Habit Tracker → search "Productivity System" in our shop.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
]

# ─── Bundles — System-Based Repositioning ────────────────────────────────────

BUNDLES = [
    {
        "search_kw": ["finance", "control"],
        "title": "Complete Finance Control System | Budget + Invoices + Goals | 3 Google Sheets | Instant Download",
        "tags": [
            "finance bundle", "budget invoice goals bundle", "google sheets finance",
            "money management system", "freelancer finance bundle", "finance templates bundle",
            "budget tracker bundle", "personal finance system", "financial freedom bundle",
            "money system", "finance google sheets", "budget goals bundle",
            "complete finance kit"
        ],
        "description": """Stop managing money with guesswork. Start using a complete finance system.

This bundle gives you the 3 core tools every financially organized person uses — for less than the price of one meal out.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 THE COMPLETE FINANCE CONTROL SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Budget Tracker — Know exactly where every euro goes every month
✔ Invoice Tracker — Track every client, invoice, and payment (get paid on time)
✔ Goals Planner — Set financial goals and break them into 90-day action plans

Together: €26.97 separately | Bundle Price: €17.99 | You Save: €9

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Freelancers who want to manage BOTH their personal and business finances
✔ Self-employed professionals who hate tax season chaos
✔ Anyone serious about building wealth, not just tracking spending
✔ People who want to go from "I don't know where my money goes" to total clarity

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Instant Download — all 3 systems in your inbox immediately
✔ Google Sheets (free) — works on any device, zero subscriptions
✔ 100% editable — fully customizable for your situation
✔ Auto-calculating — no manual math ever
✔ Lifetime access — use it every year, update it anytime

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → receive 3 download links instantly
2. Open each in Google Sheets → File → Make a Copy
3. Set up each system in under 5 minutes
4. Your complete finance system is running.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["health", "transformation"],
        "title": "Complete Health Transformation System | Workout + Meals + Habits | 3 Google Sheets | Instant Download",
        "tags": [
            "health bundle", "fitness bundle google sheets", "workout meal habit bundle",
            "health transformation kit", "fitness templates bundle", "wellness bundle",
            "workout tracker bundle", "meal planner habit bundle", "health system",
            "fitness planner bundle", "healthy lifestyle bundle", "gym nutrition habit",
            "complete health kit"
        ],
        "description": """Getting healthy isn't about motivation. It's about having the right systems for exercise, nutrition, and daily habits working together.

This bundle gives you all three — the complete health transformation system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 THE COMPLETE HEALTH TRANSFORMATION SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Workout Tracker — Log every session, track PRs, see strength progress auto-charted
✔ Meal Planner — Plan 7-day meals with auto grocery list and nutrition tracking
✔ Habit Tracker — Track 30 daily habits with automatic streak counter

Together: €23.97 separately | Bundle Price: €16.99 | You Save: €7

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone starting a fitness journey who wants a complete system
✔ People who train but eat randomly — this connects both
✔ Anyone building a healthier daily routine from scratch
✔ People who want to see real, measurable physical progress

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Instant Download — start your transformation today
✔ Google Sheets (free) — use on phone at the gym or grocery store
✔ All auto-calculating — nutrition, streaks, PRs tracked automatically
✔ No app subscriptions — own it forever
✔ Lifetime access — your health system for life

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["planning", "productivity"],
        "title": "Complete Planning & Productivity System | Weekly + Student + Goals | 3 Google Sheets | Instant Download",
        "tags": [
            "planner bundle", "productivity bundle google sheets", "weekly student goals bundle",
            "planning system bundle", "planner templates bundle", "productivity kit",
            "organization bundle", "study planner bundle", "life planner bundle",
            "goal setting planner bundle", "productivity system", "schedule planner bundle",
            "complete planner kit"
        ],
        "description": """Most people are busy. Very few are productive. The difference is a planning system.

This bundle gives you everything you need to plan your week, ace your academics, and achieve your biggest goals — all working as one connected system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 THE COMPLETE PLANNING & PRODUCTIVITY SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Weekly Planner — Time-block your week, protect your focus, tackle priorities first
✔ Student Planner — Track assignments, auto-calculate GPA, countdown to exams
✔ Goals Planner — Set annual goals, break into 90-day sprints, track progress %

Together: €23.97 separately | Bundle Price: €16.99 | You Save: €7

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Students who want to improve their grades AND have a life
✔ Anyone who feels busy but unproductive
✔ People who set goals but never follow through
✔ Anyone who wants a complete personal organization system

⚡ Instant Download | Google Sheets Free | Lifetime Access | No Subscription

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["creator", "business"],
        "title": "Complete Creator Business System | Content + Invoices + Budget | 3 Google Sheets | Instant Download",
        "tags": [
            "business bundle", "creator business kit", "content invoice budget bundle",
            "freelancer business bundle", "solopreneur bundle", "creator tools bundle",
            "content creator business", "business templates google sheets", "entrepreneur bundle",
            "freelancer kit", "creator finance bundle", "business system",
            "complete business kit"
        ],
        "description": """Running a creator business without systems means working twice as hard for half the results.

This bundle gives you the three systems every successful creator and freelancer uses to run their business like a CEO.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 THE COMPLETE CREATOR BUSINESS SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Content Creator Planner — Plan content, track analytics, manage brand deals
✔ Invoice Tracker — Track every client and invoice, get paid on time
✔ Budget Tracker — Manage your business and personal finances

Together: €27.97 separately | Bundle Price: €21.99 | You Save: €6

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Content creators who also manage client work or brand deals
✔ Freelancers who create content to market their services
✔ Solopreneurs who need business + marketing + finance in one place
✔ Anyone building an online business around their personal brand

⚡ Instant Download | Google Sheets Free | Lifetime Access | No Subscription

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
    {
        "search_kw": ["complete", "life"],
        "title": "The Complete Life System | All 10 Google Sheets | Finance Health Business Planning | Save 50% | Instant Download",
        "tags": [
            "ultimate bundle", "complete life system", "all google sheets bundle",
            "life management system", "best value bundle", "all templates bundle",
            "complete system bundle", "10 templates bundle", "digital planner bundle",
            "finance health business bundle", "life organization system",
            "productivity finance health bundle", "complete google sheets kit"
        ],
        "description": """Everything you need to run every area of your life — in one purchase, at 50% off.

Most people buy tools one at a time and never build a complete system. This gives you the complete system on day one.

━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ THE COMPLETE LIFE SYSTEM — ALL 10 SYSTEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Budget Tracker — Track income, expenses & savings automatically
✅ Habit Tracker — Build 30 daily habits with auto streak counter
🥗 Meal Planner — Plan 7-day meals + auto grocery list
💍 Wedding Planner — Budget, guests, vendors & timeline
💪 Workout Tracker — Log every session, track PRs, see progress charts
📱 Content Creator Planner — Content calendar, analytics & brand deals
📄 Invoice Tracker — Clients, invoices, payments & tax prep
🎓 Student Planner — Assignments, grades & auto GPA calculator
🎯 Goals Planner — Annual goals + 90-day sprint plans
📅 Weekly Planner — Time-blocking, priorities & daily scheduling

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 THE VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━━
Individual Price: €79.90 total
Bundle Price: €39.99
You Save: €39.91 (50% OFF)

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who wants to upgrade their entire life system at once
✔ People serious about improving their finances, health, AND career
✔ The perfect gift for someone who "has everything" (they don't have systems)
✔ Anyone who wants the best value purchase in our entire shop

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — all 10 systems immediately after purchase
✔ Google Sheets (free) — use on any device, always accessible
✔ 100% editable — fully customize every system
✔ All formulas auto-calculate — no manual math ever
✔ Lifetime access — pay once, yours forever, no subscription
✔ Use on desktop, tablet, and phone simultaneously

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO ACCESS ALL 10 SYSTEMS
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → download the ZIP file immediately
2. Unzip → open each system in Google Sheets
3. File → Make a Copy for each one → saved to your Drive forever
4. All 10 systems running. Your complete life upgrade begins now.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com | Systems That Run Your Life""",
    },
]

# ─── New Shop Announcement ────────────────────────────────────────────────────

NEW_ANNOUNCEMENT = """\
🚀 Welcome to NasriTools — Systems That Run Your Life.

We don't sell spreadsheets. We build Google Sheets systems that help ambitious people take control of their money, health, business, and daily life — without apps, subscriptions, or complexity.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 MOST POPULAR SYSTEMS:
✔ Budget & Expense System — Know where every euro goes
✔ Content Creator Business System — Grow your audience systematically
✔ The Complete Life System — All 10 systems at 50% off
━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 FREE: Download our FREE Budget Tracker Lite — search "Free Budget Tracker" in this shop.

⚡ All systems: Instant Download · Google Sheets (Free) · Lifetime Access · No Subscription Ever

💬 Questions? Message us — we reply within 24 hours.
⭐ Loved your system? A quick review takes 30 seconds and helps us grow!

nasritools.etsy.com
"""


# ─── API Functions ────────────────────────────────────────────────────────────

def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t


def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def fetch_all_listings(token):
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset}, timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("results", [])
        listings.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return listings


def find_listing_id(active_listings, keywords):
    for lst in active_listings:
        title = (lst.get("title") or "").lower()
        if all(kw.lower() in title for kw in keywords):
            return lst["listing_id"]
    return None


def update_listing(token, listing_id, title, tags, description):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"title": title, "tags": tags, "description": description},
        timeout=30,
    )
    return r


def update_announcement(token, text):
    r = requests.put(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"announcement": text},
        timeout=30,
    )
    return r


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Complete Store Repositioning")
    print(f"{'='*65}\n")

    print("  Fetching all active listings…")
    active = fetch_all_listings(token)
    token = get_token()
    print(f"  Found {len(active)} active listings\n")

    ok = 0
    total = len(PRODUCTS) + len(BUNDLES)

    # ── Update Products ────────────────────────────────────────────────────────
    print("  ── PRODUCTS ──")
    for p in PRODUCTS:
        lid = find_listing_id(active, p["search_kw"])
        label = p["title"][:55] + "…"

        if lid is None:
            print(f"  [NOT FOUND] kw={p['search_kw']}")
            continue

        key = str(lid)
        if done.get(key):
            print(f"  [{lid}] skipped (already done)")
            ok += 1
            continue

        print(f"  Updating {lid}: {label}", end=" ")
        r = update_listing(token, lid, p["title"], p["tags"], p["description"])
        time.sleep(1)

        if r.ok:
            print("✓")
            done[key] = True
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:100]}")

        DONE_FILE.write_text(json.dumps(done, indent=2))
        token = get_token()

    # ── Update Bundles ─────────────────────────────────────────────────────────
    print("\n  ── BUNDLES ──")
    for b in BUNDLES:
        lid = find_listing_id(active, b["search_kw"])
        label = b["title"][:55] + "…"

        if lid is None:
            print(f"  [NOT FOUND] kw={b['search_kw']}")
            continue

        key = str(lid)
        if done.get(key):
            print(f"  [{lid}] skipped (already done)")
            ok += 1
            continue

        print(f"  Updating {lid}: {label}", end=" ")
        r = update_listing(token, lid, b["title"], b["tags"], b["description"])
        time.sleep(1)

        if r.ok:
            print("✓")
            done[key] = True
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:100]}")

        DONE_FILE.write_text(json.dumps(done, indent=2))
        token = get_token()

    # ── Update Shop Announcement ───────────────────────────────────────────────
    print("\n  ── SHOP ANNOUNCEMENT ──")
    print("  Updating announcement…", end=" ")
    r = update_announcement(token, NEW_ANNOUNCEMENT)
    if r.ok:
        print("✓")
    else:
        print(f"✗  {r.status_code}: {r.text[:100]}")

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} listings repositioned")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
