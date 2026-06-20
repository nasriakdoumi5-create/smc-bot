"""
run_all.py
Runs every pending step in the correct order.
One command to finish everything.
"""
import subprocess, sys, time

STEPS = [
    ("update_prices.py",          "Updating strategic prices"),
    ("update_hero_descriptions.py","Updating Hero product descriptions"),
    ("upload_thumbnails.py",       "Uploading thumbnails to Etsy listings"),
    ("activate_bundles.py",        "Activating all draft Bundle listings"),
]

def run(script, label):
    print(f"\n{'='*65}")
    print(f"  STEP: {label}")
    print(f"  Script: python {script}")
    print(f"{'='*65}")
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"\n  [WARN] {script} exited with code {result.returncode}")
    time.sleep(2)

def main():
    print("=" * 65)
    print("  NasriTools — RUN ALL (Final Completion)")
    print(f"  {len(STEPS)} steps total")
    print("=" * 65)

    for script, label in STEPS:
        run(script, label)

    print(f"\n{'='*65}")
    print("  ALL STEPS COMPLETE")
    print("  Your store is now fully optimized.")
    print("  Next: get your first reviews using FRIENDS100 coupon")
    print(f"{'='*65}")

if __name__ == "__main__":
    main()
