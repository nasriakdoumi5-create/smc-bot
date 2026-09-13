---
name: cro
description: Improve conversion rate on a page or flow — diagnose where visitors drop, form a hypothesis, and specify the change. Use for landing pages, pricing pages, and checkout. The hub skill for signup-flow, popups, paywalls, and ab-testing.
---

# cro

Read `product-marketing` first.

## Diagnose before you optimize

Never change a page because it "feels weak". Find the drop first:

1. Pull the funnel from `analytics`: view → CTA click → signup start →
   payment → access granted.
2. Find the step with the worst relative drop, not the smallest absolute
   number.
3. Watch 10 session recordings of people who dropped at that step.
4. Read 10 support/DM messages from the same week. The objection is usually
   already written down in the user's own words — use it verbatim
   (`customer-research`).

## The conversion equation

Conversion rises when **motivation** and **clarity** rise, and **friction**
and **anxiety** fall. For this product, anxiety is the dominant term. The ICP
has been scammed before. Every scam-adjacent signal costs more than a bad
headline does.

Anxiety reducers that actually move numbers here:

- Unedited signal history, losses included.
- Exact fulfillment mechanics stated up front: "you get a TradingView access
  grant within 12 hours and a Telegram invite link valid for 30 days."
- Named cancellation policy. Manual billing makes people fear they cannot get
  out; say how they get out.
- No countdown timers, no fake scarcity, no "only 3 spots". Our audience
  reads those as scam markers — this is the rare case where a classic CRO
  tactic is net negative.
- Risk disclosure visible, not buried. Counter-intuitively it *raises*
  conversion here: scammers never include it.

## Page structure that works

1. Headline: mechanism + instrument + session. Not a benefit promise.
2. One annotated chart showing a real flagged setup.
3. What you get — three bullets, concrete deliverables.
4. How it works — 3 steps, ending in "alerts arrive in Telegram".
5. Proof — signal history link, backtest range, honest stats.
6. Pricing, from `pricing`, with the bundle anchored.
7. FAQ answering the top 5 objections from `customer-research`.
8. Single CTA, repeated, identical wording every time.

## Friction audit

- How many fields to start? Email only until payment.
- How many clicks from landing to payment? Target ≤ 3.
- Is the price visible without clicking? It must be.
- Does the page work at 390px during a live session? Test it.

## Rules

- One variable per test (`ab-testing`).
- Never test into a smaller idea. Test the offer and the headline before the
  button color.
- Ship the fix for anything that is plainly broken; do not A/B test a bug.

## Cross-references

- `copywriting` ↔ `cro` ↔ `ab-testing` — the core loop.
- `signup-flow`, `popups`, `paywalls` — specific surfaces.
- `customer-research` — the source of every good hypothesis.
