# NasriTools — Etsy Store

Digital products shop selling Google Sheets / Excel templates.
Owner: Nasri (replies in Arabic — Moroccan/Levantine mix, often Latin script).

- Shop: **https://nasritools.etsy.com** · shop_id `66526082`
- Positioning: *"Buy once, own forever"* — no subscriptions, no sign-ups.
- Repo branch: `claude/digital-products-knowledge-yzpw50`

---

## Current state (Aug 2026)

7 premium products, all live. The old 121-listing catalogue was **deleted
on purpose** — the strategy changed from many cheap products to few
high-value ones.

| Product | Price | File |
|---|---|---|
| Options Trading Journal | $19.99 | `PREMIUM_Trading_Journal.xlsx` |
| Business KPI Dashboard | $19.99 | `PREMIUM_Business_KPI.xlsx` |
| Invoice & Client Tracker | $14.99 | `PREMIUM_Invoice_Client.xlsx` |
| Monthly Budget Tracker | $12.99 | `PREMIUM_Budget_Tracker.xlsx` |
| Habit Tracker | $12.99 | `PREMIUM_Habit_Tracker.xlsx` |
| Student Planner + GPA | $12.99 | `PREMIUM_Student_Planner.xlsx` |
| Meal Planner + Grocery | $12.99 | `PREMIUM_Meal_Planner.xlsx` |

Published listing IDs live in `premium_published.json`.

**Still pending (manual, Etsy has no API for these):**
- Shop icon → `logos/logo_falling.png`
- Big banner → `nasritools-banner.png`
- Both at: Shop Manager → Settings → Info & Appearance

---

## Daily driver

```bash
python store_agent.py          # full report: health + stats + next steps
python store_agent.py health   # billing/suspension risk only
```

Run it before anything else — it surfaces problems early.

---

## Scripts that matter

| Script | Does |
|---|---|
| `store_agent.py` | Read-only health + stats + plan report |
| `etsy_reauth.py` | Fresh OAuth token → `~/etsy_token.json` |
| `publish_premium.py` | Publishes products from `DIGITAL_PRODUCTS/` |
| `delete_all_listings.py` | Wipes the catalogue (types `DELETE ALL` to confirm) |
| `set_api_keys.py` | Swaps API credentials across every script at once |
| `verify_final.py` | Reads live data back to prove changes landed |

Everything else in the repo root is from earlier bulk-edit campaigns on the
old catalogue — mostly obsolete now.

---

## Product assets

```
DIGITAL_PRODUCTS/
├── files/           7 xlsx · 17 png · 7 mp4 demo videos
└── content/
    ├── listings.json      ← source of truth: title, tags, price, description
    └── صفحة_النسخ.html    ← copy-paste page for manual publishing
```

Paths inside `listings.json` are stale (from another machine) — the
publisher resolves assets **by filename** against `DIGITAL_PRODUCTS/files/`.

`marketing/launch_pack.md` holds ready Reddit / TikTok / X / Medium content.
`pins/` holds 3 Pinterest pins + captions.

---

## Hard-won gotchas

**Etsy title rules.** Each of `& % : ; @` may appear **once**. Five listings
failed with `too_many_invalid_characters` before `clean_title()` was added to
`publish_premium.py`. Reuse that function for any new publisher.

**Price updates need the inventory endpoint.** `PATCH /listings/{id}` accepts a
`price` field, returns 200, and silently ignores it. Use
`PUT /listings/{id}/inventory` with a rebuilt payload (writable fields only,
price as a plain float). See git history of `update_prices.py`.

**`x-api-key` must be `CLIENT_ID:SECRET`.** Just the client id returns
`403 Shared secret is required`.

**The shop was suspended once** — unpaid listing fees (121 listings ×
$0.20 ≈ $25 with almost no sales). Everything went dark: API 403,
"application not recognized", listings deactivated. Paying the invoice
restored it automatically. `store_agent.py health` now watches the balance so
it cannot happen silently again.

**Etsy has no API for shop icon, banner, or About text.** Always manual.

---

## Working with Nasri

- Reply in Arabic. Keep it short, with concrete next steps.
- He runs commands on **his own Windows PC** (`C:\Users\nasri\smc-bot`) —
  this cloud container has no Etsy network access and no `~/etsy_token.json`.
- **Pasting into his PowerShell duplicates the text.** Give one short command
  per block and tell him to type it manually when it matters.
- Verify claims against live Etsy data before saying something worked —
  he has been burned by scripts that printed ✓ while changing nothing.
