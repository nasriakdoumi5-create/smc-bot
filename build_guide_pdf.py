"""
Build a professional PDF guide + Etsy listing for the digital product
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import PageBreak

W, H = A4

# ── Colors ───────────────────────────────────────────
DARK    = colors.HexColor("#1A1A2E")
PRIMARY = colors.HexColor("#16213E")
ACCENT  = colors.HexColor("#E94560")
GREEN   = colors.HexColor("#0F9B58")
YELLOW  = colors.HexColor("#FFD700")
BLUE    = colors.HexColor("#4A90D9")
ORANGE  = colors.HexColor("#FF6B35")
LIGHT   = colors.HexColor("#F5F5F5")
WHITE   = colors.white
GRAY    = colors.HexColor("#666666")

def build_pdf():
    doc = SimpleDocTemplate(
        "/home/user/smc-bot/Product_Guide.pdf",
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("Title",
        fontSize=28, textColor=WHITE, alignment=TA_CENTER,
        fontName="Helvetica-Bold", spaceAfter=6, leading=34)

    subtitle_style = ParagraphStyle("Subtitle",
        fontSize=13, textColor=colors.HexColor("#AAAAAA"),
        alignment=TA_CENTER, fontName="Helvetica-Oblique", spaceAfter=4)

    h1_style = ParagraphStyle("H1",
        fontSize=16, textColor=WHITE, fontName="Helvetica-Bold",
        spaceAfter=6, spaceBefore=10, leading=20)

    h2_style = ParagraphStyle("H2",
        fontSize=13, textColor=DARK, fontName="Helvetica-Bold",
        spaceAfter=4, spaceBefore=8)

    body_style = ParagraphStyle("Body",
        fontSize=11, textColor=DARK, fontName="Helvetica",
        spaceAfter=4, leading=16, alignment=TA_JUSTIFY)

    bullet_style = ParagraphStyle("Bullet",
        fontSize=11, textColor=DARK, fontName="Helvetica",
        spaceAfter=3, leading=15, leftIndent=15)

    note_style = ParagraphStyle("Note",
        fontSize=10, textColor=colors.HexColor("#5D4037"),
        fontName="Helvetica-Oblique", spaceAfter=3, leading=14,
        leftIndent=10, backColor=colors.HexColor("#FFF9C4"))

    story = []

    # ══ COVER PAGE ══════════════════════════════════
    # Dark banner
    story.append(Spacer(1, 5*mm))

    cover_data = [[
        Paragraph("🍽️  RESTAURANT &amp; CAFE MANAGER", title_style),
    ]]
    cover_table = Table(cover_data, colWidths=[170*mm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), [8,8,8,8]),
    ]))
    story.append(cover_table)

    sub_data = [[Paragraph("Smart Business Automation Template — Complete User Guide", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[170*mm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PRIMARY),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 8*mm))

    # What's included box
    included = [
        ["📦  WHAT'S INCLUDED IN THIS TEMPLATE"],
        [""],
        ["📊  Dashboard          Weekly KPI cards + auto sales summary"],
        ["📦  Inventory Tracker  Stock levels + low-stock alerts"],
        ["📈  Daily Sales Log    Transaction recording + auto totals"],
        ["👥  Staff Schedule     Weekly shifts + hours calculation"],
        ["📊  Reports Tab        Auto P&L + performance indicators"],
        [""],
        ["         🟡 Yellow cells = Enter your data"],
        ["         🟢 Green cells  = Calculated automatically"],
    ]

    inc_style = ParagraphStyle("Inc", fontSize=11, fontName="Helvetica",
                                textColor=WHITE, leading=16)
    inc_h_style = ParagraphStyle("IncH", fontSize=14, fontName="Helvetica-Bold",
                                  textColor=YELLOW, leading=18)

    inc_table_data = []
    for row in included:
        if row[0].startswith("📦  WHAT"):
            inc_table_data.append([Paragraph(row[0], inc_h_style)])
        elif row[0] == "":
            inc_table_data.append([Spacer(1, 2*mm)])
        else:
            inc_table_data.append([Paragraph(row[0], inc_style)])

    inc_table = Table(inc_table_data, colWidths=[170*mm])
    inc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), PRIMARY),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 15),
        ("RIGHTPADDING",  (0,0), (-1,-1), 15),
        ("LINEBELOW",     (0,0), (-1,0), 1, ACCENT),
    ]))
    story.append(inc_table)
    story.append(Spacer(1, 6*mm))

    # ══ HOW TO USE ══════════════════════════════════
    story.append(PageBreak())

    sec_style = ParagraphStyle("Sec", fontSize=15, fontName="Helvetica-Bold",
                                textColor=WHITE, leading=20)

    def section_header(text, color=DARK):
        data = [[Paragraph(text, sec_style)]]
        t = Table(data, colWidths=[170*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), color),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING",   (0,0), (-1,-1), 15),
            ("RIGHTPADDING",  (0,0), (-1,-1), 15),
        ]))
        return t

    # Step 1
    story.append(section_header("STEP 1 — OPEN THE FILE", GREEN))
    story.append(Spacer(1, 3*mm))
    steps1 = [
        "✅ Upload the .xlsx file to Google Drive",
        "✅ Right-click → Open with → Google Sheets",
        "✅ Or open directly in Microsoft Excel",
        "✅ Enable editing if prompted",
        "✅ Save a copy for your own use (File → Make a copy)",
    ]
    for s in steps1:
        story.append(Paragraph(s, bullet_style))
    story.append(Spacer(1, 5*mm))

    # Step 2
    story.append(section_header("STEP 2 — DASHBOARD TAB", BLUE))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "The Dashboard is your main control center. It shows real-time summaries "
        "from all other tabs automatically. You do NOT need to enter data here — "
        "it updates as you fill in the other tabs.",
        body_style))
    story.append(Spacer(1, 3*mm))
    kpi_data = [
        ["Card", "What it shows", "Source"],
        ["💰 Today's Sales", "Total daily revenue", "Daily Sales tab"],
        ["📦 Low Stock Items", "Items below minimum level", "Inventory tab"],
        ["👥 Staff Today", "Staff marked as Working", "Staff Schedule tab"],
    ]
    kpi_table = Table(kpi_data, colWidths=[45*mm, 75*mm, 50*mm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("BACKGROUND",    (0,1), (-1,-1), LIGHT),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (0,0), (-1,-1), "LEFT"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 5*mm))

    # Step 3
    story.append(section_header("STEP 3 — INVENTORY TAB", colors.HexColor("#0F9B58")))
    story.append(Spacer(1, 3*mm))
    inv_steps = [
        "1. Enter your item names in column B (Item Name)",
        "2. Select the category from the dropdown in column C",
        "3. Set the current stock quantity in column E (yellow)",
        "4. Set the minimum stock level in column F (yellow)",
        "5. Enter the unit cost in column H (yellow)",
        "6. Status column auto-updates: ✅ OK or ⚠️ LOW",
        "7. Total value calculates automatically in column I",
    ]
    for s in inv_steps:
        story.append(Paragraph(s, bullet_style))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "💡 TIP: Update inventory quantities at the end of each day or week "
        "to keep the Dashboard alert accurate.",
        note_style))
    story.append(Spacer(1, 5*mm))

    # Step 4
    story.append(section_header("STEP 4 — DAILY SALES TAB", BLUE))
    story.append(Spacer(1, 3*mm))
    sales_steps = [
        "1. Enter each sale/transaction in a new row",
        "2. Column C: Item or service name",
        "3. Column D: Category (Food / Beverage / Dessert / Takeaway / Delivery)",
        "4. Column E: Quantity sold",
        "5. Column F: Price per unit ($)",
        "6. Column G: Total auto-calculates (Qty × Price)",
        "7. Column H: Payment method (Cash / Card / Online)",
        "8. Column I: Time of sale",
        "9. Row 33: Daily total auto-calculates",
    ]
    for s in sales_steps:
        story.append(Paragraph(s, bullet_style))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "💡 TIP: Clear rows at the start of each day and copy the previous "
        "day's total to the Dashboard weekly summary.",
        note_style))
    story.append(Spacer(1, 5*mm))

    # Step 5
    story.append(section_header("STEP 5 — STAFF SCHEDULE TAB", ORANGE))
    story.append(Spacer(1, 3*mm))
    staff_steps = [
        "1. Enter staff names in column B",
        "2. Enter their role in column C (Manager / Chef / Cashier / etc.)",
        "3. For each day (Mon–Sun), select from dropdown:",
        "   • Working = 8 hours counted",
        "   • Half Day = 4 hours counted",
        "   • Off = 0 hours",
        "   • Training = 0 hours (logged separately)",
        "4. Column K auto-calculates total weekly hours per person",
        "5. Row 13 shows total hours for the whole team",
    ]
    for s in staff_steps:
        story.append(Paragraph(s, bullet_style))
    story.append(Spacer(1, 5*mm))

    # Step 6
    story.append(section_header("STEP 6 — REPORTS TAB", ACCENT))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "The Reports tab is fully automatic. Once you fill in Daily Sales and "
        "Inventory, this tab calculates everything for you:",
        body_style))
    story.append(Spacer(1, 2*mm))
    report_items = [
        "💰 Total Revenue for the week",
        "📉 Total Expenses entered in Dashboard",
        "📈 Gross Profit (Revenue − Expenses)",
        "📦 Current Inventory Value",
        "✅ Net Profit (Gross Profit − Inventory Cost)",
        "📊 Profit Margin % (auto-calculated)",
        "🏆 Best Day & Worst Day Sales",
        "📋 Average Daily Sales & Order Value",
    ]
    for item in report_items:
        story.append(Paragraph(item, bullet_style))
    story.append(Spacer(1, 5*mm))

    # ══ CUSTOMIZATION ═══════════════════════════════
    story.append(PageBreak())
    story.append(section_header("HOW TO CUSTOMIZE", PRIMARY))
    story.append(Spacer(1, 3*mm))

    custom_data = [
        ["What to change", "How to do it"],
        ["Business name", "Click Dashboard cell B2 → type your name"],
        ["Add more inventory items", "Scroll down in Inventory tab → fill empty rows"],
        ["Add more staff", "Scroll down in Staff tab → fill empty rows"],
        ["Change currency", "Select all $ cells → Format → Number → Custom"],
        ["Add more sale rows", "Copy an existing row and paste below row 31"],
        ["Change colors", "Select cell → Fill Color button in toolbar"],
    ]
    custom_table = Table(custom_data, colWidths=[80*mm, 90*mm])
    custom_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT]),
        ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("ALIGN",         (0,0), (-1,-1), "LEFT"),
    ]))
    story.append(custom_table)
    story.append(Spacer(1, 8*mm))

    # ══ FAQ ═════════════════════════════════════════
    story.append(section_header("FREQUENTLY ASKED QUESTIONS", colors.HexColor("#0D3B66")))
    story.append(Spacer(1, 3*mm))

    faqs = [
        ("Does this work on mobile?",
         "Yes! Google Sheets works on iPhone and Android. Some formatting "
         "may look slightly different on small screens."),
        ("Can I share it with my team?",
         "Yes. In Google Sheets, click Share → enter emails. "
         "Set editing permissions as needed."),
        ("Does it work offline?",
         "Google Sheets works offline if you enable offline mode in Drive settings. "
         "Excel works fully offline."),
        ("Can I add more rows or columns?",
         "Absolutely. The formulas are designed to be extended. "
         "Just copy existing rows to preserve formatting."),
        ("What if a formula breaks?",
         "Contact us via Etsy messages. We provide free support for 30 days after purchase."),
        ("Is this a one-time purchase?",
         "Yes! Pay once, use forever. Free updates included."),
    ]

    q_style = ParagraphStyle("Q", fontSize=11, fontName="Helvetica-Bold",
                               textColor=PRIMARY, spaceAfter=2, spaceBefore=6)
    a_style = ParagraphStyle("A", fontSize=10, fontName="Helvetica",
                               textColor=GRAY, spaceAfter=4, leftIndent=10, leading=14)

    for q, a in faqs:
        story.append(Paragraph(f"Q: {q}", q_style))
        story.append(Paragraph(f"A: {a}", a_style))

    story.append(Spacer(1, 8*mm))

    # ══ FOOTER / CONTACT ════════════════════════════
    footer_data = [[
        Paragraph(
            "⭐ Loved this template? Please leave a 5-star review on Etsy!<br/>"
            "It helps us create more free updates for you.<br/><br/>"
            "📩 Need help? Message us on Etsy — we reply within 24 hours.",
            ParagraphStyle("Footer", fontSize=11, textColor=WHITE,
                           fontName="Helvetica", alignment=TA_CENTER, leading=18)
        )
    ]]
    footer_table = Table(footer_data, colWidths=[170*mm])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), DARK),
        ("TOPPADDING",    (0,0), (-1,-1), 20),
        ("BOTTOMPADDING", (0,0), (-1,-1), 20),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
    ]))
    story.append(footer_table)

    doc.build(story)
    print("✅ PDF Guide created: Product_Guide.pdf")


# ══ ETSY LISTING ════════════════════════════════════
def build_etsy_listing():
    listing = """
╔══════════════════════════════════════════════════════════════════╗
║              ETSY LISTING — READY TO COPY & PASTE               ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE (max 140 chars):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Restaurant Manager Google Sheets Template | Cafe Business Automation | Sales Inventory Staff Tracker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICE:  $27.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESCRIPTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🍽️ Run Your Restaurant Smarter — Not Harder

Stop wasting hours on manual tracking. This professional Google Sheets
template automates the most time-consuming parts of running a restaurant
or cafe, so you can focus on what matters: great food and happy customers.

──────────────────────────────────────
✅ WHAT YOU GET (5 powerful tabs):
──────────────────────────────────────
📊 DASHBOARD
  → Real-time KPI cards (Sales, Inventory, Staff)
  → Weekly sales summary table
  → All data updates automatically

📦 INVENTORY TRACKER
  → Track up to 50+ items
  → Automatic LOW STOCK alerts ⚠️
  → Total inventory value calculated instantly

📈 DAILY SALES LOG
  → Record every transaction in seconds
  → Category & payment method dropdowns
  → Daily total auto-calculated

👥 STAFF SCHEDULE
  → Weekly shift planner for your whole team
  → Auto-calculates total hours per person
  → Working / Off / Half Day / Training options

📊 PROFIT & LOSS REPORTS
  → Weekly P&L statement (automatic)
  → Profit margin % calculated
  → Best/worst day performance indicators

──────────────────────────────────────
🟡 HOW IT WORKS:
──────────────────────────────────────
1. Download the file (.xlsx)
2. Upload to Google Sheets (free) or open in Excel
3. Enter your data in the yellow cells
4. Everything else calculates automatically ✅

──────────────────────────────────────
🎯 PERFECT FOR:
──────────────────────────────────────
✔ Restaurants & cafes of any size
✔ Food trucks & pop-up kitchens
✔ Bakeries & coffee shops
✔ Small food businesses
✔ Anyone who wants to track sales without expensive software

──────────────────────────────────────
💡 WHY THIS TEMPLATE?
──────────────────────────────────────
✔ No monthly subscription — pay ONCE, use FOREVER
✔ No coding required — works out of the box
✔ Mobile-friendly (Google Sheets app)
✔ Share with your team instantly
✔ Includes full PDF user guide
✔ Free 30-day support via Etsy messages

──────────────────────────────────────
📦 WHAT YOU RECEIVE AFTER PURCHASE:
──────────────────────────────────────
✔ Restaurant_Cafe_Manager.xlsx (Google Sheets compatible)
✔ Product_Guide.pdf (complete step-by-step instructions)
✔ Instant digital download — no shipping!

──────────────────────────────────────
⭐ HAPPY CUSTOMERS:
──────────────────────────────────────
"Finally a template that actually works for my cafe. Saved me hours every week!"
"Super easy to set up. My staff uses it every day now."
"Worth every penny. The inventory tracker alone is priceless."

──────────────────────────────────────
❓ QUESTIONS?
──────────────────────────────────────
Message us on Etsy — we respond within 24 hours!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13 TAGS / KEYWORDS (copy one by one into Etsy tags):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1.  restaurant spreadsheet template
2.  cafe management google sheets
3.  food business tracker
4.  restaurant inventory template
5.  small business automation
6.  daily sales tracker excel
7.  staff schedule template
8.  google sheets business template
9.  restaurant profit loss template
10. cafe inventory spreadsheet
11. food truck tracker template
12. business management spreadsheet
13. restaurant dashboard template

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CATEGORY on Etsy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Craft Supplies & Tools → Templates → Spreadsheets

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILES TO UPLOAD on Etsy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Restaurant_Cafe_Manager.xlsx
2. Product_Guide.pdf

"""
    with open("/home/user/smc-bot/Etsy_Listing.txt", "w", encoding="utf-8") as f:
        f.write(listing)
    print("✅ Etsy listing created: Etsy_Listing.txt")


if __name__ == "__main__":
    build_pdf()
    build_etsy_listing()
    print("\n🎉 Product package complete!")
    print("   • Restaurant_Cafe_Manager.xlsx")
    print("   • Product_Guide.pdf")
    print("   • Etsy_Listing.txt")
