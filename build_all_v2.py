"""
build_all_v2.py
Regenerates ALL catalog products with Factory v2 (quality templates).
Run:  python build_all_v2.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from nasritools.products import CATALOG
from nasritools.factory2 import build_workbook

def main():
    ok, failed = 0, []
    for i, cfg in enumerate(CATALOG, 1):
        try:
            out = build_workbook(cfg)
            size = out.stat().st_size
            print(f"  [{i:3}/{len(CATALOG)}] ✓ {cfg['slug']:35} {size:>7,} bytes")
            ok += 1
        except Exception as e:
            print(f"  [{i:3}/{len(CATALOG)}] ✗ {cfg['slug']:35} {e}")
            failed.append((cfg["slug"], str(e)))
    print(f"\n  Built: {ok}   Failed: {len(failed)}")
    for slug, err in failed:
        print(f"    ✗ {slug}: {err}")

if __name__ == "__main__":
    main()
