---
name: content
description: Plan, outline, and produce articles and guides that attract qualified traders and route them to the offer. Use for the /learn cluster, topic planning, and any long-form piece.
---

# content

Read `product-marketing` first.

## The only content that works here

The ICP is sophisticated and skeptical. Generic "10 trading tips" content
insults them. Three formats earn attention:

1. **Mechanism explainers** — how a liquidity sweep actually forms, with
   annotated MNQ charts from our own data. Teaches something real.
2. **Measured claims** — "we ran the PDH sweep setup over 18 months of NQ 5m
   data; here is what the distribution looks like." We can actually do this
   with `backtest_sweep.mjs`. Nobody else in this niche publishes real
   distributions, and it is the single most differentiating content we have.
3. **Build logs** — wiring TradingView alerts to Telegram, the JSON payload
   schema, why the session filter exists. Attracts the technical trader who
   becomes a bot-as-a-service buyer.

## Pillar plan

| Pillar | Spokes | Routes to |
|---|---|---|
| Kill zones | London KZ times, NY KZ times, why sessions gate signals | Kill Zone Sweep Pro |
| Liquidity | PDH/PDL sweeps, Asia H/L, swing sweeps, sweep vs breakout | Kill Zone Sweep Pro |
| VWAP | ATR bands, rejection candles, RSI confirmation, mean reversion | VWAP Bounce Pro |
| Automation | TradingView webhooks, JSON alert payloads, Telegram delivery | Signals channel / BaaS |

## Outline template

1. Direct answer in the first 40 words (`ai-seo`).
2. Key-facts table — times, levels, thresholds.
3. The mechanism, with one annotated chart per section.
4. Worked example on a real dated MNQ session.
5. Where it fails — the honest section. Publish the losing case; it is the
   trust asset, and `marketing-psychology` explains why it outperforms.
6. One CTA, matched to the pillar's product.
7. Risk disclosure.

## Production rules

- One annotated chart per ~300 words. Generate via `/vision` (`chart_vision.js`)
  and mark up per `image`.
- Every number traceable to a backtest run with symbol, timeframe, date range.
- Arabic versions written natively, not translated — see `product-marketing`.
- No publishing on a schedule for its own sake. One measured-claims piece per
  month beats eight thin posts, and the thin posts actively hurt (`seo-audit`).

## Cross-references

- `seo-audit` — keyword gaps become this plan.
- `copywriting` — headline, intro and CTA are written under those rules.
- `copy-edit` — everything ships through it.
- `lead-magnets` — long pieces host the gated asset.
