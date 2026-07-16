# I Tried 6 Budgeting Apps. A Google Sheet Beat Them All.

*How a 3-tab spreadsheet finally fixed my finances — and the exact structure so you can build it yourself.*

---

Over the last three years I tried YNAB, Mint, PocketGuard, two banking-app budgets, and a bullet journal. Every single one died within a month.

Not because they were bad — because they were *too much*. Categories I didn't need, sync that broke, subscriptions that quietly renewed while I wasn't even opening the app. I was paying €10/month to feel guilty.

So I went back to the most boring tool on earth: a spreadsheet. And it stuck. Eighteen months now, logged every week.

Here's the exact structure, so you can build it in an afternoon.

## The 3-Tab Rule

The reason budgets fail is friction. Every extra field, every extra screen, every extra decision is a reason to quit. So the system is three tabs, nothing more:

### Tab 1 — Income
Four columns: **Date | Amount | Source | Notes**

The Source column is a dropdown (Salary, Freelance, Side Hustle, Other). Dropdowns matter more than they seem — they keep data consistent, which is what makes the dashboard work later.

### Tab 2 — Expenses
Five columns: **Date | Item | Category | Amount | Notes**

Category is a dropdown too: Housing, Food, Transport, Health, Fun, Shopping, Bills, Other. Eight categories, no more. If you have twenty categories, you'll spend more time categorizing than saving.

### Tab 3 — Dashboard (the one you never touch)
This tab is pure formulas. Three numbers at the top:

**This month's income:**
```
=SUMPRODUCT((TEXT(Income!A2:A500,"yyyy-mm")=TEXT(TODAY(),"yyyy-mm"))*Income!B2:B500)
```

**This month's spending:**
```
=SUMPRODUCT((TEXT(Expenses!A2:A500,"yyyy-mm")=TEXT(TODAY(),"yyyy-mm"))*Expenses!D2:D500)
```

**What's left:** just subtract the two.

The `TEXT(TODAY(),"yyyy-mm")` trick is the whole secret — the dashboard always shows *the current month* automatically. You never update anything. You just log expenses and look.

Below that, spending by category:
```
=SUMIFS(Expenses!D2:D500, Expenses!C2:C500, "Food")
```
One line per category. Add a bar chart if you want to feel fancy.

## The Two Rules That Make It Stick

The spreadsheet is 20% of the system. These rules are the other 80%:

**1. Log same-day, on your phone.** The Google Sheets app takes 10 seconds: date, item, category, amount. If you batch it for the weekend, you'll forget half of it and quit by week three.

**2. Sunday review, 2 minutes.** Open the dashboard once a week. Look at three numbers. That's it. The point isn't control — it's *seeing*. In my first month, just seeing the numbers surfaced €140/month in subscriptions I'd forgotten about.

## Why a Spreadsheet Beats an App (For Most People)

- **You own it.** No company shutting down, no price increase, no "premium tier".
- **Zero learning curve.** You already know how spreadsheets work.
- **It works everywhere.** Phone, tablet, laptop — Google Sheets is free on all of them.
- **It's honest.** An app gamifies your money. A spreadsheet just shows it to you.

## Build It or Grab It

Everything above is enough to build the whole system yourself — genuinely, it's an afternoon of work, and you'll understand every formula in it.

If you'd rather skip the afternoon: I turned this exact system into a ready-made template — plus 115 other Google Sheets tools (invoices, meal planning, habit tracking, business dashboards) — at [nasritools.etsy.com](https://nasritools.etsy.com). Everything is buy-once-own-forever, because good tools don't expire.

Either way: start logging tomorrow morning. The first forgotten subscription you find pays for the whole experiment.
