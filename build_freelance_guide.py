"""
Freelance Business Manager — PDF Guide + Etsy Listing
Product 2 for NasriTools Etsy Store
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

ACCENT  = colors.HexColor("#4361EE")
DARK    = colors.HexColor("#0D1B2A")
GREEN   = colors.HexColor("#06D6A0")
YELLOW  = colors.HexColor("#FFD166")
LIGHT   = colors.HexColor("#F8F9FA")
WHITE   = colors.white
RED     = colors.HexColor("#EF233C")

styles = getSampleStyleSheet()

def h1(text):
    return Paragraph(text, ParagraphStyle("h1", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=22, textColor=DARK,
        spaceAfter=6, spaceBefore=14, alignment=TA_CENTER))

def h2(text):
    return Paragraph(text, ParagraphStyle("h2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=14, textColor=ACCENT,
        spaceAfter=4, spaceBefore=10))

def body(text):
    return Paragraph(text, ParagraphStyle("body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, textColor=DARK,
        spaceAfter=4, leading=16))

def bullet(text):
    return Paragraph(f"• {text}", ParagraphStyle("bullet", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, textColor=DARK,
        leftIndent=16, spaceAfter=3, leading=15))

def build_pdf():
    doc = SimpleDocTemplate(
        "/home/user/smc-bot/Freelance_Guide.pdf",
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    story = []

    # ── Cover ───────────────────────────────────────────
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph(
        '<font color="#4361EE">FREELANCE BUSINESS MANAGER</font>',
        ParagraphStyle("cover", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=28, alignment=TA_CENTER,
            textColor=ACCENT, spaceAfter=6)
    ))
    story.append(Paragraph(
        "Complete Google Sheets System for Freelancers",
        ParagraphStyle("sub", parent=styles["Normal"],
            fontName="Helvetica", fontSize=14, alignment=TA_CENTER,
            textColor=colors.HexColor("#888888"), spaceAfter=4)
    ))
    story.append(Paragraph(
        "NasriTools | nasritools.etsy.com",
        ParagraphStyle("store", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER,
            textColor=DARK, spaceAfter=10)
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 8*mm))

    # ── Quick Start ─────────────────────────────────────
    story.append(h2("🚀  Quick Start (3 Steps)"))
    steps = [
        ("1", "Download & Open",   "Download the .xlsx file → open in Google Sheets (File > Import) or Excel."),
        ("2", "Enter Your Data",   "Go to each tab and fill in the YELLOW cells with your information."),
        ("3", "Watch It Work",     "Dashboard updates automatically — income, expenses, taxes, clients all tracked."),
    ]
    tdata = [[Paragraph(f"<b>Step {s}</b>", styles["Normal"]),
              Paragraph(f"<b>{t}</b><br/>{d}", styles["Normal"])] for s,t,d in steps]
    tbl = Table(tdata, colWidths=[30*mm, 130*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), LIGHT),
        ("BACKGROUND",  (0,0), (0,-1), ACCENT),
        ("TEXTCOLOR",   (0,0), (0,-1), WHITE),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 11),
        ("ALIGN",       (0,0), (0,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (1,0), (1,-1), [WHITE, LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("ROWPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",  (0,0),(-1,-1),8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6*mm))

    # ── Tabs Overview ────────────────────────────────────
    story.append(h2("📋  What's Inside (7 Tabs)"))
    tabs = [
        ("🏠 Dashboard",        "Real-time overview: monthly revenue, expenses, profit, tax estimate, and top clients."),
        ("👥 Clients",          "Client database with auto-counted projects and total revenue per client."),
        ("📋 Projects",         "Track every project: status (Active/Completed/On Hold), category, budget, deadline, notes."),
        ("🧾 Invoices",         "Invoice tracker with auto overdue detection, payment status, and total paid/unpaid sums."),
        ("💰 Income & Expenses","Log all income and expenses by category; 25% tax estimate calculated automatically."),
        ("⏱️ Time Tracker",     "Log tasks with start/end time; hours and earnings calculated automatically by formula."),
        ("📊 Reports",          "Auto P&L summary, project breakdown, invoice summary, and time/earnings by client."),
    ]
    tdata2 = [[Paragraph(f"<b>{name}</b>", styles["Normal"]),
               Paragraph(desc, styles["Normal"])] for name, desc in tabs]
    tbl2 = Table(tdata2, colWidths=[52*mm, 108*mm])
    tbl2.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("TOPPADDING",  (0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING", (0,0),(-1,-1),8),
    ]))
    story.append(tbl2)
    story.append(Spacer(1, 6*mm))

    # ── How Formulas Work ───────────────────────────────
    story.append(h2("⚙️  How Formulas Work"))
    formulas = [
        ("Dashboard Revenue",    "Automatically sums all income from Income & Expenses tab"),
        ("Invoice Overdue",      '=IF(DueDate &lt; TODAY(),"OVERDUE","Pending") — turns red automatically'),
        ("Time Hours",           "=(End Time - Start Time) × 24 → decimal hours"),
        ("Tax Estimate",         "= Net Profit × 25% (adjustable in cell C52 of Income tab)"),
        ("Client Revenue",       "SUMIF formula totals revenue per client from Projects tab"),
        ("Project Count",        "COUNTIF formula counts projects per client automatically"),
    ]
    for label, desc in formulas:
        story.append(bullet(f"<b>{label}:</b>  {desc}"))
    story.append(Spacer(1, 6*mm))

    # ── Color Guide ─────────────────────────────────────
    story.append(h2("🎨  Color Guide"))
    story.append(bullet("<b>Yellow cells</b> = Enter your data here"))
    story.append(bullet("<b>Blue cells</b> = Formulas (do not edit)"))
    story.append(bullet("<b>Green rows</b> = Completed / Paid"))
    story.append(bullet("<b>Red rows</b> = Overdue / Unpaid"))
    story.append(Spacer(1, 6*mm))

    # ── Tips ────────────────────────────────────────────
    story.append(h2("💡  Pro Tips"))
    tips = [
        "Add your business currency symbol in the Format > Number > Currency menu.",
        "Use the Time Tracker tab daily — it automatically calculates your hourly earnings.",
        "The Dashboard refreshes every time you open the file — no manual refresh needed.",
        "You can add rows to any tab; formulas are designed to work with SUMIF/COUNTIF across full columns.",
        "Duplicate the file each month for monthly archives, then start fresh.",
        "Change the tax rate in Income tab cell C52 to match your country's rate.",
    ]
    for tip in tips:
        story.append(bullet(tip))

    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Thank you for purchasing from NasriTools!<br/>"
        "If you need help, contact us at nasritools.etsy.com",
        ParagraphStyle("footer", parent=styles["Normal"],
            fontName="Helvetica", fontSize=10, alignment=TA_CENTER,
            textColor=colors.HexColor("#888888"))
    ))

    doc.build(story)
    print("✅ PDF: Freelance_Guide.pdf")

def build_listing():
    listing = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ETSY LISTING — PRODUCT 2: FREELANCE BUSINESS MANAGER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TITLE (140 chars):
Freelance Business Manager Google Sheets Template | Client Invoice Time Tracker | Freelancer Planner

PRICE: $19

CATEGORY:
Craft Supplies & Tools → Templates → Spreadsheets

─── DESCRIPTION ───────────────────────────────────

🔵 FREELANCE BUSINESS MANAGER — Google Sheets Template

Run your entire freelance business from ONE spreadsheet.
Track clients, projects, invoices, income, expenses, and time — all in one place.

━━━━━━━━━━━━━━━━━━━
✅ WHAT'S INCLUDED
━━━━━━━━━━━━━━━━━━━

📥 Instant Download:
• Freelance_Business_Manager.xlsx (works in Google Sheets & Excel)
• PDF Setup Guide (step-by-step instructions)

7 Professional Tabs:
🏠 Dashboard — Live monthly revenue, profit, tax, top clients
👥 Clients — Client database with auto project count + revenue
📋 Projects — Status, category, budget, deadline tracker
🧾 Invoices — Auto overdue detection, payment status tracking
💰 Income & Expenses — Full P&L with 25% tax estimate
⏱️ Time Tracker — Log hours, auto-calculate earnings
📊 Reports — Auto P&L, project, invoice & time summaries

━━━━━━━━━━━━━━━━━━━
🎯 PERFECT FOR
━━━━━━━━━━━━━━━━━━━
• Freelance designers, developers, writers, marketers
• Consultants and coaches managing multiple clients
• Anyone who bills by hour or project
• Self-employed professionals wanting organized finances
• Freelancers tired of expensive software subscriptions

━━━━━━━━━━━━━━━━━━━
⚡ KEY FEATURES
━━━━━━━━━━━━━━━━━━━
✔ Auto overdue invoice detection (turns red instantly)
✔ Time tracker with automatic hours & earnings formula
✔ 25% tax estimate (adjustable to your rate)
✔ Dashboard updates automatically — no manual refresh
✔ SUMIF/COUNTIF formulas across all tabs
✔ Color-coded status: green = done, red = overdue
✔ 50+ pre-filled sample rows to guide you
✔ No subscriptions, no logins — yours forever

━━━━━━━━━━━━━━━━━━━
🚀 HOW TO USE
━━━━━━━━━━━━━━━━━━━
1️⃣ Download the file after purchase
2️⃣ Open in Google Sheets (File > Import) or Excel
3️⃣ Fill in the YELLOW cells with your data
4️⃣ Dashboard updates automatically!

━━━━━━━━━━━━━━━━━━━
📦 INSTANT DOWNLOAD
━━━━━━━━━━━━━━━━━━━
After purchase you'll receive:
• .xlsx file (works with Google Sheets & Microsoft Excel)
• PDF User Guide

⭐ Questions? Message us — we respond within 24 hours.

─── TAGS (13 tags, each max 30 chars) ─────────────

freelance tracker
client invoice template
google sheets freelancer
time tracker spreadsheet
freelance business manager
invoice tracker excel
freelance income tracker
project management sheet
self employed tracker
freelancer planner
hours tracker template
freelance budget tracker
small business template

─── NOTES ──────────────────────────────────────────
• Price: $19 (lower than Product 1 to attract more buyers)
• Category: Craft Supplies → Templates → Spreadsheets
• Files to attach: Freelance_Business_Manager.xlsx + Freelance_Guide.pdf
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    with open("/home/user/smc-bot/Freelance_Etsy_Listing.txt", "w") as f:
        f.write(listing)
    print("✅ Listing: Freelance_Etsy_Listing.txt")

build_pdf()
build_listing()
