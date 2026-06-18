#!/usr/bin/env python3
"""
Append a FAQ section to all active NasriTools Etsy listings.

- Fetches ALL active listings via pagination (limit=100)
- Skips listings that already contain "FREQUENTLY ASKED QUESTIONS"
- Tracks completed listings in ~/etsy_faq_done.json
- Sleeps 0.8s between updates to respect rate limits
"""

import json
import sys
import time
import requests
from pathlib import Path

SHOP_ID = 66526082
CLIENT_ID = "pluc0garrgcjzhim0hawxf0k"
CLIENT_SECRET = "hc89hlqkd6"
TOKEN_FILE = Path.home() / "etsy_token.json"
DONE_FILE = Path.home() / "etsy_faq_done.json"

FAQ_SECTION = """\
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ FREQUENTLY ASKED QUESTIONS

Q: How do I access my template after purchase?
A: You'll receive a download link instantly in your Etsy account (Purchases & Reviews). Click the file to download, then open with Google Sheets or Excel.

Q: Do I need a Google account?
A: A free Google account lets you use Google Sheets online. You can also open the file with Microsoft Excel — no subscription needed.

Q: Can I edit the template?
A: Yes! Click File → Make a copy in Google Sheets to get your own editable version. Do not request edit access to the original.

Q: Does it work on mobile?
A: Yes! Google Sheets has free iOS and Android apps — use it anywhere.

Q: Can I use it for multiple projects?
A: Absolutely — once you make a copy, it's yours forever with lifetime access.

Q: What if I need help?
A: Message us on Etsy — we reply within 24 hours, 7 days a week.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

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


# Module-level cache so we only refresh once per run
_cached_headers: dict | None = None


def auth_headers(force_refresh: bool = False) -> dict:
    """Return Authorization headers, auto-refreshing if a 401 is detected."""
    global _cached_headers
    if _cached_headers is not None and not force_refresh:
        return _cached_headers

    token = get_token()
    headers = {
        "Authorization": f"Bearer {token['access_token']}",
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/json",
    }
    # Quick validity check
    test_resp = requests.get(
        f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}",
        headers=headers,
    )
    if test_resp.status_code == 401:
        token = refresh_token(token)
        headers["Authorization"] = f"Bearer {token['access_token']}"

    _cached_headers = headers
    return headers


# ---------------------------------------------------------------------------
# Done-file helpers
# ---------------------------------------------------------------------------

def load_done() -> set:
    """Load the set of already-processed listing IDs."""
    if not DONE_FILE.exists():
        return set()
    with open(DONE_FILE) as f:
        data = json.load(f)
    return set(data)


def save_done(done: set) -> None:
    """Persist the set of processed listing IDs."""
    with open(DONE_FILE, "w") as f:
        json.dump(sorted(done), f, indent=2)


# ---------------------------------------------------------------------------
# Etsy API helpers
# ---------------------------------------------------------------------------

def fetch_all_active_listings() -> list[dict]:
    """Paginate through all active listings and return them."""
    listings = []
    limit = 100
    offset = 0

    print("Fetching active listings...")
    while True:
        resp = requests.get(
            f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
            headers=auth_headers(),
            params={"limit": limit, "offset": offset},
        )
        if resp.status_code == 401:
            # Token expired mid-run — refresh and retry once
            auth_headers(force_refresh=True)
            resp = requests.get(
                f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/active",
                headers=auth_headers(),
                params={"limit": limit, "offset": offset},
            )
        if resp.status_code != 200:
            print(f"ERROR fetching listings at offset {offset}: {resp.status_code} {resp.text}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        results = data.get("results", [])
        listings.extend(results)
        print(f"  Fetched {len(listings)} / {data.get('count', '?')} listings...")

        if len(results) < limit:
            break
        offset += limit

    print(f"Total active listings: {len(listings)}\n")
    return listings


def update_listing_description(listing_id: int, new_description: str) -> bool:
    """PATCH a single listing's description. Returns True on success."""
    url = f"https://openapi.etsy.com/v3/application/shops/{SHOP_ID}/listings/{listing_id}"
    resp = requests.patch(
        url,
        headers=auth_headers(),
        json={"description": new_description},
    )
    if resp.status_code == 401:
        auth_headers(force_refresh=True)
        resp = requests.patch(
            url,
            headers=auth_headers(),
            json={"description": new_description},
        )
    return resp.status_code == 200, resp


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Validate auth up-front
    auth_headers()

    done = load_done()
    listings = fetch_all_active_listings()
    total = len(listings)

    updated = 0
    skipped_already_has_faq = 0
    skipped_done_file = 0
    errors = 0

    for idx, listing in enumerate(listings, start=1):
        listing_id = listing["listing_id"]
        title = listing.get("title", "")
        description = listing.get("description") or ""

        prefix = f"[{idx:03d}/{total:03d}] {title[:60]}"

        # Skip if already processed in a previous run
        if listing_id in done:
            print(f"{prefix} → skipped (done file)")
            skipped_done_file += 1
            continue

        # Skip if FAQ already present
        if "FREQUENTLY ASKED QUESTIONS" in description:
            print(f"{prefix} → skipped (FAQ already present)")
            done.add(listing_id)
            skipped_already_has_faq += 1
            save_done(done)
            continue

        # Build new description
        new_description = description + "\n\n" + FAQ_SECTION

        # Update listing
        success, resp = update_listing_description(listing_id, new_description)
        if success:
            print(f"{prefix} → updated")
            done.add(listing_id)
            save_done(done)
            updated += 1
        else:
            print(f"{prefix} → ERROR {resp.status_code}: {resp.text[:120]}", file=sys.stderr)
            errors += 1

        time.sleep(0.8)

    print(f"\nDone.")
    print(f"  Updated           : {updated}")
    print(f"  Already had FAQ   : {skipped_already_has_faq}")
    print(f"  Skipped (done file): {skipped_done_file}")
    print(f"  Errors            : {errors}")


if __name__ == "__main__":
    main()
