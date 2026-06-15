"""
NasriTools Suite — Main CLI
Usage: python main.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nasritools.factory import build_product
from nasritools.products import CATALOG


def menu():
    print("\n" + "═" * 50)
    print("  NasriTools Suite")
    print("═" * 50)
    print("  1 — Build a product from catalog")
    print("  2 — List all catalog products")
    print("  3 — Build ALL products in catalog")
    print("  0 — Exit")
    print("─" * 50)
    return input("  Choose: ").strip()


def list_products():
    print(f"\n  {'#':<4} {'Slug':<30} {'Name':<35} {'Price'}")
    print("  " + "─" * 80)
    for i, p in enumerate(CATALOG, 1):
        print(f"  {i:<4} {p['slug']:<30} {p['name']:<35} {p.get('price','?')}")


def build_one():
    list_products()
    choice = input("\n  Enter number: ").strip()
    try:
        idx = int(choice) - 1
        cfg = CATALOG[idx]
    except (ValueError, IndexError):
        print("  Invalid choice.")
        return
    build_product(cfg)


def build_all():
    confirm = input(f"\n  Build ALL {len(CATALOG)} products? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("  Cancelled.")
        return
    for i, cfg in enumerate(CATALOG, 1):
        print(f"\n  [{i}/{len(CATALOG)}]", end="")
        build_product(cfg)
    print("\n\n  ✅ All products built!")


def main():
    while True:
        choice = menu()
        if choice == "1":
            build_one()
        elif choice == "2":
            list_products()
        elif choice == "3":
            build_all()
        elif choice == "0":
            print("  Bye!\n")
            break
        else:
            print("  Unknown option.")


if __name__ == "__main__":
    main()
