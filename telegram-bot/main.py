import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request, HTTPException
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_CHAT_ID = os.environ["TELEGRAM_ADMIN_CHAT_ID"]
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "pawcase-secret-2024")

bot = Bot(token=BOT_TOKEN)

# ── Telegram commands ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐾 *بوت إدارة PawCase*\n\n"
        "الأوامر المتاحة:\n"
        "📦 /orders — آخر 5 طلبات\n"
        "💰 /revenue — مبيعات اليوم\n"
        "📊 /stats — إحصائيات المتجر\n"
        "✅ /health — حالة المتجر",
        parse_mode="Markdown"
    )

async def cmd_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await update.message.reply_text("📦 جاري جلب آخر الطلبات...")
    # TODO: fetch from DB when connected
    await update.message.reply_text(
        "📦 *آخر الطلبات*\n\n"
        "سيتم عرض الطلبات هنا بعد ربط قاعدة البيانات.\n"
        "حالياً تصلك الإشعارات فوراً مع كل طلب جديد ✅",
        parse_mode="Markdown"
    )

async def cmd_revenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await update.message.reply_text(
        "💰 *مبيعات اليوم*\n\n"
        "سيتم عرض الإيرادات هنا بعد ربط قاعدة البيانات.\n"
        "تصلك إشعارات الطلبات فوراً ✅",
        parse_mode="Markdown"
    )

async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await update.message.reply_text(
        "✅ *حالة المتجر*\n\n"
        "🟢 البوت يعمل بشكل طبيعي\n"
        f"🕐 الوقت: {datetime.now().strftime('%H:%M:%S')}",
        parse_mode="Markdown"
    )

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        return
    await update.message.reply_text(
        "📊 *إحصائيات PawCase*\n\n"
        "سيتم عرض الإحصائيات الكاملة بعد ربط قاعدة البيانات.\n"
        "تصلك إشعارات الطلبات فوراً ✅",
        parse_mode="Markdown"
    )

# ── FastAPI app ────────────────────────────────────────────────────────────────

app_telegram = Application.builder().token(BOT_TOKEN).build()
app_telegram.add_handler(CommandHandler("start", cmd_start))
app_telegram.add_handler(CommandHandler("orders", cmd_orders))
app_telegram.add_handler(CommandHandler("revenue", cmd_revenue))
app_telegram.add_handler(CommandHandler("health", cmd_health))
app_telegram.add_handler(CommandHandler("stats", cmd_stats))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await app_telegram.initialize()
    await app_telegram.start()
    logger.info("Bot started ✅")
    yield
    await app_telegram.stop()
    await app_telegram.shutdown()

api = FastAPI(lifespan=lifespan)

# ── Webhook: receive Telegram updates ─────────────────────────────────────────

@api.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"ok": True}

# ── Webhook: receive new order from PawCase store ─────────────────────────────

@api.post("/order")
async def new_order(request: Request):
    secret = request.headers.get("x-webhook-secret", "")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()

    name     = data.get("customerName", "عميل")
    email    = data.get("customerEmail", "—")
    total    = data.get("total", 0)
    items    = data.get("items", [])
    address  = data.get("address", {})
    order_id = data.get("orderId", "—")

    items_text = "\n".join(
        f"  • {item.get('name', '—')} x{item.get('quantity', 1)} — €{item.get('price', 0)}"
        for item in items
    ) or "  —"

    city    = address.get("city", "")
    country = address.get("country", "")

    message = (
        f"🛍️ *طلب جديد!*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👤 *العميل:* {name}\n"
        f"📧 *الإيميل:* {email}\n"
        f"📍 *الموقع:* {city}, {country}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"📦 *المنتجات:*\n{items_text}\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"💰 *المجموع:* €{total}\n"
        f"🔖 *رقم الطلب:* `{order_id}`\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"✅ تم الدفع عبر Stripe"
    )

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=message,
        parse_mode="Markdown"
    )
    return {"ok": True}

# ── Health check ──────────────────────────────────────────────────────────────

@api.get("/")
async def root():
    return {"status": "PawCase Bot running 🐾"}
