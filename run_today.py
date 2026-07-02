"""
run_today.py

Master runbook — runs all pending shop tasks in the correct order.
Safe to run multiple times (skips what's already done).

Tasks:
  1. Fix shop sections (rename existing to correct names)
  2. Assign all 119 listings to their sections
  3. Update sale message (thank-you email)
  4. Update shop announcement
  5. Create FRIENDS100 coupon (100% off for reviews)

After this script: run generate_all_missing_images.py to fill image gaps.
"""
import subprocess, sys, time
from pathlib import Path

SCRIPTS = [
    ("Fix Sections + Sale Message",   "fix_setup.py"),
    ("Update Shop Announcement",      "update_announcement.py"),
    ("Create FRIENDS100 Coupon",      "create_coupon.py"),
]

def run(script):
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,   # print live output
        text=True,
    )
    return result.returncode == 0

def main():
    print("=" * 65)
    print("  NasriTools — Daily Task Runner")
    print("=" * 65)

    results = []
    for label, script in SCRIPTS:
        path = Path(script)
        if not path.exists():
            print(f"\n  [SKIP] {label} — {script} not found")
            results.append((label, "skip"))
            continue

        print(f"\n{'─'*65}")
        print(f"  ▶  {label}")
        print(f"{'─'*65}")

        ok = run(script)
        results.append((label, "OK" if ok else "FAIL"))
        if not ok:
            print(f"  ⚠  {label} returned a non-zero exit code")
        time.sleep(2)

    print(f"\n{'='*65}")
    print("  SUMMARY")
    print(f"{'─'*65}")
    for label, status in results:
        icon = "✅" if status == "OK" else ("⚪" if status == "skip" else "❌")
        print(f"  {icon}  {label}: {status}")

    print(f"\n  NEXT STEPS (manual):")
    print(f"  1. python generate_all_missing_images.py  ← fill image gaps (all 119)")
    print(f"  2. Upload thumbnails/brand/shop_logo_1000x1000.png  ← Shop Manager")
    print(f"  3. Upload thumbnails/brand/shop_banner_1600x400.png ← Shop Manager")
    print(f"  4. Paste about_section.txt → Shop Manager → Info & Appearance → Story")
    print(f"  5. Create Pinterest account at pinterest.com/nasritools")
    print(f"  6. Post 1 pin/day from pinterest_pins.md")
    print(f"  7. Share FRIENDS100 coupon with friends for first reviews")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
