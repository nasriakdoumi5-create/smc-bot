"""
NasriTools - Update Etsy Listing SEO (Title + Description + Tags)
Updates 10 individual products via Etsy API v3.
Matches listings by searching active listing titles for keywords.

Run: python update_seo.py
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

API = "https://api.etsy.com/v3/application"

SEO_DATA = [
    {
        "search_kw": ["budget", "expense"],
        "title": "Budget Tracker Google Sheets Template 2025 | Monthly Expense Tracker | Personal Finance Planner | Instant Download",
        "tags": ["budget tracker", "expense tracker", "google sheets", "finance planner", "monthly budget", "personal finance", "money tracker", "digital download", "budget template", "savings tracker", "finance template", "spreadsheet", "instant download"],
        "description": """Stop guessing where your money went. Start knowing.

This Budget & Expense Tracker is a professional, ready-to-use Google Sheets template that automatically calculates your expenses, tracks your savings goals, and shows you exactly where every euro goes — every month.

No formulas to build. No accountant needed. Open it, enter your numbers, done.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Monthly Budget Dashboard (auto-totals everything)
✅ Daily Expense Log (50+ categories)
✅ Savings Goals Tracker
✅ Category Breakdown Overview
✅ Annual 12-Month Summary
✅ Budget vs Actual Comparison

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize it?
A: Yes. Colors, categories, amounts — everything is editable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Finance Bundle — Budget + Invoice + Goals (Save 33%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["habit", "building"],
        "title": "Habit Tracker Google Sheets Template 2025 | 30-Day Habit Challenge | Daily Routine Planner | Instant Download",
        "tags": ["habit tracker", "30 day challenge", "google sheets", "daily planner", "habit builder", "routine planner", "habit template", "digital download", "morning routine", "productivity", "self improvement", "spreadsheet", "instant download"],
        "description": """Most people quit their habits by day 10. This system makes sure you don't.

This 30-Day Habit Tracker is a professional Google Sheets template with automatic streak counting, daily check-ins, and a visual progress dashboard that makes it impossible to miss a day without noticing.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 30-Day Habit Grid (track up to 20 habits daily)
✅ Automatic Streak Counter
✅ Weekly Check-In & Reflection Sheet
✅ Monthly Progress Overview
✅ Pre-loaded Habit Templates (fully customizable)
✅ Visual Completion % Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize it?
A: Yes. Habits, colors, layout — all editable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Health Bundle — Habits + Workout + Meal Plan (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["meal", "planning"],
        "title": "Meal Planner Google Sheets Template 2025 | Weekly Meal Plan | Auto Grocery List | Nutrition Tracker | Digital Download",
        "tags": ["meal planner", "weekly meal plan", "google sheets", "grocery list", "nutrition tracker", "meal prep", "diet planner", "digital download", "food planner", "healthy eating", "meal template", "spreadsheet", "instant download"],
        "description": """Meal planning takes 3 hours. This template makes it 15 minutes.

This Weekly Meal Planner is a professional Google Sheets template that automatically generates your grocery list, tracks your daily calories, and plans your full week of meals in minutes — not hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 7-Day Meal Plan Grid (Breakfast, Lunch, Dinner)
✅ Auto Grocery List Generator
✅ Daily Calorie Counter
✅ Weekly Shopping Budget Tracker
✅ Pantry & Inventory Tracker
✅ Meal Ideas Database (50+ recipes)

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize meals and categories?
A: Yes. All meals, recipes, and categories are fully editable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Health Bundle — Meal Plan + Workout + Habits (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["wedding", "planning"],
        "title": "Wedding Planner Google Sheets Template 2025 | Budget Tracker | Guest List | Vendor Manager | Digital Download",
        "tags": ["wedding planner", "wedding budget", "google sheets", "guest list", "vendor tracker", "wedding organizer", "bride to be", "digital download", "wedding template", "event planner", "wedding checklist", "spreadsheet", "instant download"],
        "description": """The average wedding goes 30% over budget. This system won't let yours.

This Complete Wedding Planner is a professional Google Sheets template that tracks every expense, manages every vendor, organizes your full guest list, and gives you a real-time overview of your entire wedding — from first venue visit to the last dance.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Full Wedding Budget Tracker (20+ categories)
✅ Guest List & RSVP Manager
✅ Vendor Contact & Status Sheet
✅ Day-of Timeline Builder
✅ Seating Chart Organizer
✅ Wedding Countdown Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize categories and budget amounts?
A: Yes. Everything is fully editable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 PLAN EVERYTHING IN ONE PLACE
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["workout", "tracking"],
        "title": "Workout Tracker Google Sheets Template 2025 | Gym Log | Exercise Progress Tracker | Fitness Planner | Digital Download",
        "tags": ["workout tracker", "gym log", "google sheets", "fitness planner", "exercise tracker", "weight training", "fitness template", "digital download", "strength tracker", "gym tracker", "fitness journal", "spreadsheet", "instant download"],
        "description": """The gym gets easier once you track every session. Here's your system.

This Gym & Workout Tracker is a professional Google Sheets template that logs every exercise, tracks your personal records automatically, and shows you exactly how much stronger you're getting — session by session.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Exercise Log (unlimited sessions, any program)
✅ Personal Record (PR) Tracker
✅ Weekly Volume & Progress Calculator
✅ Auto-generated Progress Charts
✅ Exercise Library (50+ exercises)
✅ Body Measurements & Weight Log

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I add my own exercises?
A: Yes. You can add, remove, and customize everything.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Health Bundle — Workout + Meal Plan + Habits (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["content", "creator"],
        "title": "Content Creator Planner Google Sheets 2025 | Social Media Calendar | YouTube TikTok Instagram Tracker | Digital Download",
        "tags": ["content creator", "social media", "google sheets", "content calendar", "youtube planner", "tiktok planner", "instagram planner", "digital download", "creator tools", "content schedule", "brand deals", "spreadsheet", "instant download"],
        "description": """Random posting is dead. Consistent systems win. Here's yours.

This Content Creator Business System is a professional Google Sheets template that plans your full content calendar, tracks your analytics across all platforms, manages brand deals, and shows you exactly what's working — so you can double down on it.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 90-Day Content Calendar (YouTube, TikTok, Instagram, etc.)
✅ Multi-Platform Analytics Tracker
✅ Brand Deal CRM (never miss a collaboration)
✅ Content Ideas Database
✅ Income & Expense Log
✅ Audience Growth Chart

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I add my own platforms and categories?
A: Yes. Fully editable and customizable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Business Bundle — Content + Invoice + Budget (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["invoice", "client"],
        "title": "Invoice Tracker Google Sheets Template 2025 | Freelancer Finance | Client Management | Business Tracker | Digital Download",
        "tags": ["invoice tracker", "freelancer tools", "google sheets", "client tracker", "business finance", "income tracker", "self employed", "digital download", "invoice template", "tax tracker", "billing tracker", "spreadsheet", "instant download"],
        "description": """Stop chasing unpaid invoices. See everything at a glance — and get paid on time.

This Freelancer Invoice & Client System is a professional Google Sheets template that tracks every invoice, manages your client relationships, calculates your monthly revenue, and has your tax summary ready whenever you need it.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Invoice Tracker (paid, pending, overdue — all at a glance)
✅ Client Database & CRM
✅ Monthly & Annual Revenue Summary
✅ Tax Preparation Sheet (auto-calculated)
✅ Expense Tracker for Business
✅ Outstanding Payment Dashboard

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize invoice categories and client fields?
A: Yes. Fully editable to fit your business.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Finance Bundle — Invoice + Budget + Goals (Save 33%)
⭐ Business Bundle — Invoice + Content + Budget (Save 50%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["student", "academic"],
        "title": "Student Planner Google Sheets Template 2025 | Academic Planner | Grade Tracker | GPA Calculator | College Planner",
        "tags": ["student planner", "academic planner", "google sheets", "grade tracker", "gpa calculator", "college planner", "study planner", "digital download", "school organizer", "homework tracker", "exam planner", "spreadsheet", "instant download"],
        "description": """The students with the best grades aren't the smartest. They're the most organized.

This Student Academic Planner is a professional Google Sheets template that tracks every assignment, calculates your GPA live, builds your study schedule, and makes sure you never miss a deadline again.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Assignment & Deadline Tracker
✅ Live GPA Calculator (auto-updates)
✅ Study Schedule Builder
✅ Exam Countdown Dashboard
✅ Grade Tracker per Subject
✅ Semester Overview Summary

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I add my own subjects and assignment types?
A: Yes. Fully customizable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Planning Bundle — Student + Goals + Weekly (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["annual", "goal"],
        "title": "Goal Planner Google Sheets Template 2025 | 90-Day Planner | Annual Goal Tracker | Life Planner | Digital Download",
        "tags": ["goal planner", "90 day planner", "google sheets", "annual planner", "life planner", "goal tracker", "vision board", "digital download", "goal template", "success planner", "action planner", "spreadsheet", "instant download"],
        "description": """A goal without a system is just a wish. Here's your system.

This Annual Goals & 90-Day Action Planner is a professional Google Sheets template that breaks your big goals into weekly steps, tracks your progress automatically, and keeps you on schedule all year long.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Annual Goals Dashboard (track up to 12 goals)
✅ 90-Day Sprint Planner
✅ Weekly Action Steps Breakdown
✅ Auto Progress % Calculator
✅ Habit-to-Goal Linking System
✅ Year-End Review & Reflection Sheet

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I add my own goals and milestones?
A: Yes. Fully editable and customizable.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Finance Bundle — Goals + Budget + Invoice (Save 33%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
    {
        "search_kw": ["weekly", "productivity"],
        "title": "Weekly Planner Google Sheets Template 2025 | Productivity Planner | Time Blocking | Task Manager | Digital Download",
        "tags": ["weekly planner", "productivity", "google sheets", "time blocking", "task manager", "work planner", "daily planner", "digital download", "weekly template", "schedule planner", "time management", "spreadsheet", "instant download"],
        "description": """Your week won't plan itself. 15 minutes on Sunday. Done for the whole week.

This Weekly Productivity System is a professional Google Sheets template with time-blocking, priority ranking, and task tracking that helps you do 2x more work in less time — every single week.

━━━━━━━━━━━━━━━━━━━━━━━━━
📋 WHAT'S INSIDE
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Time-Blocked Weekly Grid (Monday to Sunday)
✅ Top 3 Priorities System (the 3 things that matter most)
✅ Task Completion Tracker with % score
✅ Energy Level & Focus Planner
✅ Rolling To-Do List (never lose a task)
✅ Weekly Reflection & Review Sheet

━━━━━━━━━━━━━━━━━━━━━━━━━
💻 COMPATIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Google Sheets — 100% FREE, all features work
✅ Microsoft Excel — fully compatible
✅ Mac & PC — works in any browser
✅ iPhone & Android — via Google Sheets app (free)

━━━━━━━━━━━━━━━━━━━━━━━━━
📥 HOW TO GET IT (2 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━

1. Complete your purchase
2. Open the PDF you receive instantly
3. Click the Google Sheets link → File → Make a Copy → done

━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Is Google Sheets free?
A: Yes, 100% free. You only need a Google account.

Q: Can I customize the time blocks and categories?
A: Yes. Fully editable to fit your schedule.

Q: Is this a physical product?
A: No. This is a digital file — instant access after purchase.

Q: Does it work on Mac or iPhone?
A: Yes. Works on any device with a browser.

Q: What if I need help?
A: Message us anytime — we respond within 24 hours.

━━━━━━━━━━━━━━━━━━━━━━━━━
💼 SAVE MORE WITH BUNDLES
━━━━━━━━━━━━━━━━━━━━━━━━━

⭐ Planning Bundle — Weekly + Goals + Student (Save 50%)
⭐ Complete Life System — All 10 templates (Save 65%)

→ See all our tools: nasritools.etsy.com""",
    },
]


# ── Auth ───────────────────────────────────────────────────────────────────────

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
    return {
        "Authorization": "Bearer " + token["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


# ── API helpers ────────────────────────────────────────────────────────────────

def fetch_active_listings(token):
    """Fetch all active listings for the shop (handles pagination)."""
    listings = []
    offset = 0
    limit = 100
    while True:
        r = requests.get(
            f"{API}/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(token),
            params={"limit": limit, "offset": offset},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        listings.extend(results)
        if len(results) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return listings


def find_listing(listings, search_kw):
    """Return the first listing whose title matches all keywords (case-insensitive)."""
    kw_lower = [k.lower() for k in search_kw]
    for listing in listings:
        title_lower = listing.get("title", "").lower()
        if all(k in title_lower for k in kw_lower):
            return listing
    return None


def update_listing(token, listing_id, title, description, tags):
    """PATCH a listing with new title, description, and tags via form-encoded body."""
    payload = {
        "title": title[:140],
        "description": description,
    }
    # Build form body manually so tags are sent as repeated keys (tags[]=...)
    base_body = urllib.parse.urlencode(payload)
    tag_part = "&".join(
        "tags[]=" + urllib.parse.quote(t, safe="") for t in tags[:13]
    )
    form_body = base_body + "&" + tag_part

    r = requests.patch(
        f"{API}/shops/{SHOP_ID}/listings/{listing_id}",
        headers={
            **auth_headers(token),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=form_body,
        timeout=30,
    )
    return r


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    total = len(SEO_DATA)

    print(f"\n{'='*60}")
    print(f"  NasriTools - Update SEO  [title + description + tags]")
    print(f"  Products to update: {total}")
    print(f"{'='*60}\n")

    print("Fetching token...")
    token = get_token()

    print("Fetching active listings...")
    try:
        listings = fetch_active_listings(token)
    except requests.HTTPError as e:
        print(f"ERROR fetching listings: {e}")
        return

    print(f"Found {len(listings)} active listings.\n")

    ok = 0
    skipped = 0

    for i, item in enumerate(SEO_DATA, 1):
        kw        = item["search_kw"]
        new_title = item["title"]
        new_desc  = item["description"]
        new_tags  = item["tags"]

        kw_display = " + ".join(kw)
        print(f"[{i:02d}/{total}] Keywords: [{kw_display}]")

        listing = find_listing(listings, kw)
        if not listing:
            print(f"         SKIP — no listing found matching all keywords\n")
            skipped += 1
            continue

        lid   = listing["listing_id"]
        old_t = listing.get("title", "")[:60]
        print(f"         Matched listing {lid}: \"{old_t}...\"")
        print(f"         New title: \"{new_title[:60]}...\"")

        # Refresh token periodically
        if i % 5 == 0:
            token = get_token()

        r = update_listing(token, lid, new_title, new_desc, new_tags)
        time.sleep(1)

        if r.ok:
            ok += 1
            print(f"         OK — title, description & tags updated\n")
        else:
            print(f"         ERROR {r.status_code}: {r.text[:200]}\n")

    print(f"{'='*60}")
    print(f"  Done: {ok}/{total} updated  |  {skipped} skipped (not found)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
