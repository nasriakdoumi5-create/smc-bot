"""
NasriTools Etsy Agent v2 — يستخدم Chrome الحقيقي مع جلستك المسجّلة
"""
from playwright.sync_api import sync_playwright
import time, os

SHOP = "NasriTools"
# مسار ملف Chrome الخاص بك على Windows
CHROME_PROFILE = r"C:\Users\nasri\AppData\Local\Google\Chrome\User Data"

def get_listings(page):
    print("\n🔍 جلب روابط المنتجات...")
    page.goto(f"https://www.etsy.com/shop/{SHOP}", wait_until="domcontentloaded", timeout=15000)
    time.sleep(3)
    links = page.query_selector_all("a[href*='/listing/']")
    urls = list(set([
        l.get_attribute("href") for l in links
        if l.get_attribute("href") and "/listing/" in l.get_attribute("href")
    ]))
    print(f"\n✅ {len(urls)} منتج:\n")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    return urls

def main():
    with sync_playwright() as p:
        print("🌐 فتح Chrome مع جلستك المسجّلة...")

        # استخدام Chrome الحقيقي مع Profile المستخدم
        context = p.chromium.launch_persistent_context(
            user_data_dir=CHROME_PROFILE,
            channel="chrome",       # Chrome الحقيقي وليس Chromium
            headless=False,
            slow_mo=300,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = context.new_page()

        print("\nماذا تريد؟")
        print("  1 — جلب روابط المنتجات")
        print("  2 — فتح صفحة إنشاء listing جديد")
        choice = input("اختر (1 أو 2): ").strip()

        if choice == "1":
            get_listings(page)

        elif choice == "2":
            print("\n🚀 فتح صفحة إنشاء منتج...")
            page.goto(
                "https://www.etsy.com/your/shops/me/tools/listings/create",
                wait_until="domcontentloaded", timeout=15000
            )
            print("✅ الصفحة مفتوحة — أكمل يدوياً في المتصفح")

        input("\nاضغط Enter لإغلاق...")
        context.close()

if __name__ == "__main__":
    main()
