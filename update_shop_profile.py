#!/usr/bin/env python3
"""
Update NasriTools Etsy shop profile:
- announcement (shown on shop homepage)
- sale_message (auto-sent to buyers after purchase)
"""

import json
import os
import sys
import requests
from pathlib import Path

SHOP_ID = 66526082
CLIENT_ID = "pluc0garrgcjzhim0hawxf0k"
CLIENT_SECRET = "hc89hlqkd6"
TOKEN_FILE = Path.home() / "etsy_token.json"

ANNOUNCEMENT = """\
🎉 Welcome to NasriTools — Google Sheets Templates that actually work!
✅ Instant download • Works on Google Sheets (free) + Excel • Lifetime access
📦 Bundle deals available — save up to 65%!
📩 Questions? Message us — we reply within 24 hours."""

SALE_MESSAGE = """\
Thank you for your purchase! 🎉

Your template is ready to download — go to Etsy → Purchases & Reviews → find this order → click Download.

HOW TO USE:
1. Open the file link
2. Click File → Make a copy
3. Save to your Google Drive — it's yours forever!

Works on Google Sheets (free) + Microsoft Excel.

If you need any help at all, just reply to this message — we respond within 24 hours.

Thank you for supporting NasriTools! ♥
Please leave a review if you enjoy the template — it means the world to us!

nasritools.etsy.com"""


def get_token() -> dict:
    """Load token from file."""
    if not TOKEN_FILE.exists():
        print(f"ERROR: Token file not found at {TOKEN_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(TOKEN_FILE) as f:
        return json.load(f)


def save_token(token: dict) -> None:
    """Save token back to file."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)


def refresh_token(token: dict) -> dict:
    """Refresh the access token using the refresh token."""
    print("Access token expired — refreshing...")
    resp = requests.post(
        "https://api.etsy.com/v3/public/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": token["refresh_token"],
        },
    )
    if resp.status_code != 200:
        print(f"ERROR: Failed to refresh token: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)
    new_token = resp.json()
    save_token(new_token)
    print("Token refreshed successfully.")
    return new_token


def auth_headers() -> dict:
    """Return Authorization headers, refreshing if necessary."""
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/json",
    }
    # Test with a lightweight call to check token validity
    test_resp = requests.get(
        f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}",
        headers=headers,
    )
    if test_resp.status_code == 401:
        token = refresh_token(token)
        headers["Authorization"] = f"Bearer {token['access_token']}"
    return headers


def update_shop_profile() -> None:
    """Update shop announcement and sale_message via PUT."""
    print("Fetching auth headers...")
    headers = auth_headers()

    url = f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}"
    payload = {
        "announcement": ANNOUNCEMENT,
        "sale_message": SALE_MESSAGE,
    }

    print(f"Sending PUT to {url} ...")
    resp = requests.put(url, headers=headers, json=payload)

    if resp.status_code == 200:
        data = resp.json()
        print("\nSUCCESS: Shop profile updated.")
        print(f"  Shop name  : {data.get('shop_name', 'N/A')}")
        print(f"  Announcement length : {len(data.get('announcement', ''))} chars")
        print(f"  Sale message length : {len(data.get('sale_message', ''))} chars")
    else:
        print(f"\nERROR: {resp.status_code} {resp.reason}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    update_shop_profile()
