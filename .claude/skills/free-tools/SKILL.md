---
name: free-tools
description: Build small free utilities that attract the ICP, earn links, and demonstrate competence. The highest-leverage acquisition asset available to this product.
---

# free-tools

Read `product-marketing` first.

## Why this is the best channel we have

Paid is mostly closed (`ads`). Content takes months (`content`). A free tool
that a trader opens every session is a durable acquisition asset: it ranks,
it earns links, it gets shared in Discords where promotion is banned but
useful links are not, and it proves competence without a single claim.

We already have the engine. Shipping a calculator is days of work, not months.

## The build queue, ranked

1. **Kill Zone Clock** — live countdown to London (07:00–11:00 UTC) and NY
   (13:30–17:00 UTC) opens, in the visitor's local timezone. Trivial to
   build, genuinely used daily, perfectly targeted. Ship this first.
2. **Prop-Firm Position Sizer** — contracts for MNQ/NQ/MES/ES given account
   size, stop in points, and a max-drawdown rule. Speaks to the ICP's actual
   fear (`product-marketing`), not a generic risk calculator.
3. **PDH/PDL + Asia Range Marker** — yesterday's high/low and the Asia
   session range for NQ/ES, updated daily. We already have the data
   (`data/nq_5m.json`) and the logic.
4. **Webhook Payload Tester** — paste a TradingView alert JSON, see it
   validated and rendered as a Telegram message. Attracts the technical
   segment and the bot-as-a-service buyer directly.
5. **Session Stats** — feeds `programmatic-seo`.

## Design rules

- **No email gate.** Gating a tool kills the sharing that makes it work. Ask
  for the email *after* value is delivered, optionally (`lead-magnets`).
- Works on a phone in ten seconds, no signup, no cookie banner.
- Loads fast and standalone — these get bookmarked and opened mid-session.
- One quiet, honest product mention: "the PDH/PDL sweeps this marks are what
  Kill Zone Sweep Pro flags automatically." One line, not a banner.
- Show the math. A visible formula converts skeptics; a black box does not.
- Accurate timezone handling, DST included. A clock that is wrong once is
  deleted forever.

## Distribution

Post to the relevant communities as a *free thing*, not a promotion. Submit to
tool directories (`directory`). Link from every relevant `/learn/` article.
Tools earn links passively, which is the compounding part (`seo-audit`).

## Cross-references

- `lead-magnets` — the post-value email ask.
- `site-architecture` — `/tools/` placement.
- `paywalls` — tools are firmly on the free side.
- `social` — the only self-promotion most communities tolerate.
