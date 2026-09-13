---
name: analytics
description: Define what to measure, instrument it, and build the small set of numbers that actually drive decisions here. Use before any campaign, and when a question cannot be answered from existing data.
---

# analytics

Read `product-marketing` first.

## The numbers that matter

At 20-subscriber scale, dashboards are a distraction. Five numbers run this
business:

1. **Active paid subscribers** — the only real scoreboard.
2. **Monthly churn** — at $45/mo with manual fulfillment, this dominates
   everything (`product-marketing`).
3. **Free-list size and growth** — the leading indicator of #1.
4. **Signal quality delivered** — flagged setups per session, star
   distribution, outcome distribution. This is a *marketing* metric: it is
   the input to every proof asset we publish.
5. **Time from payment to access granted** — the fulfillment SLA
   (`signup-flow`, `revops`). Directly predicts early churn.

Anything else is secondary until these are tracked reliably.

## Instrumentation

**Site**: a privacy-respecting analytics tool (Plausible/Umami-class) is
sufficient and avoids the consent-banner friction that hurts `cro`. Track:
pageviews, the CTA click, signup start, payment complete.

**Attribution**: UTM on every external link we control, consistently:
`?utm_source=twitter&utm_medium=social&utm_campaign=killzone-thread`.
Inconsistent UTMs are the most common reason a channel looks like it produces
nothing.

**Subscribers**: a single source of truth for who is paid, when they renew,
and which channel they came from. A spreadsheet is fine at this scale — see
`revops`. What is not fine is having it only in Telegram's member list.

**Signals**: `bot.js` already counts signals; `market_memory.js` holds state.
Persist per-signal outcomes so weekly recaps (`emails`, `video`) can be
generated rather than reconstructed by hand.

## Attribution honesty

Most acquisition here will be dark: a Telegram forward, a Discord mention, a
word-of-mouth referral. Expect 40%+ "direct". Do not over-invest in tracking
what is untrackable — instead **ask at signup**: "How did you find us?" One
optional field beats an attribution stack at this scale.

## Reporting cadence

Weekly: the five numbers, one line each, no commentary. Monthly: channel
review, test log (`ab-testing`), and one decision. A report that does not end
in a decision should not be produced.

## Cross-references

- `ab-testing` — depends entirely on this instrumentation.
- `revops` — the subscriber source of truth.
- `churn-prevention` — consumes the churn and SLA numbers.
- `ads` — no spend before attribution exists.
