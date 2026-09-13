---
name: schema
description: Add and validate structured data (JSON-LD) so pages qualify for rich results and are cleanly parsed by search engines and LLMs. Use on every new page template and whenever seo-audit flags missing markup.
---

# schema

Read `product-marketing` first.

## Rules

- JSON-LD in `<head>`. Never microdata, never RDFa.
- Mark up only what is **visible on the page**. Invisible markup is a
  manual-action risk.
- Validate every template against the Rich Results Test and Schema.org
  validator before it ships. Both — they catch different things.

## Types this site needs

**Organization** (site-wide, once):
```json
{"@context":"https://schema.org","@type":"Organization",
 "name":"SMC Bot","url":"https://example.com",
 "logo":"https://example.com/logo.png",
 "sameAs":["https://tradingview.com/u/...","https://t.me/..."]}
```
`sameAs` matters more than it looks — it links the TradingView profile, the
Telegram channel and the site into one entity. See `ai-seo`.

**Product + Offer** on each indicator page — name, description, price,
priceCurrency, availability. Use the real price from `pricing`; mismatched
markup and on-page price is a violation.

**FAQPage** on `/faq` and on `/learn/` pages with a real Q&A block. The
highest-leverage markup we have: it wins SERP real estate and feeds LLM
extraction.

**Article** (or TechArticle) on `/learn/` posts — headline, datePublished,
dateModified, author. `dateModified` must be truthful.

**SoftwareApplication** is tempting for the indicators. Use Product instead —
the offer is a subscription, and Product carries the Offer cleanly.

**BreadcrumbList** wherever `site-architecture` defines a hierarchy.

## Review markup — a warning

Do not add AggregateRating to the product pages. Self-serving review markup on
your own product is against Google's guidelines, and in a financial category
it invites exactly the scrutiny we do not want. Testimonials stay as plain
content with the disclaimer required by `product-marketing`.

## Cross-references

- `seo-audit` — schema coverage is an audit line item.
- `ai-seo` — FAQ and Product markup are the main extraction levers.
- `pricing` — the source of truth for any Offer block.
