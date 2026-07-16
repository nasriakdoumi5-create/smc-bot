"""
fix_remaining.py  (run on YOUR PC)
Fixes the 12 remaining listings:
  • bundles: replaces the .txt/.zip with a REAL zip of v2 templates
  • free budget listings: uploads the quality starter template
  • Freelance/Restaurant managers: uploads rebuilt premium workbooks
  • sets the new hero image on every one of them (+ the starter listing)
Run:  python fix_remaining.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
ROOT       = Path(__file__).parent
OUT        = ROOT / "output"
FIX        = OUT / "_fix"

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ZIP_MIME  = "application/zip"

STARTER_XLSX = OUT / "starter_budget_tracker" / "starter_budget_tracker.xlsx"

# listing_id → {files: [(path, upload_name, mime)], hero: path}
FIXES = {
    4524724846: {"files": [(FIX/"complete_life_system"/"NasriTools_Complete_Life_System_10_Templates.zip", None, ZIP_MIME)],
                 "hero": FIX/"complete_life_system"/"hero.jpg"},
    4525136892: {"files": [(FIX/"finance_os"/"NasriTools_Complete_Finance_OS.zip", None, ZIP_MIME)],
                 "hero": FIX/"finance_os"/"hero.jpg"},
    4525136928: {"files": [(FIX/"health_os"/"NasriTools_Complete_Health_OS.zip", None, ZIP_MIME)],
                 "hero": FIX/"health_os"/"hero.jpg"},
    4524724798: {"files": [(FIX/"business_bundle"/"NasriTools_Business_Bundle.zip", None, ZIP_MIME)],
                 "hero": FIX/"business_bundle"/"hero.jpg"},
    4524724758: {"files": [(FIX/"planner_bundle"/"NasriTools_Productivity_Planner_Bundle.zip", None, ZIP_MIME)],
                 "hero": FIX/"planner_bundle"/"hero.jpg"},
    4524724720: {"files": [(FIX/"health_bundle"/"NasriTools_Health_Meal_Bundle.zip", None, ZIP_MIME)],
                 "hero": FIX/"health_bundle"/"hero.jpg"},
    4524283886: {"files": [(FIX/"ultimate_bundle"/"NasriTools_Ultimate_Bundle_10_Templates.zip", None, ZIP_MIME)],
                 "hero": FIX/"ultimate_bundle"/"hero.jpg"},
    # free budget listings — quality starter file under their original names
    4523968643: {"files": [(STARTER_XLSX, "free_budget_tracker.xlsx", XLSX_MIME)],
                 "hero": FIX/"free_budget"/"hero.jpg"},
    4524681057: {"files": [(STARTER_XLSX, "NasriTools_Budget_Tracker_FREE.xlsx", XLSX_MIME)],
                 "hero": FIX/"free_budget"/"hero.jpg"},
    4526750401: {"files": [(STARTER_XLSX, "Budget_Tracker_FREE_NasriTools.xlsx", XLSX_MIME)],
                 "hero": FIX/"free_budget"/"hero.jpg"},
    # premium managers — rebuilt workbooks
    4522499954: {"files": [(OUT/"Freelance_Business_Manager"/"Freelance_Business_Manager.xlsx", None, XLSX_MIME)],
                 "hero": FIX/"Freelance_Business_Manager"/"hero.jpg"},
    4522305528: {"files": [(OUT/"Restaurant_Cafe_Manager"/"Restaurant_Cafe_Manager.xlsx", None, XLSX_MIME)],
                 "hero": FIX/"Restaurant_Cafe_Manager"/"hero.jpg"},
    # starter listing — hero refresh only
    4538866889: {"files": [], "hero": OUT/"starter_budget_tracker"/"starter_budget_tracker_01_hero.jpg"},
}

DONE_FILE = ROOT / "fix_done.json"

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

def main():
    print("=" * 62)
    print("  NasriTools — Fix the 12 remaining listings")
    print("=" * 62)

    done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
    total = len(FIXES)

    for idx, (lid, fix) in enumerate(FIXES.items(), 1):
        if str(lid) in done:
            print(f"  [{idx:2}/{total}] SKIP (done) {lid}")
            continue

        print(f"  [{idx:2}/{total}] listing {lid}")
        token = get_token()

        # 1. replace files (if any)
        if fix["files"]:
            r = requests.get(f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
                             headers=auth_headers(token), timeout=30)
            if not r.ok:
                print(f"       ✗ list files {r.status_code}")
                continue
            old = r.json().get("results", [])
            for f in old:
                rd = requests.delete(
                    f"{API}/shops/{SHOP_ID}/listings/{lid}/files/{f['listing_file_id']}",
                    headers=auth_headers(token), timeout=30)
                print(f"       {'✓ deleted' if rd.ok else '✗ delete'} {f.get('filename')}")
                time.sleep(0.4)

            ok_all = True
            for rank, (path, name, mime) in enumerate(fix["files"], 1):
                upload_name = name or path.name
                with open(path, "rb") as fh:
                    ru = requests.post(
                        f"{API}/shops/{SHOP_ID}/listings/{lid}/files",
                        headers=auth_headers(token),
                        files={"file": (upload_name, fh, mime)},
                        data={"name": upload_name, "rank": rank},
                        timeout=180,
                    )
                print(f"       {'✓ uploaded' if ru.ok else '✗ upload'} {upload_name}"
                      + ("" if ru.ok else f" ({ru.status_code}: {ru.text[:90]})"))
                ok_all = ok_all and ru.ok
                time.sleep(0.5)
            if not ok_all:
                continue

        # 2. hero image
        hero = fix["hero"]
        if hero and hero.exists():
            with open(hero, "rb") as fh:
                ri = requests.post(
                    f"{API}/shops/{SHOP_ID}/listings/{lid}/images",
                    headers=auth_headers(token),
                    files={"image": (hero.name, fh, "image/jpeg")},
                    data={"rank": 1, "overwrite": "true"},
                    timeout=120,
                )
            print(f"       {'✓ hero set' if ri.ok else '✗ hero'}"
                  + ("" if ri.ok else f" ({ri.status_code})"))
            if not ri.ok:
                continue

        done[str(lid)] = True
        DONE_FILE.write_text(json.dumps(done, indent=2))
        time.sleep(0.6)

    print(f"\n{'=' * 62}")
    print(f"  Completed: {len(done)}/{total}")
    print(f"{'=' * 62}")
    if len(done) < total:
        print("  Re-run to retry the failed ones — progress is saved.")

if __name__ == "__main__":
    main()
