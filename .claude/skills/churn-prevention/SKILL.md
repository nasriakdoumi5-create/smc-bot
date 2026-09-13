---
name: churn-prevention
description: Reduce cancellations and recover lapsed subscribers. Given manual billing and a $45/mo price, this outranks acquisition work whenever both are on the table.
---

# churn-prevention

Read `product-marketing` first.

## Why this comes first

A subscriber who leaves in month two, after manual TradingView provisioning
and a hand-made Telegram invite, was a net loss. Acquisition is expensive and
policy-constrained (`ads`); retention is entirely within our control.

## The four churn causes, in order

**1. Involuntary — the renewal simply lapsed.**
Manual billing means a subscriber who meant to stay can vanish because an
invite link expired. This is the largest and most fixable bucket.
Fix: T-5 renewal notice, T-3 expiry warning, T+1 and T+7 recovery messages
(`emails`). Never let access lapse silently.

**2. Never activated.**
They joined, did not understand the payload, never took a signal.
Fix: `onboarding`, specifically the payload guide and the first-alert
follow-up. Watch for subscribers who never reply and never react — that
silence is the highest-precision churn signal we have.

**3. Expectation mismatch.**
They expected 20 signals a day and got 4, or expected every one to win.
Fix: set expectations *down* at signup (`copywriting`, `onboarding`). Most of
this churn was created by the sales copy, not the product.

**4. Drawdown.**
A losing week. Unavoidable, and the real test.
Fix: be *more* present in a bad week, not less. The weekly recap with losses
included (`emails`) is the retention mechanism — subscribers churn from
silence during drawdown far more than from the drawdown itself.

## Early warning signals

| Signal | Meaning | Action |
|---|---|---|
| No channel reactions in 10 days | Disengaged | Personal message, ask what is missing |
| Never replied during onboarding | Not activated | Payload walkthrough offer |
| Asked about cancelling | Decided | Ask why, do not pitch |
| Renewal 3 days out, no response | Involuntary risk | Direct message, make renewing one step |

## The cancellation conversation

- Make cancelling easy and say so publicly (`cro` — it raises conversion).
- One question only: "What would have had to be different?" Log every answer
  into `customer-research`. Cancellation interviews are the highest-signal
  research we get.
- No retention discount on first attempt. Discounting to save a mismatched
  subscriber buys one month and a worse refund conversation.
- Leave the door open, remove access cleanly, keep them on the free list.

## Win-back

At 30 and 90 days, one message each, with new information: what the system
has changed, or a notable session they missed. Never a "we miss you" email.

## Cross-references

- `onboarding` — where most churn is actually prevented.
- `emails` — renewal and win-back mechanics.
- `analytics` — the churn and SLA numbers.
- `customer-research` — exit interviews feed everything.
