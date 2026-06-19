"""
NasriTools - SEO Optimizer
Updates titles, tags, and descriptions for all 10 core products using the
Systems-based marketing framework (sell solutions, not files).
Run: python optimize_seo.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_seo_done.json"

# ─── Product SEO Data ──────────────────────────────────────────────────────────
# Each product: listing_id, optimized title, 13 tags, full description
PRODUCTS = [
    {
        "keywords": ["budget", "tracker"],
        "title": "Budget Tracker Spreadsheet Google Sheets | Monthly Budget Planner | Expense Tracker | Personal Finance Template | Instant Download",
        "tags": [
            "budget tracker", "expense tracker", "google sheets template",
            "monthly budget", "budget planner", "financial planner",
            "money tracker", "budget spreadsheet", "personal finance",
            "savings tracker", "income tracker", "spending tracker",
            "excel budget"
        ],
        "description": """Take control of your money in under 5 minutes.
This Budget Tracker spreadsheet helps you track every expense, plan your monthly budget, and build savings — automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who wants to stop overspending
✔ People who want to save more money every month
✔ Anyone who feels lost when it comes to their finances
✔ Anyone tired of checking their balance and being surprised

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Monthly Budget Dashboard (auto-calculating)
✔ Income & Expense Tracker (50+ categories)
✔ Savings Goal Tracker
✔ Bill Payment Tracker
✔ Annual Overview (all 12 months at a glance)
✔ Net Worth Calculator

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start using in minutes
✔ Works on Google Sheets (free) and Microsoft Excel
✔ 100% Editable — change colors, categories, everything
✔ Auto-calculating formulas — no manual math
✔ Lifetime access — yours forever after purchase
✔ No subscription, no app, no monthly fees

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → receive download link instantly
2. Click the link → open in Google Sheets
3. File → Make a Copy → saved to your Drive forever
4. Enter your income and expenses → watch it auto-calculate

Setup time: Under 5 minutes. No technical skills needed.

━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: Do I need to pay for Google Sheets?
A: No! Google Sheets is completely free. You just need a Google account.

Q: Can I use this on my phone?
A: Yes! Google Sheets works on iOS and Android with the free app.

Q: Can I edit the categories and colors?
A: Absolutely — everything is fully customizable.

Q: Is there a monthly fee?
A: No. You pay once and own it forever.

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com""",
    },
    {
        "listing": 4487740567,
        "title": "Habit Tracker Spreadsheet Google Sheets | Daily Habit Planner | 30 Day Habit Tracker | Streak Counter | Instant Download",
        "tags": [
            "habit tracker", "daily habit tracker", "google sheets template",
            "habit planner", "30 day challenge", "streak tracker",
            "routine tracker", "productivity tracker", "self improvement",
            "wellness tracker", "morning routine", "goal tracker",
            "daily planner"
        ],
        "description": """Build life-changing habits in 30 days — automatically tracked.
This Habit Tracker spreadsheet shows your streaks, progress, and momentum every single day so you never break the chain.

━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who wants to build healthy daily routines
✔ People doing 30-day challenges
✔ Anyone who keeps starting habits and giving up
✔ People who want visual proof of their progress

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Monthly Habit Grid (track up to 30 habits simultaneously)
✔ Auto-Streak Counter (never lose count)
✔ Weekly Completion Rate (%)
✔ Monthly Progress Dashboard
✔ Annual Habit Review
✔ Habit Notes & Reflection Section

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start today, not tomorrow
✔ Works on Google Sheets (free) and Microsoft Excel
✔ 100% Editable — track any habit you want
✔ Auto-calculates your streaks and completion rates
✔ Lifetime access — yours forever
✔ No app, no subscription, no fees

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → download link arrives instantly
2. Open in Google Sheets → File → Make a Copy
3. Add your habits in the first column
4. Check off each day and watch your streaks grow!

Setup time: Under 3 minutes.

━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: How many habits can I track?
A: Up to 30 habits per month simultaneously.

Q: Does it work on mobile?
A: Yes, Google Sheets app is free on iOS and Android.

Q: Can I change the habit names?
A: Yes, everything is fully customizable.

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487742011,
        "title": "Meal Planner Spreadsheet Google Sheets | Weekly Meal Plan Template | Grocery List | Nutrition Tracker | Instant Download",
        "tags": [
            "meal planner", "weekly meal plan", "google sheets template",
            "grocery list", "meal prep", "nutrition tracker",
            "food planner", "healthy eating", "diet planner",
            "family meal planner", "recipe planner", "calorie tracker",
            "meal planning template"
        ],
        "description": """Plan a full week of healthy meals in under 15 minutes.
This Meal Planner spreadsheet helps you plan meals, build grocery lists, and track nutrition — all in one beautiful template.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🥗 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who wants to eat healthier but doesn't know where to start
✔ People who overspend on groceries (no plan = wasted food)
✔ Meal preppers who want an organized system
✔ Families planning weekly dinners

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ 7-Day Meal Plan (breakfast, lunch, dinner, snacks)
✔ Auto-Generated Grocery List
✔ Nutrition Tracker (calories, protein, carbs, fat)
✔ Monthly Meal Calendar
✔ Recipe Database Sheet
✔ Budget Tracker for groceries

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this week's meals today
✔ Works on Google Sheets (free) and Microsoft Excel
✔ Fully customizable — add your own recipes
✔ Auto-calculates nutrition totals
✔ Lifetime access — no subscription ever

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET STARTED
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → instant download
2. Open in Google Sheets → Make a Copy
3. Add your meals for the week
4. Print or use on your phone while shopping

Setup time: Under 5 minutes.

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487743321,
        "title": "Wedding Planner Spreadsheet Google Sheets | Wedding Budget Tracker | Guest List Manager | Vendor Tracker | Instant Download",
        "tags": [
            "wedding planner", "wedding budget tracker", "google sheets template",
            "guest list manager", "wedding checklist", "vendor tracker",
            "wedding organizer", "bride planner", "wedding spreadsheet",
            "wedding timeline", "seating chart", "wedding budget",
            "bridal planner"
        ],
        "description": """Plan your perfect wedding without the stress — or the chaos.
This Wedding Planner spreadsheet keeps your budget, guest list, vendors, and timeline all in one place so nothing falls through the cracks.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💍 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Engaged couples planning their wedding
✔ Brides who want to stay organized and on budget
✔ Anyone overwhelmed by wedding planning apps
✔ Couples planning a wedding on a specific budget

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Wedding Budget Tracker (track every expense vs. budget)
✔ Guest List Manager (RSVPs, dietary needs, seating)
✔ Vendor Tracker (contracts, deposits, contact info)
✔ Master Wedding Checklist (month-by-month tasks)
✔ Wedding Day Timeline
✔ Budget Summary Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start planning today
✔ Works on Google Sheets (free) and Microsoft Excel
✔ Share with your partner or wedding planner
✔ 100% customizable for your wedding style
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487744011,
        "title": "Workout Tracker Spreadsheet Google Sheets | Gym Log Template | Fitness Progress Tracker | Exercise Journal | Instant Download",
        "tags": [
            "workout tracker", "gym tracker", "google sheets template",
            "fitness tracker", "exercise log", "weight lifting tracker",
            "gym log", "training log", "strength tracker",
            "fitness planner", "workout journal", "progress tracker",
            "bodybuilding tracker"
        ],
        "description": """Track every rep, every set, every PR — and watch yourself get stronger.
This Workout Tracker spreadsheet logs your gym sessions, tracks personal records, and shows your progress over time automatically.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Gym-goers who want to track their progress
✔ Anyone doing strength training or bodybuilding
✔ Fitness enthusiasts who want to beat their PRs
✔ Anyone who wants to stop guessing at the gym

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Workout Log (sets, reps, weight, notes)
✔ Personal Record (PR) Tracker
✔ Weekly Training Schedule
✔ Progress Charts (auto-generated)
✔ Exercise Database (100+ exercises)
✔ Body Measurements Tracker

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — log your next session today
✔ Works on Google Sheets (free) and Microsoft Excel
✔ Auto-charts your strength progress
✔ No gym app subscription required
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487745211,
        "title": "Content Creator Planner Google Sheets | Social Media Calendar | Content Calendar Template | Instagram YouTube Planner | Instant Download",
        "tags": [
            "content planner", "social media calendar", "google sheets template",
            "content creator", "instagram planner", "youtube planner",
            "content calendar", "social media planner", "influencer planner",
            "tiktok planner", "content schedule", "marketing planner",
            "blog planner"
        ],
        "description": """Plan 3 months of content in one weekend — and never run out of ideas.
This Content Creator Planner helps you schedule posts, track analytics, manage collaborations, and grow your audience systematically.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Content creators on Instagram, YouTube, TikTok, or blogs
✔ Social media managers handling multiple accounts
✔ Anyone who posts content but has no system
✔ Influencers who want to track brand deals and revenue

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Monthly Content Calendar (plan all platforms)
✔ Content Ideas Bank (never run dry)
✔ Platform Analytics Tracker (followers, engagement, reach)
✔ Brand Collaboration Tracker (deals, deadlines, payments)
✔ Revenue Tracker (sponsorships, affiliate, products)
✔ Content Performance Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this month's content today
✔ Works on Google Sheets (free) — accessible anywhere
✔ Multi-platform: Instagram + YouTube + TikTok + Blog
✔ No subscription, no complicated tool to learn
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487744321,
        "title": "Freelancer Invoice Tracker Google Sheets | Client Management Template | Business Finance Tracker | Self Employed Tax Prep | Instant Download",
        "tags": [
            "freelancer invoice tracker", "client tracker", "google sheets template",
            "invoice tracker", "freelancer planner", "self employed",
            "business finance tracker", "tax prep", "client management",
            "freelance business", "income tracker", "payment tracker",
            "small business tracker"
        ],
        "description": """Stop losing money to disorganized invoices and forgotten payments.
This Freelancer Invoice Tracker manages every client, invoice, payment, and deadline — so you get paid on time, every time.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Freelancers tired of chasing unpaid invoices
✔ Self-employed professionals who hate tax season
✔ Anyone managing multiple clients simultaneously
✔ Small business owners who need simple bookkeeping

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Invoice Tracker (all invoices, statuses, due dates)
✔ Client Database (contact info, project history)
✔ Payment Status Dashboard (paid / pending / overdue)
✔ Monthly & Annual Revenue Summary
✔ Tax Prep Sheet (income and deductible expenses)
✔ Project Time Tracker

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start managing clients today
✔ Works on Google Sheets (free) and Microsoft Excel
✔ No monthly accounting software fees
✔ Auto-calculates outstanding and total revenue
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487742911,
        "title": "Student Planner Spreadsheet Google Sheets | Study Schedule Template | Grade Tracker | GPA Calculator | College Planner | Instant Download",
        "tags": [
            "student planner", "study planner", "google sheets template",
            "grade tracker", "gpa calculator", "college planner",
            "assignment tracker", "study schedule", "student organizer",
            "homework tracker", "exam planner", "school planner",
            "university planner"
        ],
        "description": """Organize your entire semester in one place — and actually hit your GPA goal.
This Student Planner tracks assignments, deadlines, grades, and study time so you stay on top of everything without the stress.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ University and college students
✔ Students who miss deadlines or forget assignments
✔ Anyone who wants to improve their GPA
✔ Students balancing classes, work, and social life

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Assignment Tracker (all subjects, due dates, status)
✔ Grade Tracker with auto-calculated GPA
✔ Weekly Study Schedule
✔ Exam Countdown Calendar
✔ Semester Overview Dashboard
✔ Study Hours Log

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — organize your semester today
✔ Works on Google Sheets (free) — use on any device
✔ Auto-calculates your GPA in real time
✔ No expensive planner apps needed
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487743721,
        "title": "Goals Planner Spreadsheet Google Sheets | Annual Goal Tracker | 90 Day Plan Template | Vision Board Alternative | Instant Download",
        "tags": [
            "goals planner", "goal tracker", "google sheets template",
            "annual planner", "90 day plan", "vision board",
            "life planner", "goal setting", "productivity planner",
            "new year planner", "milestone tracker", "achievement tracker",
            "success planner"
        ],
        "description": """Set goals that actually stick — and build the system to achieve them.
This Goals Planner breaks down your annual goals into 90-day milestones and weekly actions, so you make real progress every single week.

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who sets goals and never follows through
✔ People who want to go from "dreaming" to "doing"
✔ Anyone who wants a structured system for personal growth
✔ Entrepreneurs and professionals with ambitious targets

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Annual Goals Dashboard (all life areas: health, finance, career, relationships)
✔ 90-Day Sprint Planner (quarterly breakdowns)
✔ Weekly Action Tracker
✔ Monthly Review & Reflection
✔ Progress Percentage Calculator
✔ Habit-to-Goal Connector

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — start today, not January 1st
✔ Works on Google Sheets (free) and Microsoft Excel
✔ Covers all life areas in one template
✔ No motivation app subscription needed
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4487742511,
        "title": "Weekly Planner Spreadsheet Google Sheets | Time Blocking Template | Productivity Planner | Daily Schedule Organizer | Instant Download",
        "tags": [
            "weekly planner", "time blocking", "google sheets template",
            "productivity planner", "daily schedule", "work planner",
            "time management", "weekly schedule", "task planner",
            "priority planner", "daily planner", "schedule template",
            "work life balance"
        ],
        "description": """Plan your perfect week in 15 minutes every Sunday — and actually follow through.
This Weekly Planner uses time-blocking to help you prioritize the right tasks, protect your time, and get more done with less stress.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Busy professionals who feel overwhelmed
✔ Anyone who wants to be more productive
✔ People who end every week feeling like they accomplished nothing
✔ Remote workers who need structure at home

━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Weekly Time-Block Schedule (30-min intervals)
✔ Priority Task List (Top 3 most important tasks)
✔ Daily To-Do Lists
✔ Weekly Goals & Review
✔ Meeting & Appointment Tracker
✔ Energy Level Planner (plan hard tasks when you're sharpest)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ WHY THIS TEMPLATE?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — plan this week right now
✔ Works on Google Sheets (free) and Microsoft Excel
✔ Based on proven time-blocking productivity system
✔ No app subscription or complicated tools
✔ Lifetime access — yours forever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
]

# Bundle SEO updates
BUNDLES = [
    {
        "listing": 4524283814,
        "title": "Finance Bundle | Budget Tracker + Invoice Tracker + Goals Planner | Google Sheets Templates | Save 50% | Instant Download",
        "tags": [
            "finance bundle", "budget tracker", "invoice tracker",
            "goals planner", "google sheets bundle", "finance templates",
            "money management", "financial planner", "freelancer finance",
            "budget bundle", "personal finance", "financial freedom",
            "expense tracker bundle"
        ],
        "description": """Get 3 essential finance templates for the price of 1 — and take complete control of your money.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 WHAT'S IN THE BUNDLE (Save 50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Budget Tracker — track income, expenses & savings monthly
✔ Freelancer Invoice Tracker — manage clients, invoices & payments
✔ Goals Planner — set annual goals & break them into 90-day actions

Individually: €25.97 | Bundle Price: €17.99 | You Save: €8

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Freelancers who want to manage money AND clients in one system
✔ Anyone serious about achieving financial goals this year
✔ People who want a complete personal finance system

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Instant Download — access all 3 templates immediately
✔ Works on Google Sheets (free) and Microsoft Excel
✔ 100% Editable — customize everything
✔ Auto-calculating formulas throughout
✔ Lifetime access — yours forever
✔ No subscription, no monthly fees

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW IT WORKS
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → receive 3 download links instantly
2. Open each in Google Sheets → File → Make a Copy
3. Start using immediately — setup under 5 min each

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com""",
    },
    {
        "listing": 4524276503,
        "title": "Health Bundle | Workout Tracker + Meal Planner + Habit Tracker | Google Sheets Templates | Save 50% | Instant Download",
        "tags": [
            "health bundle", "workout tracker", "meal planner",
            "habit tracker", "google sheets bundle", "fitness templates",
            "health planner", "wellness bundle", "fitness bundle",
            "healthy lifestyle", "gym tracker", "nutrition planner",
            "self improvement bundle"
        ],
        "description": """Build the body and lifestyle you want — with 3 templates that work together as a complete system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💪 WHAT'S IN THE BUNDLE (Save 50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Workout Tracker — log every session, track PRs and strength progress
✔ Meal Planner — plan 7-day meals with auto grocery list
✔ Habit Tracker — track 30 daily habits with streak counter

Individually: €25.97 | Bundle Price: €16.99 | You Save: €9

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone starting a fitness journey
✔ People who want to eat healthy AND train consistently
✔ Anyone building a healthier daily routine

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Instant Download — start your health journey today
✔ Works on Google Sheets (free) and Microsoft Excel
✔ 100% customizable for your goals and schedule
✔ Auto-tracking and progress charts built in
✔ Lifetime access — no subscription ever

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4524276527,
        "title": "Planner Bundle | Weekly Planner + Student Planner + Goals Planner | Google Sheets Templates | Save 50% | Instant Download",
        "tags": [
            "planner bundle", "weekly planner", "student planner",
            "goals planner", "google sheets bundle", "planner templates",
            "productivity bundle", "study planner", "life planner",
            "academic planner", "organization bundle", "schedule planner",
            "planner set"
        ],
        "description": """Plan your week, ace your studies, and hit your goals — all in one complete planning system.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 WHAT'S IN THE BUNDLE (Save 50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Weekly Planner — time-blocking, priorities, and daily task lists
✔ Student Planner — assignments, grades, GPA tracker & study schedule
✔ Goals Planner — annual goals broken into 90-day action plans

Individually: €25.97 | Bundle Price: €16.99 | You Save: €9

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Students who want to improve grades AND stay organized
✔ Anyone who wants a complete personal planning system
✔ People who set goals but struggle to follow through

⚡ Instant Download | Google Sheets (Free) | Lifetime Access | No Subscription

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4524276553,
        "title": "Business Bundle | Content Planner + Invoice Tracker + Goals Planner | Google Sheets Templates | Save 50% | Instant Download",
        "tags": [
            "business bundle", "content planner", "invoice tracker",
            "goals planner", "google sheets bundle", "business templates",
            "freelancer bundle", "solopreneur bundle", "entrepreneur planner",
            "business planner", "small business", "content calendar",
            "business kit"
        ],
        "description": """Run your business like a CEO — with 3 templates that cover marketing, finance, and strategy.

━━━━━━━━━━━━━━━━━━━━━━━━━━
💼 WHAT'S IN THE BUNDLE (Save 50%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Content Creator Planner — content calendar, analytics & collaboration tracker
✔ Invoice Tracker — manage clients, invoices, payments & tax prep
✔ Goals Planner — quarterly business goals & KPI tracking

Individually: €28.97 | Bundle Price: €21.99 | You Save: €7

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Freelancers who want to grow their business systematically
✔ Content creators who also manage client work
✔ Solopreneurs who need business + marketing + goals in one place

⚡ Instant Download | Google Sheets (Free) | Lifetime Access | No Subscription

Questions? Message us on Etsy — we reply within 24 hours. ♥""",
    },
    {
        "listing": 4524283886,
        "title": "Ultimate Bundle | All 10 Google Sheets Templates | Save 65% | Finance + Health + Business + Productivity | Instant Download",
        "tags": [
            "ultimate bundle", "google sheets bundle", "template bundle",
            "budget tracker", "habit tracker", "meal planner",
            "complete bundle", "all templates", "productivity bundle",
            "life planner bundle", "finance health business", "best value bundle",
            "digital planner bundle"
        ],
        "description": """Everything you need to manage your entire life — in one complete system at 65% off.
10 premium Google Sheets templates covering finance, health, business, planning, and lifestyle.

━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ ALL 10 TEMPLATES INCLUDED (Save 65%)
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Budget Tracker — track income, expenses & build savings
✅ Habit Tracker — 30 daily habits with auto streak counter
🥗 Meal Planner — 7-day meals + auto grocery list
💍 Wedding Planner — budget, guests, vendors & timeline
💪 Workout Tracker — gym log, PRs & progress charts
📱 Content Creator Planner — content calendar & analytics
📄 Invoice Tracker — clients, payments & tax prep
🎓 Student Planner — assignments, grades & GPA calculator
🎯 Goals Planner — annual goals + 90-day action plans
📅 Weekly Planner — time-blocking & priority tasks

Individually: €89.90 | Bundle Price: €39.99 | You Save: €49.91 (65% OFF)

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 WHO IS THIS FOR?
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Anyone who wants a complete life management system
✔ People serious about improving every area of life
✔ Best value purchase for anyone using Google Sheets
✔ Perfect gift for students, professionals, or anyone who loves organizing

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ BUNDLE FEATURES
━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ INSTANT DOWNLOAD — all 10 templates immediately after purchase
✔ Works on Google Sheets (free) and Microsoft Excel
✔ 100% Editable — customize colors, categories, everything
✔ All formulas auto-calculate — no manual math
✔ Lifetime access — yours forever, no subscription ever
✔ Access on any device (desktop, tablet, mobile)

━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO ACCESS ALL 10 TEMPLATES
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Purchase → download the ZIP file instantly
2. Unzip → open each template in Google Sheets
3. File → Make a Copy for each → saved to your Drive forever
4. Start using all 10 immediately!

Questions? Message us on Etsy — we reply within 24 hours. ♥
nasritools.etsy.com""",
    },
]


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


def update_listing_seo(token, product):
    lid = product["listing"]
    payload = {
        "title":       product["title"],
        "tags":        product["tags"],
        "description": product["description"],
    }
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    return r


def fetch_all_listings(token):
    """Fetch all active listings from the shop."""
    listings, offset = [], 0
    while True:
        r = requests.get(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": 100, "offset": offset},
            timeout=30,
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


def find_listing_id(active_listings, search_keywords):
    """Find listing ID by matching ALL keywords in the title (case-insensitive)."""
    for lst in active_listings:
        title = (lst.get("title") or "").lower()
        if all(kw.lower() in title for kw in search_keywords):
            return lst["listing_id"]
    return None


# Maps each product to search keywords that uniquely identify it
PRODUCT_KEYWORDS = {
    0: ["budget", "tracker"],           # Budget Tracker
    1: ["habit", "tracker"],            # Habit Tracker
    2: ["meal", "planner"],             # Meal Planner
    3: ["wedding", "planner"],          # Wedding Planner
    4: ["workout", "tracker"],          # Workout Tracker
    5: ["content", "creator", "planner"],  # Content Creator
    6: ["invoice", "tracker"],          # Invoice Tracker
    7: ["student", "planner"],          # Student Planner
    8: ["goals", "planner"],            # Goals Planner
    9: ["weekly", "planner"],           # Weekly Planner
}

BUNDLE_KEYWORDS = {
    0: ["finance", "bundle"],
    1: ["health", "bundle"],
    2: ["planner", "bundle"],
    3: ["business", "bundle"],
    4: ["ultimate", "bundle"],
}


def main():
    done = {}
    if DONE_FILE.exists():
        done = json.loads(DONE_FILE.read_text())

    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - SEO Optimizer (auto-discover listing IDs)")
    print(f"{'='*65}\n")

    # Fetch all active listings once
    print("  Fetching all active listings to discover IDs…")
    active = fetch_all_listings(token)
    print(f"  Found {len(active)} active listings\n")
    token = get_token()

    all_items = [
        (PRODUCT_KEYWORDS, PRODUCTS),
        (BUNDLE_KEYWORDS,  BUNDLES),
    ]

    ok = 0
    total = len(PRODUCTS) + len(BUNDLES)

    for kw_map, item_list in all_items:
        for idx, p in enumerate(item_list):
            keywords = kw_map.get(idx, [])
            lid = find_listing_id(active, keywords)
            label = p["title"][:55] + "…"

            if lid is None:
                print(f"  [NOT FOUND] keywords={keywords} — {label}")
                continue

            key = str(lid)
            if done.get(key):
                print(f"  [{lid}] skipped (already updated)")
                ok += 1
                continue

            print(f"  Updating {lid}: {label}", end=" ")
            p_copy = dict(p)
            p_copy["listing"] = lid
            r = update_listing_seo(token, p_copy)
            time.sleep(1)

            if r.ok:
                print("✓")
                done[key] = True
                ok += 1
            else:
                print(f"✗  {r.status_code}: {r.text[:120]}")

            DONE_FILE.write_text(json.dumps(done, indent=2))
            token = get_token()

    print(f"\n{'='*65}")
    print(f"  Done: {ok}/{total} listings updated")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
