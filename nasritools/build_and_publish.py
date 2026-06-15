"""
NasriTools — Build + Publish in one command
Usage:
  python nasritools/build_and_publish.py              # build & publish all
  python nasritools/build_and_publish.py budget_tracker
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nasritools.factory import build_product
from nasritools.etsy_auth import get_token
from nasritools.etsy_publisher import get_shop_id, publish_product, _load_db, _save_db
from nasritools.products import CATALOG


def run(slugs: list = None):
    targets = [c for c in CATALOG if (not slugs or c["slug"] in slugs)]

    print(f"\n{'═'*50}")
    print(f"  NasriTools — Build & Publish ({len(targets)} products)")
    print(f"{'═'*50}")

    print("\n  [AUTH] Loading Etsy token...")
    token   = get_token()
    shop_id = get_shop_id(token)
    print(f"  Shop ID: {shop_id}")

    db = _load_db()
    results = {"built": 0, "published": 0, "failed": []}

    for i, cfg in enumerate(targets, 1):
        slug = cfg["slug"]
        print(f"\n{'─'*50}")
        print(f"  [{i}/{len(targets)}] {cfg['name']}")
        print(f"{'─'*50}")

        build_product(cfg)
        results["built"] += 1

        time.sleep(1)
        ok = publish_product(cfg, shop_id, token, db)
        if ok:
            results["published"] += 1
        else:
            results["failed"].append(slug)

    print(f"\n{'═'*50}")
    print(f"  DONE")
    print(f"  Built:     {results['built']}")
    print(f"  Published: {results['published']}")
    if results["failed"]:
        print(f"  Failed:    {', '.join(results['failed'])}")
    print(f"{'═'*50}\n")


if __name__ == "__main__":
    slugs = sys.argv[1:] or None
    run(slugs)
