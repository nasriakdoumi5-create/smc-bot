"""
build_starter.py
Builds the lead-magnet product: Starter Budget Tracker (€0.99).
Purpose: reviews + shop traffic, not profit.
Run:  python build_starter.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nasritools.factory import build_product

STARTER = {
    "slug": "starter_budget_tracker",
    "name": "Starter Budget Tracker",
    "subtitle": "Simple Monthly Budget Google Sheets Template",
    "price": "€0.99",
    "listing_title": "Budget Template Google Sheets | Simple Budget Tracker | Monthly Budget Spreadsheet | Easy Expense Tracker | Starter Finance Planner",
    "listing_emoji": "💰",
    "category": "Craft Supplies & Tools → Templates → Spreadsheets",
    "description_intro": "The easiest way to start budgeting — a clean, simple monthly budget that takes 5 minutes to set up. Perfect first step to control your money.",
    "accent_color": "F97316",
    "dark_color": "1A1A2E",
    "green_color": "22C55E",
    "yellow_color": "FBBF24",
    "red_color": "EF4444",
    "kpis_preview": ["Income", "Spent", "Left", "Rate"],
    "tabs": [
        {"name": "My Budget", "emoji": "🏠", "color": "1A1A2E", "type": "dashboard",
         "description": "One clean page: income, spending, and what's left.",
         "kpis": [
             {"label": "Income",   "formula": "=SUM(Income!B:B)"},
             {"label": "Spent",    "formula": "=SUM(Spending!C:C)"},
             {"label": "Left",     "formula": "=B4-C4"},
             {"label": "Rate",     "formula": '=TEXT(D4/B4,"0%")'},
         ]},
        {"name": "Income", "emoji": "💵", "color": "22C55E", "type": "table",
         "description": "Log your income — salary, side hustle, anything.",
         "columns": [
             {"name": "Date",   "width": 14, "sample": "2026-07-01"},
             {"name": "Amount", "width": 14, "sample": "2200"},
             {"name": "Source", "width": 22, "dropdown": ["Salary","Freelance","Side Hustle","Gift","Other"]},
             {"name": "Notes",  "width": 26, "sample": "Monthly salary"},
         ], "sample_rows": 5},
        {"name": "Spending", "emoji": "💳", "color": "EF4444", "type": "table",
         "description": "Every expense in one place, categorized automatically.",
         "columns": [
             {"name": "Date",     "width": 14, "sample": "2026-07-03"},
             {"name": "Item",     "width": 22, "sample": "Groceries"},
             {"name": "Amount",   "width": 14, "sample": "65"},
             {"name": "Category", "width": 18, "dropdown": ["Housing","Food","Transport","Fun","Health","Other"]},
             {"name": "Notes",    "width": 22, "sample": "Weekly shop"},
         ], "sample_rows": 8},
    ],
    "features": [
        "5-minute setup — no learning curve",
        "Auto-calculating: income, spending, what's left",
        "Simple category dropdowns",
        "Works on phone, tablet & desktop",
        "No subscription — yours forever",
        "Free Google account is all you need",
    ],
    "tags": ["budget template", "budget tracker", "google sheets budget",
             "monthly budget", "expense tracker", "simple budget",
             "budget spreadsheet", "finance tracker", "money tracker",
             "budget planner", "spending tracker", "beginner budget",
             "easy budget"],
}

if __name__ == "__main__":
    result = build_product(STARTER)
    print("\nBuild result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
