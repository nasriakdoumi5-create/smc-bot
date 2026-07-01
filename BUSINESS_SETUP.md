# SMC Trading Bot — Business Setup Guide

---

## الفكرة التجارية

```
┌─────────────────────────────────────────────────────┐
│  TradingView Alert  →  /webhook  →  Telegram Channel │
│                                                      │
│  الربح من 3 مصادر:                                  │
│  ① بيع المؤشرات على TradingView (15-50$/شهر)       │
│  ② اشتراكات القناة الخاصة (20-50$/شهر)             │
│  ③ Bot-as-a-Service (إعداد البوت للآخرين)          │
└─────────────────────────────────────────────────────┘
```

---

## الخطوة ① — إعداد قناة Telegram الخاصة

### إنشاء القناة:
1. افتح Telegram → اضغط على ✏️ → "New Channel"
2. اسم القناة: `NQ Signals Pro` أو `SMC Trading Signals`
3. النوع: **Private** (خاصة — بالدعوة فقط)
4. أضف البوت (`@your_bot_username`) كـ **Administrator**
5. صلاحيات البوت: Post Messages ✅، Delete Messages ✅

### ربط القناة بالبوت:
```bash
# في Railway → Variables → أضف:
CHANNEL_ID = -100xxxxxxxxxx   # ID القناة (يبدأ بـ -100)
```

### كيف تحصل على Channel ID:
```
1. أضف @userinfobot إلى القناة
2. أرسل أي رسالة في القناة
3. سيرسل لك @userinfobot الـ ID تلقائياً
```

---

## الخطوة ② — إعداد TradingView Alerts

### للمؤشر: VWAP Bounce Pro

```
1. افتح TradingView → الشارت → أضف المؤشر
2. اضغط ⏰ (Create Alert)
3. Condition: "VWAP Bounce Pro"
4. Alert Actions:
   ☑️ Webhook URL: https://smc-bot-production-70f3.up.railway.app/webhook
5. Message: اتركه فارغاً (المؤشر يرسل JSON تلقائياً)
6. Alert name: "VWAP MNQ"
7. Expiration: Open-ended
```

### للمؤشر: Kill Zone Sweep Pro

```
1. نفس الخطوات أعلاه
2. Alert name: "Kill Zone MNQ"
3. نفس Webhook URL
```

### التنبيه:
> ⚠️ **مهم**: في TradingView الـ Alert Message يجب أن يكون فارغاً أو `{{strategy.order.alert_message}}` — المؤشرات ترسل JSON تلقائياً عبر `alert()` في Pine Script.

---

## الخطوة ③ — بيع المؤشرات على TradingView

### نشر المؤشر (Publish):
```
1. Pine Editor → Save → اضغط Publish Script
2. Visibility: Invite-only (خاصة — أفضل للبيع)
3. وصف جذاب بالإنجليزية:
```

#### نموذج وصف VWAP Bounce Pro:
```
🎯 VWAP Bounce Pro — NQ/MNQ 5M Scalping System

Detects high-probability mean-reversion entries when price
rejects the VWAP ± 1.5 ATR bands with RSI confirmation.

✅ 5-10 signals per day on MNQ 5M
✅ Dynamic JSON webhook alerts (SL/TP auto-calculated)
✅ Built-in session filter (London + New York only)
✅ Rejection candle confirmation (wick + body filter)

Best on: MNQ, NQ, ES, MES — 5 Minute chart
Sessions: 07:00–20:00 UTC
```

#### نموذج وصف Kill Zone Sweep Pro:
```
⚡ Kill Zone Sweep Pro — Liquidity Sweep + Reversal

Identifies institutional liquidity sweeps above PDH/PDL,
Asia Session H/L, and Swing Highs/Lows during Kill Zones.

✅ PDH/PDL sweep: 3 points (highest priority)
✅ Asia H/L sweep: 2 points
✅ Swing H/L sweep: 1 point
✅ Only fires during London KZ (07:00-11:00) and NY KZ (13:30-17:00)
✅ Quality rating: 1-3 stars based on confluence

Best on: MNQ, NQ — 5 Minute chart
```

### الأسعار المقترحة:
```
┌─────────────────────────────────────────┐
│  VWAP Bounce Pro:      $15/month        │
│  Kill Zone Sweep Pro:  $20/month        │
│  Bundle (كلاهما):      $30/month        │
│  + Bot Signals Channel: $20/month       │
│  ─────────────────────────────────────  │
│  Full Package:          $45/month       │
└─────────────────────────────────────────┘
```

### كيفية إدارة الوصول:
```
TradingView → Profile → My Scripts → الـ Script → Manage Access
→ Add users by username/email
→ Set expiration date (30 days, 90 days, 1 year)
```

---

## الخطوة ④ — إدارة المشتركين في القناة

### الطريقة:
1. المشترك يدفع عبر PayPal/USDT
2. أنت تولّده رابط دعوة `invite link` للقناة
3. كل شهر تجدد — أو تزيل من القناة

### إنشاء رابط دعوة مؤقت (30 يوم):
```
القناة → إعدادات → Invite Links → Create New Link
Expire: 30 days | Limit: 1 use
```

---

## الخطوة ⑤ — Railway Environment Variables

```bash
# في Railway Dashboard → Variables:

TELEGRAM_TOKEN   = 8986679008:AAHmT44SZeoUzdkiaKg-OlnA3NHOonHZ2cw
TELEGRAM_CHAT_ID = 6526134897          # معرفك الشخصي
CHANNEL_ID       = -100xxxxxxxxxx      # معرف القناة
WEBHOOK_TOKEN    = my_secret_token_123  # (اختياري) حماية الـ webhook
```

---

## الخطوة ⑥ — اختبار النظام

### اختبار الـ webhook يدوياً:
```bash
curl -X POST https://smc-bot-production-70f3.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"s":"MNQ","t":"LONG","p":21000,"sl":20970,"tp1":21060,"tp2":21090,"r":41.5,"a":25.0,"v":20980,"src":"vwap_lower"}'
```

### التحقق من حالة البوت:
```
https://smc-bot-production-70f3.up.railway.app/
```
يعرض: status, session, signals count, uptime

---

## ملخص مصادر الدخل

```
┌─────────────────────────────────────────────────────┐
│                  📊 الخطة التجارية                  │
├─────────────────────────────────────────────────────┤
│  10 مشترك × $45/شهر    =    $450/شهر               │
│  20 مشترك × $45/شهر    =    $900/شهر               │
│  50 مشترك × $30/شهر    =  $1,500/شهر               │
│                                                     │
│  مصاريف ثابتة:                                      │
│  Railway:       ~$5/شهر                             │
│  TradingView:   $14.95/شهر (Essential)              │
│  ─────────────────────────────────────────────────  │
│  صافي الربح مع 20 مشترك: ~$880/شهر 🎯              │
└─────────────────────────────────────────────────────┘
```
