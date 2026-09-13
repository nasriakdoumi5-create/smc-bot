---
name: pricing
description: Set and change prices, structure plans and bundles, and hold the discount line. The source of truth for every price stated anywhere. Use before any copy quotes a number.
---

# pricing

Read `product-marketing` first.

## Current structure (source of truth)

| Plan | Price | Contents |
|---|---|---|
| VWAP Bounce Pro | $15/mo | Indicator access |
| Kill Zone Sweep Pro | $20/mo | Indicator access |
| Indicator bundle | $30/mo | Both indicators |
| Signals channel | $20/mo | Private Telegram alerts |
| **Full package** | **$45/mo** | Both indicators + channel |

Any price appearing on a page, in an email, or in `schema` markup must match
this table. A mismatch between markup and page is a violation (`schema`), and
a mismatch between page and invoice is a refund.

## Structural notes

- The full package at $45 is the intended default — pre-select it
  (`signup-flow`). The standalone plans exist to make it look correct, and
  the indicator bundle at $30 anchors the $15 gap to the full package.
- The $20 channel-only plan is the weak point: it is the highest-support,
  lowest-margin option and the one most likely to churn (no chart tooling
  means less activation, see `churn-prevention`). Consider retiring it or
  raising it to $25 once there is enough data.

## Unit economics

Fixed costs are ~$20/mo (Railway ~$5, TradingView ~$15). Marginal cost per
subscriber is near zero in compute and ~10 minutes of manual work
(`revops`). This means:

- Break-even is one subscriber.
- The binding constraint is **operator time, not money** — which argues for
  raising price rather than volume as the growth lever.
- CAC ceiling: at $45/mo and a target of 3-month payback, do not exceed ~$135
  fully-loaded acquisition cost, and be far under it while churn is unproven
  (`ads`).

## Discount policy

There isn't one. No launch discounts, no "first month $1", no retention
discounts on a first cancellation attempt (`churn-prevention`). Reasons:

- In this niche, discounting signals desperation and invites scam comparison.
- Discounted subscribers churn faster and refund more.
- Manual fulfillment means a discounted subscriber can be genuinely
  unprofitable in operator time.

Exceptions, both structural rather than promotional: annual prepay at 10
months for 12 (improves cash and retention), and partner bundle rates agreed
per deal (`co-marketing`).

## Raising prices

The upgrade path from $45 is not a higher number alone — it is bot-as-a-service
and partner deals, which are priced per engagement. When raising subscription
prices: grandfather existing subscribers for at least 6 months, tell them
first (`launch`), and state the reason in one sentence without apology.

## Cross-references

- `paywalls` — what sits on each side of the line.
- `signup-flow` — plan presentation and defaults.
- `sales-enablement` — the "it's expensive" objection.
- `schema` — Offer markup must mirror this table.
