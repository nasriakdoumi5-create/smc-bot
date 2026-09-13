---
name: seo-audit
description: Audit a site or landing page for technical and on-page SEO problems, ranked by impact on qualified traffic. Use before any content push, after a redesign, or when rankings drop. Pairs with schema and ai-seo.
---

# seo-audit

Read `product-marketing` first.

## When to use

Before investing in `content`, after a site change, or when organic signups
fall. Auditing is cheap; writing 20 posts onto a broken site is not.

## Order of operations

Fix in this order. Each step is worthless if the one above it is broken.

1. **Indexable** — robots.txt, `noindex`, canonical tags pointing at
   themselves, sitemap submitted and matching reality.
2. **Reachable** — every money page within 3 clicks of home; no orphan pages.
   See `site-architecture`.
3. **Fast** — LCP < 2.5s, CLS < 0.1. Chart screenshots are the usual culprit:
   serve WebP, set explicit width/height, lazy-load below the fold.
4. **Understood** — one `<h1>`, descriptive title tags, `schema` markup.
5. **Matched to intent** — the page answers the query the keyword implies.

## What to check, specifically

- Title tags: unique, < 60 chars, keyword front-loaded. `MNQ Kill Zone Signals
  — VWAP Bounce Pro` not `Home | Trading`.
- Meta descriptions: they do not rank, they do get clicked. Write them as ad
  copy — `copywriting` rules apply.
- Thin pages: anything under ~300 words that is not a tool page. Merge or cut.
- Duplicate content: the same indicator description on three pages.
- Broken internal links, redirect chains (> 1 hop), 404s with inbound links.
- Mobile: the audience checks signals on a phone during a session. Test at
  390px, not just "responsive-ish".
- HTTPS everywhere, no mixed content from chart image CDNs.

## Keyword reality for this product

Do not chase head terms (`day trading`, `futures`). They are owned by brokers
with real budgets and the traffic does not convert. Win the long tail the ICP
actually types:

- `nq kill zone times`, `london kill zone utc`
- `pdh pdl liquidity sweep strategy`
- `vwap bounce scalping mnq`
- `tradingview alert webhook telegram`  ← high intent, low competition, and
  we have genuinely useful content for it (see `free-tools`)
- `topstep drawdown rule` adjacents — the fear, not the feature

Search intent here is *informational leading to tooling*. The post teaches the
concept; the CTA offers the thing that automates it.

## Output format

Deliver findings as a ranked table: Issue | Pages affected | Impact (H/M/L) |
Fix | Effort. Never deliver an unranked crawl dump — it does not get actioned.

## Cross-references

- `schema` — structured data is part of every audit, handled separately.
- `ai-seo` — audit for LLM retrieval as a second pass over the same pages.
- `site-architecture` — fixes for internal linking and depth findings.
- `content` — where the audit's keyword gaps become a plan.
