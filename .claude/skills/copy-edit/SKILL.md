---
name: copy-edit
description: Edit existing copy for clarity, voice, and compliance before it ships. Every public-facing asset passes through this skill. Use as the final gate on any copy, from any other skill.
---

# copy-edit

Read `product-marketing` first.

## Role

This is the gate, not a style preference. Nothing public ships unedited:
landing pages, script descriptions, emails, social posts, ad copy, bot
messages.

## Pass 1 — compliance (blocking)

Any failure stops the asset:

- [ ] No guaranteed/implied returns, no "risk-free", no income claims.
- [ ] Every statistic carries symbol, timeframe, and date range.
- [ ] Backtested figures labeled **hypothetical**, at the same visual weight.
- [ ] Risk disclosure present where the surface requires it.
- [ ] No advice framing.
- [ ] Testimonials carry the required disclaimer.
- [ ] TradingView assets: no links, price, or promo in script descriptions.
- [ ] No fake scarcity or urgency.

## Pass 2 — voice

- Cut every adjective that is not load-bearing. "Powerful", "advanced",
  "elite", "game-changing" — delete, do not replace.
- Convert passive to active. "Signals are generated when..." → "The system
  flags...".
- Replace vague quantities with numbers, or cut the sentence.
- One idea per sentence. Break anything over ~25 words.
- Remove hype punctuation: no exclamation marks, no rocket/money emoji.
- Arabic copy: check it reads as native register, not translationese. Mixed
  Arabic/English technical terms are correct and normal for this audience —
  do not "fix" `liquidity sweep` into an awkward calque.

## Pass 3 — structure

- Does the first line answer the reader's question? (`ai-seo`)
- Is the CTA singular and identical everywhere on the asset? (`cro`)
- Are the strongest proof points above the fold?
- Would the ICP recognize the vocabulary as insider-correct? Wrong jargon is
  worse than plain language — `PDH` misused ends the read.

## Pass 4 — mechanics

Spelling, number consistency (a price stated twice must match `pricing`),
link targets live, UTM parameters correct (`analytics`), timezone labels
present on every time.

## Output

Return the edited copy plus a short list of what changed and why. If a
compliance item blocked, say so explicitly at the top — do not quietly
rewrite around a claim the requester may have wanted.

## Cross-references

- `copywriting` — writes it; this skill gates it.
- `product-marketing` — the claim rules enforced here.
