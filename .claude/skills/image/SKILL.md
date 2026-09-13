---
name: image
description: Produce and standardize visual assets — annotated chart screenshots, thumbnails, listing images, and social cards. Use whenever an asset needs a picture, which for this product is nearly always.
---

# image

Read `product-marketing` first.

## The core asset: the annotated chart

Nearly every image we publish is a chart with something marked on it. Getting
this consistent is a brand decision, not a design flourish — repeated visual
grammar is how a small operation looks established.

**House chart style:**
- Dark background, single instrument, 5m timeframe unless stated.
- Instrument, timeframe and date **always** visible, top-left.
- The swept level drawn as a horizontal ray, labeled (`PDH`, `Asia H`).
- The kill-zone window shaded, faintly.
- Entry / SL / TP marked with the same three colors every time.
- Maximum three annotations. A cluttered chart reads as post-hoc rationalizing.
- Watermark: small, bottom-right, consistent placement, low opacity.

## Generation

`chart_vision.js` / `/vision` captures live charts via CDP. Prefer real
captures over drawn mockups — always. A mockup that is discovered as a mockup
ends the relationship with this audience.

## Format-specific specs

| Use | Size | Notes |
|---|---|---|
| TradingView listing | 16:9, clean | It is the thumbnail; one setup, no clutter (`aso`) |
| YouTube thumbnail | 1280×720 | Legible at 120px; 4 words maximum |
| X/Twitter post | 16:9 or 4:5 | 4:5 takes more feed height |
| Open Graph | 1200×630 | Text safe-zone centered |
| Telegram | any, < 1MB | Compression is aggressive; avoid thin lines |

## Technical rules

- WebP for the site with PNG fallback; explicit width/height to protect CLS
  (`seo-audit`).
- Descriptive alt text on every image — it is accessibility, SEO and LLM
  extraction at once: `MNQ 5m, PDH swept at 09:42 UTC, rejection into short`.
- File names descriptive: `mnq-pdh-sweep-0942.webp`.
- Never screenshot someone else's chart or paid indicator. Copyright and
  credibility both.

## Banned

Stock photos of traders, city skylines, bull/bear statues, glowing candlestick
renders, money imagery of any kind. Every one of these is a category scam
marker to our ICP.

## Cross-references

- `aso` — listing images.
- `video` — thumbnails share this grammar.
- `social` — most posts are one image.
- `ad-creative` — if paid ever opens up, creative starts from this style.
