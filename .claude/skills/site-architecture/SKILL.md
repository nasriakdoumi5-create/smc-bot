---
name: site-architecture
description: Design URL structure, internal linking, and navigation so that authority flows to money pages and visitors reach the offer in under three clicks. Use when planning a new site, adding a content section, or fixing orphan pages found in seo-audit.
---

# site-architecture

Read `product-marketing` first.

## Principle

Structure is a routing problem: every page either converts, or routes to a
page that converts. A page doing neither should not exist.

## The shape for this business

```
/                         → offer, proof, pricing (the money page)
/indicators/
  /vwap-bounce-pro        → product page, invite-only access
  /kill-zone-sweep-pro    → product page
/signals                  → Telegram channel offer
/learn/                   → the content hub (traffic entry)
  /kill-zones
  /liquidity-sweeps
  /vwap-bands
  /tradingview-webhook-telegram
/tools/                   → free tools (link magnets, see free-tools)
  /kill-zone-clock
  /position-size-calculator
/pricing
/faq
```

Flat and shallow. Three levels maximum. Every `/learn/` page links up to its
hub and across to the one product that solves what it just taught.

## Internal linking rules

- **Hub-and-spoke, not a mesh.** Each topic cluster has one pillar page; the
  spokes link to the pillar and to each other only where genuinely relevant.
- Link with descriptive anchor text (`London kill zone times`), never
  `click here` or a bare URL.
- The money pages get the most internal links. Count them; if `/pricing` has
  fewer inbound internal links than a blog post, the structure is upside down.
- Every page has exactly one obvious next action. Two CTAs compete and both
  lose — see `cro`.

## URL rules

- Lowercase, hyphenated, no dates, no IDs. `/learn/kill-zones` not
  `/blog/2025/03/post-142`.
- Never change a URL that has links or rankings. If you must, 301 it and keep
  the redirect forever.
- No parameters in indexable URLs. Filters get canonical tags.

## Navigation

Header: Indicators · Signals · Learn · Pricing. Four items. Footer carries
compliance (risk disclosure, terms, refund policy) and secondary links.

The risk disclosure lives in the footer of every page — `product-marketing`
requires it and it is an architecture decision, not a copy decision.

## Cross-references

- `seo-audit` — surfaces the depth and orphan problems this skill fixes.
- `cro` — page-level conversion; this skill handles between-page flow.
- `content` — the `/learn/` cluster plan comes from here.
