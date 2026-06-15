"""
NasriTools Etsy Agent — يعمل على جهاز المستخدم
يجلب روابط المنتجات ويستطيع إنشاء listings جديدة
"""
from playwright.sync_api import sync_playwright
import time

SHOP = "NasriTools"

def get_listings(page):
    """جلب روابط كل المنتجات"""
    print("\n🔍 جلب روابط المنتجات...")
    page.goto(f"https://www.etsy.com/shop/{SHOP}", wait_until="domcontentloaded")
    time.sleep(2)

    links = page.query_selector_all("a[href*='/listing/']")
    urls = list(set([
        l.get_attribute("href") for l in links
        if l.get_attribute("href") and "/listing/" in l.get_attribute("href")
    ]))

    print(f"\n✅ وُجد {len(urls)} منتج:\n")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")
    return urls

def create_listing(page, data):
    """إنشاء listing جديد على Etsy"""
    print("\n🚀 فتح صفحة إنشاء منتج جديد...")
    page.goto("https://www.etsy.com/your/shops/me/tools/listings/create",
              wait_until="domcontentloaded")
    time.sleep(3)

    print(f"📌 العنوان: {data['title']}")
    title_input = page.query_selector("input[name='title'], #title, [data-testid='title']")
    if title_input:
        title_input.fill(data["title"])
        print("✅ العنوان أُدخل")
    else:
        print("⚠️ لم أجد خانة العنوان — الصفحة قد تكون مختلفة")

    print("\n✋ السكريبت توقف — أكمل باقي الحقول يدوياً إذا لزم")
    time.sleep(60)  # دقيقة كاملة للمراجعة

def main():
    with sync_playwright() as p:
        print("🌐 فتح المتصفح...")

        # استخدام Chromium بدون Profile موجود (يحتاج تسجيل دخول)
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500  # تأخير للمراقبة
        )
        context = browser.new_context()
        page = context.new_page()

        print("🔑 يرجى تسجيل الدخول على Etsy في المتصفح الذي فتح...")
        page.goto("https://www.etsy.com/signin", wait_until="domcontentloaded")

        print("⏳ انتظر... سجّل دخولك ثم اضغط Enter هنا")
        input(">>> اضغط Enter بعد تسجيل الدخول: ")

        # الخيارات
        print("\nماذا تريد؟")
        print("  1 — جلب روابط المنتجات")
        print("  2 — إنشاء listing جديد (تجريبي)")
        choice = input("اختر (1 أو 2): ").strip()

        if choice == "1":
            get_listings(page)

        elif choice == "2":
            data = {
                "title": input("أدخل عنوان المنتج: ").strip()
            }
            create_listing(page, data)

        input("\nاضغط Enter لإغلاق المتصفح...")
        browser.close()

if __name__ == "__main__":
    main()
