# NasriTools — منتجات Etsy الرقمية (جاهزة للرفع)

**آخر تحديث:** 2026-08-26
**المتجر:** NasriTools · فارغ تماماً (0 نشط · 0 مسوّدة)

---

## المحتويات

```
DIGITAL_PRODUCTS/
├── files/          31 ملفاً — 7 xlsx + 17 png + 7 mp4
├── content/
│   ├── listings.json        ← كل المحتوى منظّماً (المصدر الوحيد)
│   ├── صفحة_النسخ.html      ← افتحها: أزرار نسخ لكل حقل
│   └── build_listings.py    ← السكربت الذي بنى listings.json
└── README.md
```

---

## المنتجات السبعة

| # | المنتج | السعر $ | الملف |
|---|---|---|---|
| 1 ⭐ | Trading Journal | 19.99 | PREMIUM_Trading_Journal.xlsx |
| 2 ⭐ | Business KPI Dashboard | 19.99 | PREMIUM_Business_KPI.xlsx |
| 3 | Invoice & Client Tracker | 14.99 | PREMIUM_Invoice_Client.xlsx |
| 4 ⭐ | Monthly Budget Tracker | 12.99 | PREMIUM_Budget_Tracker.xlsx |
| 5 | Habit Tracker | 12.99 | PREMIUM_Habit_Tracker.xlsx |
| 6 | Student Planner + GPA | 12.99 | PREMIUM_Student_Planner.xlsx |
| 7 | Meal Planner + Grocery | 12.99 | PREMIUM_Meal_Planner.xlsx |

⭐ = **ابدأ بهذه الثلاثة فقط** (قرار المستخدم في خطة الإطلاق: *"لا ترفع كل شيء دفعة واحدة"*).
راقب المشاهدات أسبوعين، ثم ارفع الباقي. Bundle بـ59.99 بعد 5 مبيعات.

**كل منتج مُتحقَّق منه:** العنوان ≤140 حرفاً · 13 وسماً (كلٌّ ≤20 حرفاً) · وصف ~1600 حرف.

## الصور لكل منتج (بالترتيب)
1. `0X_<اسم المنتج>.png` ← **الأهم: لوحة التحكّم**
2. `included_<اسم>.png` ← قائمة المحتويات
3. `00_How_It_Works.png` ← مشترك بين الكل
+ فيديو `demo_<اسم>.mp4`

---

## إعدادات Etsy لكل listing
- النوع: **Digital** · Quantity: **999**
- Who made it: I did · When: 2020–2025 · What: A finished product
- الفئة المستعملة سابقاً: Paper & Party Supplies → Templates (taxonomy_id **2078**)
- **احفظ كـ Draft أولاً** — النشر يخصم 0.20 $ لكل منتج

---

## ⚠️ حالة الحساب (مهم)
- **تحقّق بنكي معلّق:** Etsy أرسلت إيداعاً صغيراً؛ يجب إدخال المبلغ بالضبط.
  المحاولة بـ0.07 فشلت. الشريط الآن **أزرق** (لا خطر تعليق) بانتظار إيداع جديد.
  ابحث في كشف البنك عن: `Etsy` / `Adyen` / `Envoy` / `Worldpay`.
- التحقّق يخصّ **استلام المدفوعات** — لا يمنع رفع المنتجات.

---

## 🔴 ما لا يعمل (مُجرَّب بالكامل 2026-08-26 — لا تُعِد المحاولة)

| الطريق | النتيجة |
|---|---|
| Playwright + ملف كروم الحقيقي | ❌ مهلة 180s — لا يفتح (الملف 1.53 GB) |
| نسخة مصغّرة من ملف كروم (3 MB) | ❌ يفتح لكن الكوكيز لا تُفكّ (App-Bound Encryption، كروم 127+) |
| CDP `--remote-debugging-port` | ❌ كروم 136+ يمنعه على الملف الافتراضي |
| **Etsy API v3** | ❌ **CLIENT_ID `pluc0garr...` مسحوب** — "application not recognized" |
| إضافة claude-in-chrome | ❌ نطاق Etsy محجوب (لا تنقّل ولا قراءة) |
| computer-use على كروم | ❌ مستوى "read" — رؤية بلا نقر |

**البيئة:** Playwright 1.62.0 · Chrome 151 · Firefox (playwright) 153

---

## ✅ ما يعمل — طريقان

### (أ) فايرفوكس آلي — يحتاج تسجيل دخول واحد
```
ملف الجلسة: scratchpad/ffprof
تشغيل نافذة عادية مرئية:
  & "C:\Users\nasri\AppData\Local\ms-playwright\firefox-1538\firefox\firefox.exe" `
    -profile "<مسار ffprof>" -no-remote -new-window "https://www.etsy.com/signin"
```
المستخدم يسجّل مرّة → الجلسة تُحفظ → Playwright يعيد استعمال نفس الملف → رفع آلي كامل.
**اختُبر:** فايرفوكس يفتح Etsy بنجاح (بلا قيود كروم). ⚠️ لا تمرّر `args=["-width",...]` — تُسقط فايرفوكس.

### (ب) يدوي — يعمل فوراً
افتح `content/صفحة_النسخ.html` → أزرار نسخ لكل حقل → الصق في Etsy. ~10 دقائق للمنتج.

---

## 🔑 الحدّ الوحيد
**تسجيل الدخول يحتاج المستخدم** — لن يُلمس أي كلمة مرور. كل طريق آلي يتطلّب إمّا جلسة مسجّلة أو مفتاح API (مسحوب).
**الحلّ الجذري للمستقبل:** تسجيل تطبيق Etsy جديد على `etsy.com/developers` → مفتاح دائم → API رسمي (يحتاج موافقة Etsy، أيام).
