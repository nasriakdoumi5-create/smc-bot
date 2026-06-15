"""
جلب روابط منتجات NasriTools بدون تسجيل دخول
"""
from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        print("🔍 فتح صفحة المتجر...")
        page.goto("https://www.etsy.com/shop/NasriTools", timeout=20000)
        time.sleep(4)

        links = page.query_selector_all("a[href*='/listing/']")
        urls = list(set([
            l.get_attribute("href") for l in links
            if l.get_attribute("href") and "/listing/" in l.get_attribute("href")
        ]))

        print(f"\n✅ المنتجات ({len(urls)}):\n")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")

        input("\nاضغط Enter لإغلاق...")
        browser.close()

if __name__ == "__main__":
    main()
