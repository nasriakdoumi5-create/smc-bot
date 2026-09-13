---
name: signup-flow
description: Design and debug the path from intent to paid access — form fields, payment, and provisioning. Use when signups start but do not finish, or when building the flow for the first time.
---

# signup-flow

Read `product-marketing` first, especially the note that fulfillment is manual.

## Our actual flow

```
Landing → Choose plan → Pay (PayPal / USDT) → Collect TradingView username
        → Manual: grant script access + generate 30-day Telegram invite
        → Deliver credentials → Onboarding (see onboarding)
```

The manual middle is the weak point. Every hour between payment and access is
an hour the buyer spends wondering if they were scammed.

## Rules for this flow

- **Collect the TradingView username at checkout, not after.** Asking after
  payment adds a round trip and it is the field most likely to be wrong.
  Validate the format at entry; a wrong username is the #1 provisioning delay.
- **Set the expectation in writing on the confirmation screen**: "Access is
  granted manually within X hours." Then beat X. A promised delay is fine; an
  unexplained one is not.
- **Automate what the delay allows.** Send an immediate confirmation email
  containing what happens next, the risk disclosure, and a link to the
  getting-started guide, so the wait is occupied.
- **One plan pre-selected** — the $45 full package, per `pricing`. A flow that
  opens with an unselected 4-way choice converts worse than one that opens
  with a recommended option.
- Email is the only field before payment. Everything else is post-intent.

## Payment reality

PayPal and USDT both carry friction for this audience: PayPal risks account
review for "signals" descriptions (use a neutral product descriptor —
"software subscription"); USDT filters out non-crypto-native buyers. Offer
both, default to whichever `analytics` shows converting, and never make the
buyer ask how to pay.

## Failure states to design for

- Payment succeeded, username missing → automated follow-up within 1 hour.
- Username invalid → one clear email, not silence.
- Renewal lapsed → see `churn-prevention`; the invite link expiring without
  warning is the worst possible last impression.

## Instrumentation

Track each step as a distinct event (`analytics`). Without step-level events
you cannot tell a pricing problem from a payment problem.

## Cross-references

- `cro` — the diagnosis that sends you here.
- `onboarding` — what happens after access is granted.
- `revops` — the manual provisioning queue and its SLA.
- `pricing` — plan presentation and defaults.
