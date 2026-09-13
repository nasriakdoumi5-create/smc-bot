---
name: onboarding
description: Get a new subscriber to their first real value fast — first alert received, understood, and acted on. Use when designing welcome sequences or when early churn is high.
---

# onboarding

Read `product-marketing` first.

## The activation moment

Not "joined the channel". Activation is: **the subscriber receives an alert,
understands every field in it, and takes the trade with correct sizing.**
Until that happens they are paying for something they have not used, and they
will cancel in week three.

Time-to-activation target: within the first session after access is granted.

## The first 48 hours

**Immediately on access:**
- Both access confirmations in one message: TradingView granted + Telegram
  invite link, with the link's expiry stated.
- A one-screen "read this first" covering the alert payload:
  `s` symbol, `t` direction, `p` entry, `sl` stop, `tp1`/`tp2` targets,
  `r` risk in points, `v` VWAP reference, `src` trigger source.
  Every field, one line each. This is the single highest-value asset in
  onboarding — most cancellations trace to alerts that were never understood.
- Session times in *their* timezone, not UTC. Ask at signup or offer both.

**Before the first session:**
- "Signals fire only 07:00–11:00 and 13:30–17:00 UTC. Silence outside those
  windows is the system working." Unmanaged silence reads as a broken product
  and generates most week-one support load.

**After the first alert:**
- A short follow-up: did it arrive, was it clear, did you take it? This single
  message is the best churn predictor we have (`churn-prevention`).

**Day 7:**
- Show the week's flagged setups including the losers, with the star ratings.
  Reinforces that the feed is unedited.

## Design rules

- Teach the system, not trading. They know how to trade. They do not know how
  *our* ratings map to their sizing.
- One concept per message. Six short messages beat one manual nobody reads.
- Every message ends with a reply-able question. Replies are the retention
  signal and the research source (`customer-research`).
- Set expectations *down*: typical signal counts per day, and the fact that
  some sessions produce nothing.

## Cross-references

- `signup-flow` — hands off to here.
- `churn-prevention` — weak activation is the root cause it keeps finding.
- `emails` — the sequence mechanics.
- `community` — where activated users should land.
