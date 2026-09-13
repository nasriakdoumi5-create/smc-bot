---
name: popups
description: Specify interstitials, exit-intent offers, banners and slide-ins so they capture intent without damaging trust or SEO. Use sparingly and only with a real offer behind them.
---

# popups

Read `product-marketing` first.

## The trust constraint

This audience treats aggressive popups as a scam marker. The cost of a badly
judged popup is not a lower conversion rate on that session — it is a visitor
who concludes the whole operation is a boiler room and never returns. Default
to *none*, and earn each one.

## What is allowed

- **Exit-intent on desktop only**, offering a genuinely useful asset (a
  `lead-magnets` piece, e.g. the kill-zone cheat sheet), once per visitor per
  30 days.
- **Inline slide-in** at 60% scroll depth on `/learn/` articles. Inline, not
  overlay. No dimming, no page block.
- **Persistent slim banner** for something factually important (a price
  change, a fulfillment delay). Dismissible, and it stays dismissed.

## What is banned

- Entry popups within the first 15 seconds — a Google mobile-interstitial
  penalty risk (`seo-audit`) and the worst trust signal we can send.
- Countdown timers, spinning wheels, "wait! don't go" guilt copy.
- Anything on mobile that covers content. Ever.
- Fake scarcity of any kind (`product-marketing` claim rules).
- Second popups after a dismissal.

## Specification checklist

- [ ] Trigger: exact event and threshold.
- [ ] Frequency cap and how it is stored.
- [ ] Mobile behavior explicitly defined (usually: does not show).
- [ ] Close affordance ≥ 44px, visible, top-right, no dark pattern.
- [ ] The offer is worth the interruption — if the asset would not stand
      alone as a page, it is not worth a popup.
- [ ] Copy follows `copywriting`: concrete asset, not "join our newsletter".
- [ ] Instrumented as its own funnel step in `analytics`.

## Measurement

Judge on *net* effect: capture rate minus bounce-rate change on the pages it
fires on, and 30-day return-visit rate. A popup that captures 4% while adding
6 points of bounce is a loss. Most are.

## Cross-references

- `cro` — the parent skill; popups are a last resort, not a first move.
- `lead-magnets` — the only acceptable payload.
- `ab-testing` — measure net effect, on the metrics above.
