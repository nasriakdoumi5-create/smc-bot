"""
create_coupon.py
Creates a 100% discount coupon on Etsy for sending to friends/family
to get the first reviews.
"""
import json, os, time, requests, urllib.parse
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

COUPON_CODE    = "FRIENDS100"
PCT_DISCOUNT   = 100
FREE_SHIPPING  = False


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
    token = get_token()
    print(f"\nCreating coupon: {COUPON_CODE} ({PCT_DISCOUNT}% off)")

    # Try form-encoded first (required by some Etsy endpoints)
    payload = (
        f"coupon_code={urllib.parse.quote(COUPON_CODE, safe='')}"
        f"&pct_discount={PCT_DISCOUNT}"
        f"&seller_active=true"
        f"&free_shipping={'true' if FREE_SHIPPING else 'false'}"
    )
    r = requests.post(
        f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/discount_codes",
        headers={**auth_headers(token),
                 "Content-Type": "application/x-www-form-urlencoded"},
        data=payload,
        timeout=30,
    )
    # Fallback to JSON if form-encoding fails
    if not r.ok and r.status_code in (400, 415, 422):
        r = requests.post(
            f"https://api.etsy.com/v3/application/shops/{SHOP_ID}/discount_codes",
            headers={**auth_headers(token), "Content-Type": "application/json"},
            json={"coupon_code": COUPON_CODE, "pct_discount": PCT_DISCOUNT,
                  "seller_active": True, "free_shipping": FREE_SHIPPING},
            timeout=30,
        )

    if r.ok:
        data = r.json()
        print(f"\n✓ Coupon created successfully!")
        print(f"  Code:     {data.get('coupon_code', COUPON_CODE)}")
        print(f"  Discount: {PCT_DISCOUNT}%")
        print(f"\nShare this link with friends:")
        print(f"  https://www.etsy.com/shop/nasritools?coupon={COUPON_CODE}")
        print(f"\nMessage to send:")
        print(f"  Hey! Use code {COUPON_CODE} to get my template for FREE.")
        print(f"  Link: https://nasritools.etsy.com")
        print(f"  All I ask is an honest review after you use it :)")
    else:
        print(f"\n✗ Failed (HTTP {r.status_code}): {r.text[:400]}")
        if r.status_code == 409:
            print(f"\n  Code '{COUPON_CODE}' already exists — you can use it directly.")
            print(f"  https://www.etsy.com/shop/nasritools?coupon={COUPON_CODE}")


if __name__ == "__main__":
    main()
