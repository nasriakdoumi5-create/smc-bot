"""
fix_title_mobile.py
Ensures the most important keyword appears in the first 40 characters of every title.
Etsy mobile shows only ~40 chars — front-loading keywords boosts rankings.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

# Map: keyword to find in title → short label to put at start
KEYWORD_MAP = [
    (["budget tracker", "budget & expense", "monthly budget"],     "Budget Tracker"),
    (["invoice tracker", "invoice & client", "freelancer invoice"], "Invoice Tracker"),
    (["workout tracker", "gym tracker"],                            "Workout Tracker"),
    (["meal planner", "meal plan"],                                 "Meal Planner"),
    (["habit tracker", "habit builder", "30-day habit"],           "Habit Tracker"),
    (["weekly planner", "weekly productivity"],                     "Weekly Planner"),
    (["student planner", "student academic"],                       "Student Planner"),
    (["goals planner", "90-day", "goal planner"],                  "Goals Planner"),
    (["content creator"],                                           "Content Creator"),
    (["wedding planner"],                                           "Wedding Planner"),
    (["profit loss", "profit & loss"],                             "Profit Loss Tracker"),
    (["cash flow"],                                                 "Cash Flow Tracker"),
    (["kpi dashboard"],                                             "KPI Dashboard"),
    (["social media"],                                              "Social Media Planner"),
    (["project management"],                                        "Project Tracker"),
    (["debt payoff"],                                               "Debt Payoff Planner"),
    (["startup financial"],                                         "Startup Finance"),
    (["travel planner"],                                            "Travel Planner"),
    (["event planner"],                                             "Event Planner"),
    (["keto diet"],                                                 "Keto Tracker"),
    (["sleep tracker"],                                             "Sleep Tracker"),
    (["weight loss"],                                               "Weight Loss Tracker"),
    (["stock trading"],                                             "Stock Trading Journal"),
    (["options trading"],                                           "Options Tracker"),
    (["real estate"],                                               "Real Estate Tracker"),
    (["dropshipping"],                                              "Dropshipping Tracker"),
    (["restaurant"],                                                "Restaurant Tracker"),
    (["hair salon"],                                                "Salon Tracker"),
    (["law firm"],                                                   "Law Firm Billing"),
    (["marketing roi"],                                             "Marketing ROI"),
    (["employee performance"],                                      "HR Tracker"),
    (["inventory"],                                                 "Inventory Tracker"),
    (["job application"],                                           "Job Application"),
    (["youtube"],                                                   "YouTube Tracker"),
    (["time tracking", "timesheet"],                               "Time Tracker"),
    (["marathon"],                                                  "Marathon Planner"),
    (["pregnancy"],                                                 "Pregnancy Tracker"),
    (["mental health"],                                             "Mental Health Journal"),
    (["nonprofit"],                                                 "Nonprofit Budget"),
    (["church budget"],                                             "Church Budget"),
    (["emergency fund"],                                            "Emergency Fund"),
    (["etsy shop tracker"],                                         "Etsy Shop Tracker"),
    (["print on demand"],                                           "POD Tracker"),
    (["virtual assistant"],                                         "VA Tracker"),
    (["influencer"],                                                "Influencer Tracker"),
    (["musician"],                                                  "Musician Tracker"),
    (["artist commission"],                                         "Artist Tracker"),
    (["author book"],                                               "Author Tracker"),
    (["tutor"],                                                     "Tutor Tracker"),
    (["online course"],                                             "Course Planner"),
    (["certification"],                                             "Certification Tracker"),
    (["skill development"],                                         "Skill Planner"),
    (["family chores"],                                             "Family Planner"),
    (["car maintenance"],                                           "Car Tracker"),
    (["school supply"],                                             "School Budget"),
    (["thesis"],                                                    "Thesis Planner"),
    (["pet expense"],                                               "Pet Budget"),
    (["annual review"],                                             "Annual Review"),
    (["supply chain"],                                              "Supply Chain"),
    (["construction"],                                              "Construction Tracker"),
    (["ecommerce"],                                                 "Ecommerce Tracker"),
    (["content repurpos"],                                          "Content Tracker"),
    (["hr onboarding"],                                             "HR Onboarding"),
    (["sales commission"],                                          "Sales Tracker"),
    (["bundle"],                                                    None),  # skip bundles
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
    return {"Authorization": "Bearer " + token["access_token"], "x-api-key": CLIENT_ID + ":" + SECRET}

def get_all_listings(token):
    listings = []
    offset = 0
    while True:
        r = requests.get(f"{API}/shops/{SHOP_ID}/listings/active",
                         headers=auth_headers(token), params={"limit": 100, "offset": offset})
        if not r.ok: break
        results = r.json().get("results", [])
        listings.extend(results)
        if len(results) < 100: break
        offset += 100
    return listings

def update_title(token, lid, title):
    r = requests.patch(f"{API}/shops/{SHOP_ID}/listings/{lid}",
                       headers={**auth_headers(token), "Content-Type": "application/x-www-form-urlencoded"},
                       data=urllib.parse.urlencode({"title": title[:140]}), timeout=30)
    return r.ok, r.status_code

def get_label(title_lower):
    for kws, label in KEYWORD_MAP:
        for kw in kws:
            if kw in title_lower:
                return label
    return None

def main():
    print("=" * 65)
    print("  NasriTools — Fix Title Mobile (First 40 Chars)")
    print("=" * 65)
    token = get_token()
    listings = get_all_listings(token)
    print(f"[*] Found {len(listings)} listings\n")

    ok = skip = fail = 0

    for l in listings:
        lid = l["listing_id"]
        title = l["title"]
        title_lower = title.lower()

        label = get_label(title_lower)
        if label is None:
            print(f"  [SKIP] {title[:50]}")
            skip += 1
            continue

        # Check if label already at start
        if title_lower.startswith(label.lower()):
            print(f"  [OK]   {title[:50]}")
            skip += 1
            continue

        # Remove existing label from title if it appears later, then prepend
        new_title = label + " | " + title
        if len(new_title) > 140:
            new_title = new_title[:140]

        print(f"  [FIX]  {title[:35]} → {new_title[:45]}...", end=" ", flush=True)
        token = get_token()
        r_ok, code = update_title(token, lid, new_title)
        if r_ok:
            print(f"OK")
            ok += 1
        else:
            print(f"FAIL ({code})")
            fail += 1
        time.sleep(0.8)

    print(f"\n{'='*65}")
    print(f"  Fixed: {ok} | Skipped/OK: {skip} | Failed: {fail}")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
