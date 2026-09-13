---
name: programmatic-seo
description: Generate large sets of templated pages that each target a real long-tail query, without producing doorway spam. Use only when a genuine structured dataset exists to power them.
---

# programmatic-seo

Read `product-marketing` first.

## The one hard rule

Each generated page must contain data that page alone has. If the only
difference between two pages is a swapped noun, you have built doorway pages,
they will be deindexed, and they may take the rest of the site with them.

## Where this product has real data

We have OHLC history (`data/es_5m.json`, `data/nq_5m.json`, 1h files) and
backtest engines. That is a legitimate dataset. Viable templates:

1. **Session statistics pages** — `/stats/nq-london-kill-zone-<month>`:
   average range, sweep frequency, PDH vs PDL sweep split, for that month.
   Computed from real candles, updated monthly.
2. **Level pages** — `/levels/nq-previous-day-high-<date>` only if there is
   analysis, not just a number. Usually fails the hard rule. Skip.
3. **Comparison pages** — `/compare/<our-indicator>-vs-<alternative>`. Real
   but small-N; write these by hand via `competitor-profile` instead.

Realistically: **template #1 only**, on the order of dozens of pages, not
thousands. That matches the business — see `product-marketing` on why volume
is not the goal here.

## Build checklist

- [ ] Data source is real, refreshable, and scripted (a `.mjs` in this repo).
- [ ] Each page has ≥ 3 unique data points and a chart image.
- [ ] Template includes a hand-written intro per *cluster*, not per page.
- [ ] Internal links: page → cluster hub → money page (`site-architecture`).
- [ ] `schema` Dataset or Article markup applied.
- [ ] Hypothetical-results labeling on every statistic (`product-marketing`).
- [ ] Indexing is staged — publish 10, watch for 4 weeks, then scale.

## Kill criteria

Pull the whole set if: impressions rise but clicks do not, average time on
page is under 15s, or Search Console starts reporting "Crawled — currently
not indexed" across the cluster. Those mean Google judged the pages thin.

## Cross-references

- `content` — hand-written pillars must exist before templated spokes.
- `schema` — structured data per template.
- `analytics` — set the kill-criteria dashboard before launch, not after.
