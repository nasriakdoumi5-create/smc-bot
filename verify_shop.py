"""
NasriTools - Shop Verification
Checks:
  - All 100 listings are ACTIVE
  - All listings have 5 images
  - All listings have a digital file
  - All listings are assigned to a section
  - Shows summary of any problems

Run: python verify_shop.py
"""
import json, time, os, requests
from pathlib import Path
from collections import defaultdict

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"


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
    return t


def auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


def check_listing(token, slug, lid):
    issues = []

    # Get listing details
    r = requests.get(
        API + "/listings/" + str(lid),
        headers=auth(token),
        params={"includes": "images,files"},
    )
    if not r.ok:
        return [f"API error {r.status_code}: {r.text[:80]}"]

    data = r.json()
    state = data.get("state", "unknown")
    images = data.get("images", [])
    files  = data.get("files", [])
    section = data.get("shop_section_id")

    if state != "active":
        issues.append(f"state={state} (not active)")
    if len(images) < 5:
        issues.append(f"only {len(images)}/5 images")
    if len(files) == 0:
        issues.append("no digital file attached")
    if not section:
        issues.append("no section assigned")

    return issues


def main():
    print("\n" + "=" * 60)
    print("  NasriTools - Shop Verification")
    print("=" * 60 + "\n")

    published = json.loads(PUB_FILE.read_text()) if PUB_FILE.exists() else {}
    if not published:
        print("ERROR: ~/etsy_published.json is empty or missing.")
        return

    print(f"Checking {len(published)} listings...\n")
    token = get_token()

    ok_count = 0
    problems = {}

    slugs = list(published.items())
    for i, (slug, lid) in enumerate(slugs, 1):
        issues = check_listing(token, slug, lid)
        if issues:
            problems[slug] = issues
            print(f"  [{i:03d}] FAIL  {slug}: {', '.join(issues)}")
        else:
            ok_count += 1
            print(f"  [{i:03d}] OK    {slug}")
        time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"  Total   : {len(published)}")
    print(f"  OK      : {ok_count}")
    print(f"  Problems: {len(problems)}")
    print("=" * 60)

    if problems:
        print("\nIssues found:")
        for slug, issues in problems.items():
            print(f"  {slug}: {', '.join(issues)}")
        print("\nRun fix_missing.py to repair missing files/images.")
    else:
        print("\nAll listings are PERFECT. Shop is fully set up!")
        print("Next: Add logo and banner in Etsy dashboard.")
        print("URL: https://www.etsy.com/your/shops/me/tools/listings")


if __name__ == "__main__":
    main()
