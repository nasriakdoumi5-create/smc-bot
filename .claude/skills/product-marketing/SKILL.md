---
name: product-marketing
description: Root marketing context for this product — who we sell to, what we sell, what we may and may not claim, and the house voice. Every other marketing skill in .claude/skills/ reads this FIRST, before doing its own job. Use whenever writing copy, planning a campaign, pricing, or building a landing page for SMC Bot.
---

# product-marketing (read first)

Every marketing skill in this repo depends on this file. Read it before doing
anything else, then return to the skill that was invoked.

## What we sell

Three products, one audience:

| Product | What it is | Price |
|---|---|---|
| VWAP Bounce Pro | Invite-only TradingView indicator — mean-reversion off VWAP ±1.5 ATR with RSI + rejection-candle confirmation | $15/mo |
| Kill Zone Sweep Pro | Invite-only TradingView indicator — liquidity sweeps of PDH/PDL, Asia H/L, swing H/L during London/NY kill zones | $20/mo |
| Signals Channel | Private Telegram channel fed by the bot's webhook (entry, SL, TP1/TP2, R) | $20/mo |

Bundles: both indicators $30/mo; full package (indicators + channel) $45/mo.
Delivery is `bot.js` → Railway webhook → Telegram. Access is managed by hand:
TradingView *Manage Access* per user, timed Telegram invite links per month.

Break-even is ~1 subscriber. Target from `BUSINESS_SETUP.md` is 20 subscribers
(~$880/mo net). **That number sets the strategy: this is a small, high-intent,
retention-driven business, not a volume funnel.** Twenty right people beat
twenty thousand impressions. Skills that optimize for reach over fit are
being misapplied.

## Who we sell to

Primary ICP — the *semi-serious retail futures trader*:

- Trades MNQ/NQ, sometimes ES/MES, on the 5-minute chart.
- Funded-account holder or working toward one (Topstep, Apex, FTMO-style).
  Their real fear is **breaching a drawdown rule**, not missing a winner.
- Already pays for TradingView (Essential+) — they can use invite-only scripts.
- Fluent in SMC/ICT vocabulary: liquidity sweep, kill zone, PDH/PDL, OTE, FVG.
- Sits in London KZ (07:00–11:00 UTC) or NY KZ (13:30–17:00 UTC).
- Bilingual market: Arabic-first and English-first traders both convert. Write
  the *same* offer in both; do not machine-translate one into the other.

Secondary: bot-as-a-service buyers — traders who want their own Pine strategy
wired to their own Telegram channel. Higher ticket, one-off, low volume.

Not our buyer: crypto-only traders, investors, anyone who needs to be taught
what a candle is. Educating a beginner costs more than they pay.

## Positioning

> Institutional-grade entry logic, mechanically enforced, on the two sessions
> that actually matter.

What makes the product different, in order of persuasive strength:

1. **Session-gated by design.** The system refuses to fire outside London/NY
   kill zones. Competitors fire all day and let the trader sort it out.
2. **The alert is a complete trade.** JSON with entry, SL, TP1, TP2 and R —
   not "long NQ 🚀". Nothing is left to the subscriber's discretion.
3. **Quality is graded, not implied.** Kill Zone Sweep Pro rates 1–3 stars by
   confluence (PDH/PDL sweep 3 pts > Asia H/L 2 > swing H/L 1).
4. **Same engine, two surfaces.** The indicator on their chart and the channel
   alert come from one codebase, so they never disagree.

Lead with #1 and #2. They are verifiable from a screenshot in ten seconds.

## Claim rules — non-negotiable

Trading products live under real rules, and TradingView/Meta/Google enforce
them harder than most categories. These override any persuasive instinct in
any other skill:

- **Never** state or imply guaranteed profit, "risk-free", income replacement,
  or a specific dollar/percent return a subscriber will earn.
- **Never** publish a win rate, average R, or equity curve you cannot produce
  from `backtest_*.mjs` output on a named symbol, timeframe and date range.
  If you cite a number, cite the range with it.
- Backtested/hypothetical results are labeled **hypothetical**, every time,
  in the same visual weight as the number itself.
- Every public asset carries a risk line. Standard short form:
  *Futures trading involves substantial risk of loss and is not suitable for
  every investor. Hypothetical results are not indicative of future results.*
- No testimonial implying typical results without the disclaimer beside it.
- We sell **signals and tooling**, never advice, never managed money. Phrase
  as "the system flags", never "you should buy".
- TradingView script descriptions: no external links, no price, no contact
  details, no promotional language in the script description itself — that
  gets scripts removed. Sell in the profile/signature, describe in the script.

If a piece of copy needs a claim you cannot support, the answer is to change
the copy, not to soften the disclaimer.

## House voice

- Flat, technical, unhyped. The audience is allergic to hype because every
  scammer they have met used it.
- Short declaratives. Numbers over adjectives. "3-point confluence" beats
  "extremely powerful".
- No rocket/money emoji. The bot's own output uses at most one status glyph.
- Arabic copy is written natively, in the same flat register — not a
  translated English pitch.
- Screenshots > prose. A chart with the marked sweep does more than a
  paragraph about sweeps.
- Admit the losses. Posting a stopped-out trade converts better here than
  posting a tenth winner, because it proves the feed is unedited.

## Proof assets we actually have

Know what exists before promising proof in a campaign:

- `backtest_fib.mjs`, `backtest_ict.mjs`, `backtest_sweep.mjs`,
  `backtest_new_strategy.mjs` — runnable backtests over `data/es_5m.json`,
  `data/nq_5m.json` (and 1h equivalents).
- `indicator_vwap_bounce.pine`, `strategy_tradingview.pine` — the published
  scripts; their descriptions are marketing surface.
- Live channel history — the strongest asset we have, and it costs nothing.
- `chart_vision.js` / `/vision` — live chart capture, useful for generating
  annotated screenshots at scale.

## The skill map

```
product-marketing (this file)
├── SEO & Content ...... seo-audit, ai-seo, site-architecture,
│                        programmatic-seo, schema, content, aso
├── CRO ................ cro, signup-flow, onboarding, popups, paywalls
├── Content & Copy ..... copywriting, copy-edit, cold-email, emails,
│                        social, video, image, sms
├── Paid & Measurement . ads, ad-creative, ab-testing, analytics
├── Growth & Retention . referrals, free-tools, churn-prevention,
│                        community, lead-magnets, co-marketing
├── Sales & GTM ........ revops, sales-enablement, launch, pricing,
│                        competitors, competitor-profile, directory,
│                        prospecting
└── Strategy ........... marketing-ideas, marketing-psychology,
                         customer-research
```

Cross-references that matter most:

- `copywriting` ↔ `cro` ↔ `ab-testing` — never write, test or ship one alone.
- `revops` ↔ `sales-enablement` ↔ `cold-email` — one pipeline, three views.
- `seo-audit` ↔ `schema` ↔ `ai-seo` — one crawl surface, three lenses.
- `customer-research` → `copywriting`, `cro`, `competitors` — research feeds
  all three; do it first when any of them feels like guesswork.

## Where the business constraints bite

Before recommending a tactic, check it against reality:

- **Paid ads are mostly closed to us.** Meta and Google restrict financial
  products; "signals" copy gets accounts banned. Assume organic + community
  until `ads` says otherwise with a compliant angle.
- **Fulfillment is manual.** Every new subscriber is a TradingView access
  grant and a Telegram invite by hand. A campaign that lands 200 signups in a
  day breaks fulfillment. Growth should be paced to what `revops` can serve.
- **Churn is the whole game.** At $45/mo with manual onboarding, a subscriber
  who leaves in month two was a net loss. Retention work outranks acquisition
  work whenever both are on the table.
