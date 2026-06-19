"""
NasriTools - Off-Niche Deactivator v2
Precisely deactivates listings that don't belong to the 5 core systems.
Run: python deactivate_offniche_v2.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

# Listings that MUST stay active — never deactivate these
CORE_KEEP_KEYWORDS = [
    ["budget", "tracker"],
    ["habit", "tracker"],
    ["meal", "planner"],
    ["wedding", "planner"],
    ["workout", "tracker"],
    ["content", "creator"],
    ["invoice", "tracker"],
    ["student", "planner"],
    ["goals", "planner"],
    ["weekly", "planner"],
    ["finance", "bundle"],
    ["health", "bundle"],
    ["planner", "bundle"],
    ["business", "bundle"],
    ["ultimate", "bundle"],
    ["free", "budget"],    # Free lead magnet
]

# Keywords that signal an off-niche listing to deactivate
OFFNICHE_KEYWORDS = [
    "restaurant",
    "nonprofit",
    "non-profit",
    "startup financial",
    "kpi dashboard",
    "content repurposing",
    "social media posting calendar",
    "social media calendar",  # standalone (not content creator planner)
    "church",
    "real estate",
    "construction",
    "rental property",
    "dropshipping",
    "amazon fba",
    "crypto",
    "nft",
    "e-commerce tracker",
    "ecommerce tracker",
    "inventory",
    "hr tracker",
    "employee",
    "payroll",
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


def is_core(title_lower):
    for kw_set in CORE_KEEP_KEYWORDS:
        if all(kw in title_lower for kw in kw_set):
            return True
    return False


def is_offniche(title_lower):
    for kw in OFFNICHE_KEYWORDS:
        if kw in title_lower:
            # Extra check: "social media calendar" is off-niche
            # but "content creator" + "social media" is fine (it's our product)
            if kw == "social media posting calendar" and "content creator" in title_lower:
                continue
            if kw == "social media calendar" and "content creator" in title_lower:
                continue
            return True
    return False


def deactivate(token, listing_id):
    r = requests.patch(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}",
        headers={**auth_headers(token), "Content-Type": "application/json"},
        json={"state": "inactive"},
        timeout=30,
    )
    return r.ok


def main():
    token = get_token()

    print(f"\n{'='*65}")
    print(f"  NasriTools - Off-Niche Deactivator v2")
    print(f"{'='*65}\n")

    print("  Fetching active listings…")
    listings = fetch_all_listings(token)
    token = get_token()
    print(f"  Found {len(listings)} active listings\n")

    keep = []
    to_deactivate = []
    uncertain = []

    for lst in listings:
        lid   = lst["listing_id"]
        title = (lst.get("title") or "")
        tl    = title.lower()

        if is_core(tl):
            keep.append((lid, title))
        elif is_offniche(tl):
            to_deactivate.append((lid, title))
        else:
            uncertain.append((lid, title))

    print(f"  Core listings (protected):  {len(keep)}")
    print(f"  Off-niche (to deactivate):  {len(to_deactivate)}")
    print(f"  Uncertain (keeping active): {len(uncertain)}\n")

    if uncertain:
        print("  ── Uncertain (keeping, review manually) ──")
        for lid, t in uncertain:
            print(f"    [{lid}] {t[:65]}")
        print()

    if not to_deactivate:
        print("  Nothing to deactivate — store is clean.")
        print(f"\n{'='*65}\n")
        return

    print(f"  ── Deactivating {len(to_deactivate)} off-niche listings ──")
    ok = 0
    for lid, title in to_deactivate:
        print(f"  Deactivating: {title[:60]}…", end=" ")
        success = deactivate(token, lid)
        print("✓" if success else "✗")
        if success:
            ok += 1
        time.sleep(0.8)
        token = get_token()

    print(f"\n  Deactivated: {ok}/{len(to_deactivate)}")
    print(f"\n{'='*65}")
    print(f"  Done. Store cleaned.")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
