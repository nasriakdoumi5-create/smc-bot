"""
NasriTools - Generate Bundle Delivery Files
Creates a .txt file for each bundle that buyers receive after purchase
User fills in their Google Sheets links, then uploads each file to Etsy
Run: python make_bundle_files.py
"""
from pathlib import Path
import os

OUT_DIR = Path(os.path.expanduser("~")) / "nasri_bundle_files"
OUT_DIR.mkdir(exist_ok=True)

BUNDLES = [
    {
        "filename": "finance_bundle_delivery.txt",
        "name": "Finance Bundle",
        "templates": [
            ("Budget Tracker",             "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Freelancer Invoice Tracker", "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Goals Planner",              "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
        ],
    },
    {
        "filename": "health_bundle_delivery.txt",
        "name": "Health Bundle",
        "templates": [
            ("Workout Tracker", "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Meal Planner",    "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Habit Tracker",   "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
        ],
    },
    {
        "filename": "planner_bundle_delivery.txt",
        "name": "Planner Bundle",
        "templates": [
            ("Weekly Planner",  "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Student Planner", "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Goals Planner",   "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
        ],
    },
    {
        "filename": "business_bundle_delivery.txt",
        "name": "Business Bundle",
        "templates": [
            ("Content Creator Planner",    "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Freelancer Invoice Tracker", "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("KPI Dashboard",              "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
        ],
    },
    {
        "filename": "ultimate_bundle_delivery.txt",
        "name": "Ultimate Bundle (All 10 Templates)",
        "templates": [
            ("Budget Tracker",             "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Habit Tracker",              "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Meal Planner",               "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Wedding Planner",            "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Workout Tracker",            "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Content Creator Planner",    "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Freelancer Invoice Tracker", "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Student Planner",            "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Goals Planner",              "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
            ("Weekly Planner",             "PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE"),
        ],
    },
]

TEMPLATE = """\
================================================================
  NasriTools — {name}
  Thank you for your purchase!
================================================================

Your Google Sheets templates are ready to use instantly.

HOW TO ACCESS YOUR TEMPLATES:
  1. Click each link below
  2. Click File → Make a copy
  3. Save it to your Google Drive
  4. Start using it immediately!

----------------------------------------------------------------
  YOUR TEMPLATES:
----------------------------------------------------------------

{template_list}
----------------------------------------------------------------

NEED HELP?
  Message us on Etsy — we reply within 24 hours.
  Or visit: nasritools.etsy.com

IMPORTANT:
  • These templates work on Google Sheets (free) and Excel
  • Make a copy before editing — do not request edit access
  • You have lifetime access to your templates

================================================================
  Thank you for supporting NasriTools!
  Please leave a review — it means the world to us ♥
================================================================
"""


def main():
    print(f"\n{'='*55}")
    print(f"  NasriTools - Bundle Delivery File Generator")
    print(f"  Output: {OUT_DIR}")
    print(f"{'='*55}\n")

    for bundle in BUNDLES:
        lines = []
        for i, (name, link) in enumerate(bundle["templates"], 1):
            lines.append(f"  {i}. {name}")
            lines.append(f"     Link: {link}")
            lines.append("")

        content = TEMPLATE.format(
            name=bundle["name"],
            template_list="\n".join(lines),
        )

        out = OUT_DIR / bundle["filename"]
        out.write_text(content, encoding="utf-8")
        print(f"  Created: {bundle['filename']}")

    print(f"\n{'='*55}")
    print(f"  Done! 5 delivery files created in:")
    print(f"  {OUT_DIR}")
    print(f"\n  NEXT STEP:")
    print(f"  Open each .txt file and replace")
    print(f"  PASTE_YOUR_GOOGLE_SHEETS_LINK_HERE")
    print(f"  with the real links from your Google Drive")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
