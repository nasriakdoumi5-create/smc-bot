"""
NasriTools - Activate Bundle Drafts
Activates the 4 bundle listings that were created as drafts.
Run: python activate_bundles.py
"""
import json, os, time, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_missing_bundles.json"

# Fallback IDs if done file not found
FALLBACK_IDS = {
    "health_bundle":   4524724720,
    "planner_bundle":  4524724758,
    "business_bundle": 4524724798,
    "ultimate_bundle": 4524724846,
}


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


def main():
    done  = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else FALLBACK_IDS
    token = get_token()

    bundle_ids = {k: v for k, v in done.items() if k in FALLBACK_IDS}
    if not bundle_ids:
        bundle_ids = FALLBACK_IDS

    print(f"\n{'='*60}")
    print(f"  NasriTools - Activate Bundle Drafts")
    print(f"{'='*60}\n")

    ok = 0
    for key, lid in bundle_ids.items():
        print(f"  Activating [{lid}] {key}…", end=" ")
        token = get_token()

        # First check current state
        check = requests.get(
            f"https://api.etsy.com/v3/application/listings/{lid}",
            headers=auth_headers(token), timeout=15,
        )
        if check.ok:
            state = check.json().get("state", "unknown")
            if state == "active":
                print(f"already active ✓")
                ok += 1
                continue
            print(f"(state={state})", end=" ")

        r = requests.patch(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/listings/{lid}",
            headers={**auth_headers(token), "Content-Type": "application/json"},
            json={"state": "active"},
            timeout=30,
        )

        if r.ok:
            print("✓")
            ok += 1
        else:
            print(f"✗  {r.status_code}: {r.text[:200]}")

        time.sleep(1)

    print(f"\n  Activated: {ok}/{len(bundle_ids)}")
    print(f"\n  Bundle URLs:")
    for key, lid in bundle_ids.items():
        print(f"    https://www.etsy.com/listing/{lid}  ({key})")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
