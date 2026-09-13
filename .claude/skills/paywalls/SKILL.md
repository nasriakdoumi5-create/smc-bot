---
name: paywalls
description: Decide what is free, what is gated, and how the boundary is presented. Use when designing the free/paid line for signals, indicators, or content.
---

# paywalls

Read `product-marketing` first.

## The core trade

Free content builds the trust this category requires. Gated content produces
revenue. The boundary should be drawn so that the free side *proves* the paid
side rather than substituting for it.

## Where the line goes

**Free, always:**
- All `/learn/` education. Concepts are not the product.
- Free tools (kill-zone clock, position size calculator) — `free-tools`.
- Delayed signal history. Yesterday's flagged setups, with outcomes, posted
  publicly. This is our strongest proof asset and it costs nothing, because
  a signal is worthless after the session it belongs to.
- The losing trades. Always public.

**Paid:**
- Real-time alerts during the session. Timing *is* the product.
- Indicator access on their own chart (TradingView invite-only).
- Star ratings and the full JSON payload (SL/TP/R).

The rule that makes this coherent: **we gate immediacy, not knowledge.**

## Free-tier design

A public channel carrying delayed signals plus education, feeding the private
channel, is the highest-converting structure available to us. It is a
permanent, searchable proof archive that also serves `community` and `social`.

Do not offer a free trial of the live channel. Trials in signal businesses
attract screenshot-and-leave users, and manual provisioning makes them
expensive (`revops`). A delayed public feed does the same job with none of
the cost.

## Presenting the boundary

- Say what is behind it, specifically: "real-time alerts, 07:00–11:00 and
  13:30–17:00 UTC, with entry/SL/TP1/TP2."
- Never tease with a blurred screenshot. It reads as manipulative to this
  audience.
- Price beside the boundary, always (`pricing`).
- No "last chance" framing at the wall.

## Leak control

Subscribers forward alerts. Accept a baseline of it; alerts are time-decaying
and forwarded proof is marketing. Act only on systematic redistribution:
watermark chart images (`image`), keep invite links single-use and timed
(`signup-flow`), and rotate on abuse.

## Cross-references

- `pricing` — what each side of the wall costs.
- `free-tools`, `lead-magnets` — the free side's assets.
- `community` — the public channel is a community surface too.
