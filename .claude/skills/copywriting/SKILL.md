---
name: copywriting
description: Write headlines, landing page copy, CTAs, and product descriptions in the house voice and within the claim rules. The most-used skill here; pairs with cro and ab-testing.
---

# copywriting

Read `product-marketing` first — the voice and claim rules there are binding,
not advisory.

## Before writing a word

You need three inputs. If you lack them, get them from `customer-research`
rather than inventing them:

1. The **objection** this copy must answer.
2. The **mechanism** that answers it (something the product actually does).
3. The **proof** that the mechanism is real (a backtest range, a chart, a
   channel history link).

Copy without all three becomes adjectives, and adjectives are what our
audience filters out.

## Headline patterns that work here

Mechanism-first. The headline's job is to prove we know the domain in seven
words, filtering out everyone who does not belong.

- `Liquidity sweeps of PDH/PDL, flagged inside the kill zone.`
- `Every alert is a full trade: entry, stop, TP1, TP2, R.`
- `It refuses to fire outside London and New York.`
- `The same engine on your chart and in your Telegram.`

Patterns that fail here: profit promises, "finally", "secret", any
transformation narrative, any emoji-led hook.

## CTA rules

- Describe the next literal step: `Get access — $45/mo`, not `Start now`.
- Price in the CTA whenever there is a price. Removing it does not increase
  clicks, it increases bad clicks and refund requests.
- One CTA wording per page, repeated verbatim (`cro`).

## Specificity conversion table

| Weak | Strong |
|---|---|
| High-probability setups | 3-point confluence: PDH/PDL sweep + kill zone + rejection |
| Fast alerts | JSON webhook → Telegram, sub-second from bar close |
| Proven system | 18 months of NQ 5m data, hypothetical, range stated |
| Works great | 5–10 signals/day on MNQ 5m |

Always move right. The right column is also what `ai-seo` extracts and what
`schema` can mark up.

## Claim self-check before shipping

- [ ] No guaranteed or implied return.
- [ ] Every number traceable to a backtest run or live history.
- [ ] Hypothetical results labeled as such, same visual weight.
- [ ] Risk disclosure present on the asset.
- [ ] No advice framing — "the system flags", not "you should buy".
- [ ] If TradingView-bound, no links/price/promo in the script description
      (`aso`).

## Cross-references

- `cro` ↔ `copywriting` ↔ `ab-testing` — write, test, iterate as one loop.
- `copy-edit` — everything ships through it.
- `marketing-psychology` — why these patterns work on this audience.
- `customer-research` — the source of the objection and the words for it.
