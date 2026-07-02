"""
upload_shop_assets.py

Uploads shop logo, banner, and About section text via Etsy API.
Run: python upload_shop_assets.py
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"

LOGO_PATH   = Path("thumbnails/brand/shop_logo_1000x1000.png")
BANNER_PATH = Path("thumbnails/brand/shop_banner_1600x400.png")

ABOUT_TEXT = """\
We built NasriTools because we were tired of paying monthly subscriptions \
for tools that should be simple.

Google Sheets is free. Your data stays yours. It works on every device. \
So we built 119 professional templates on top of it — for budgeting, \
business tracking, fitness, invoicing, and productivity.

Every template is designed to work immediately: no setup, no account, \
no learning curve. Download, open, and start using in under 2 minutes.

WHO WE HELP:
• Freelancers who need simple invoicing without expensive software
• Families tracking monthly budgets and saving more
• Fitness enthusiasts logging workouts and measuring progress
• Business owners who want clear KPI dashboards without complexity
• Students and professionals who want to plan their weeks better

WHY GOOGLE SHEETS:
Free for everyone, forever. Works on phone, tablet, and desktop. \
Auto-saves to your Drive. Easy to share. Fully customizable.

We answer every message within 24 hours. \
If you need a modification, just ask.

nasritools.etsy.com — built for people who get things done.\
"""


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"]})
        r.raise_for_status(); t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def auth_headers(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}


def upload_logo(token):
    print("\n[1] Uploading shop logo...", end=" ", flush=True)
    if not LOGO_PATH.exists():
        print(f"SKIP — file not found: {LOGO_PATH}")
        print(f"     Run setup_shop_complete.py first to generate assets.")
        return False

    with open(LOGO_PATH, "rb") as f:
        r = requests.put(
            f"{API}/shops/{SHOP_ID}/icon",
            headers=auth_headers(token),
            files={"image": ("shop_logo.png", f, "image/png")},
            timeout=60)

    if r.ok:
        print("✅ Logo uploaded!")
        return True
    else:
        print(f"✗ ({r.status_code}): {r.text[:120]}")
        # Try POST if PUT fails
        with open(LOGO_PATH, "rb") as f:
            r2 = requests.post(
                f"{API}/shops/{SHOP_ID}/icon",
                headers=auth_headers(token),
                files={"image": ("shop_logo.png", f, "image/png")},
                timeout=60)
        if r2.ok:
            print("  ✅ Logo uploaded (POST retry)!")
            return True
        print(f"  ✗ Retry failed ({r2.status_code}): {r2.text[:100]}")
        print(f"  → Manual: Shop Manager → Info & Appearance → Shop Icon")
        print(f"  → File: {LOGO_PATH.resolve()}")
        return False


def upload_banner(token):
    print("\n[2] Uploading shop banner...", end=" ", flush=True)
    if not BANNER_PATH.exists():
        print(f"SKIP — file not found: {BANNER_PATH}")
        print(f"     Run setup_shop_complete.py first to generate assets.")
        return False

    with open(BANNER_PATH, "rb") as f:
        r = requests.post(
            f"{API}/shops/{SHOP_ID}/banner",
            headers=auth_headers(token),
            files={"image": ("shop_banner.png", f, "image/png")},
            timeout=60)

    if r.ok:
        print("✅ Banner uploaded!")
        return True
    else:
        print(f"✗ ({r.status_code}): {r.text[:120]}")
        # Try PUT
        with open(BANNER_PATH, "rb") as f:
            r2 = requests.put(
                f"{API}/shops/{SHOP_ID}/banner",
                headers=auth_headers(token),
                files={"image": ("shop_banner.png", f, "image/png")},
                timeout=60)
        if r2.ok:
            print("  ✅ Banner uploaded (PUT retry)!")
            return True
        print(f"  ✗ Retry failed ({r2.status_code}): {r2.text[:100]}")
        print(f"  → Manual: Shop Manager → Info & Appearance → Shop Banner")
        print(f"  → File: {BANNER_PATH.resolve()}")
        return False


def update_about(token):
    print("\n[3] Updating About/Story section...", end=" ", flush=True)

    # Try multiple field names Etsy might use
    field_attempts = [
        ("about_us",   ABOUT_TEXT),
        ("story",      ABOUT_TEXT),
        ("announcement", None),   # skip announcement, already done
    ]

    for field, value in field_attempts:
        if value is None:
            continue
        r = requests.patch(
            f"{API}/shops/{SHOP_ID}",
            headers={**auth_headers(token),
                     "Content-Type": "application/x-www-form-urlencoded"},
            data=f"{field}={urllib.parse.quote(value, safe='')}",
            timeout=30)
        if r.ok:
            print(f"✅ About section updated (field: '{field}')!")
            return True
        print(f"\n  '{field}' → {r.status_code}", end=" ", flush=True)
        time.sleep(0.5)

    print(f"\n  ✗ API doesn't support About section update.")
    print(f"  → Manual: Shop Manager → Info & Appearance → Story")
    print(f"  → Copy text from: about_section.txt")
    return False


def create_coupon(token):
    print("\n[4] Creating FRIENDS100 coupon (100% off)...", end=" ", flush=True)

    # Try form-encoded
    r = requests.post(
        f"{API}/shops/{SHOP_ID}/coupon",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data="coupon_code=FRIENDS100&pct_discount=100&seller_active=true",
        timeout=30)

    if r.ok:
        print("✅ Coupon created!")
        return True

    # Try alternate endpoint
    r2 = requests.post(
        f"{API}/shops/{SHOP_ID}/discount_codes",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data="coupon_code=FRIENDS100&pct_discount=100&seller_active=true",
        timeout=30)

    if r2.ok:
        print("✅ Coupon created!")
        return True

    print(f"✗ API coupon creation not available for new shops.")
    print(f"  → Manual: Shop Manager → Marketing → Sales & Coupons")
    print(f"  → Create coupon: FRIENDS100 | 100% off | Active")
    return False


def main():
    print("=" * 60)
    print("  NasriTools — Upload Shop Assets")
    print("=" * 60)

    token = get_token()

    logo_ok   = upload_logo(token)
    token = get_token()
    banner_ok = upload_banner(token)
    token = get_token()
    about_ok  = update_about(token)
    token = get_token()
    coupon_ok = create_coupon(token)

    print(f"\n{'='*60}")
    print("  RESULTS:")
    print(f"  {'✅' if logo_ok   else '❌'}  Logo")
    print(f"  {'✅' if banner_ok else '❌'}  Banner")
    print(f"  {'✅' if about_ok  else '❌'}  About Section")
    print(f"  {'✅' if coupon_ok else '❌'}  Coupon FRIENDS100")

    manual = []
    if not logo_ok:   manual.append("Logo  → thumbnails\\brand\\shop_logo_1000x1000.png")
    if not banner_ok: manual.append("Banner → thumbnails\\brand\\shop_banner_1600x400.png")
    if not about_ok:  manual.append("About  → copy from about_section.txt")
    if not coupon_ok: manual.append("Coupon → Marketing → Sales & Coupons → FRIENDS100 (100% off)")

    if manual:
        print(f"\n  MANUAL TASKS REMAINING:")
        for m in manual:
            print(f"    • {m}")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
