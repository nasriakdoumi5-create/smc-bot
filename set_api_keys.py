"""
set_api_keys.py
Updates the Etsy API credentials across EVERY script in the repo at once.

Use it after creating a new app at etsy.com/developers/your-apps
(the old app stopped being recognized by Etsy).

Run:
    python set_api_keys.py <NEW_KEYSTRING> <NEW_SHARED_SECRET>

Example:
    python set_api_keys.py abc123def456ghi789 xy9wz8vu7t
"""
import re, sys
from pathlib import Path

OLD_ID     = "pluc0garrgcjzhim0hawxf0k"
OLD_SECRET = "hc89hlqkd6"
ROOT       = Path(__file__).parent

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("  ✗ Missing arguments.\n")
        print("  Get your keys here: https://www.etsy.com/developers/your-apps")
        print("    Keystring      → the long public key")
        print("    Shared secret  → the short private key\n")
        return

    new_id, new_secret = sys.argv[1].strip(), sys.argv[2].strip()

    if len(new_id) < 10:
        print(f"  ✗ Keystring looks too short: '{new_id}'")
        return

    print("=" * 60)
    print("  Updating Etsy API credentials in every script")
    print("=" * 60)
    print(f"  Keystring : {OLD_ID[:8]}...  →  {new_id[:8]}...")
    print(f"  Secret    : {'*' * len(OLD_SECRET)}  →  {'*' * len(new_secret)}\n")

    changed = 0
    for path in sorted(ROOT.rglob("*.py")):
        if path.name == "set_api_keys.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if OLD_ID not in text and OLD_SECRET not in text:
            continue
        new_text = text.replace(OLD_ID, new_id).replace(OLD_SECRET, new_secret)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"  ✓ {path.relative_to(ROOT)}")
            changed += 1

    print(f"\n{'=' * 60}")
    print(f"  Updated {changed} file(s)")
    print("\n  Next steps:")
    print("    1. python etsy_reauth.py       ← get a fresh token")
    print("    2. python publish_premium.py   ← publish the products")
    print("=" * 60)

if __name__ == "__main__":
    main()
