# Marketing skills

A skill tree for marketing SMC Bot — the indicators, the signals channel, and
bot-as-a-service. Structure follows the reference architecture: one root skill
that every other skill reads first, seven domains beneath it, and explicit
cross-references between related skills.

```
product-marketing  (read first — ICP, positioning, claim rules, voice)
├── SEO & Content ....... seo-audit · ai-seo · site-architecture ·
│                         programmatic-seo · schema · content · aso
├── CRO ................. cro · signup-flow · onboarding · popups · paywalls
├── Content & Copy ...... copywriting · copy-edit · cold-email · emails ·
│                         social · video · image · sms
├── Paid & Measurement .. ads · ad-creative · ab-testing · analytics
├── Growth & Retention .. referrals · free-tools · churn-prevention ·
│                         community · lead-magnets · co-marketing
├── Sales & GTM ......... revops · sales-enablement · launch · pricing ·
│                         competitors · competitor-profile · directory ·
│                         prospecting
└── Strategy ............ marketing-ideas · marketing-psychology ·
                          customer-research
```

## How to use

Invoke a skill by name for the task at hand. Each one opens by pointing back
to `product-marketing`, which carries the facts the rest depend on: who the
buyer is, what the products cost, and what may not be claimed.

The claim rules in `product-marketing` are binding. Trading products carry
real constraints — TradingView removes scripts with promotional descriptions,
Meta and Google restrict financial ads, and performance claims create
exposure. `copy-edit` is the gate every public asset passes through.

## Where the content came from

Written against this repo's actual business: the pricing, products, and
fulfillment model in `BUSINESS_SETUP.md`, the alert payload emitted by
`bot.js`, the published Pine scripts, and the backtest engines over
`data/nq_5m.json` and `data/es_5m.json`. The recommendations assume a
one-operator business with manual provisioning, because that is what it is.

## Starting points

- Never marketed this before → `marketing-ideas` (ranked backlog)
- Writing anything public → `copywriting`, then `copy-edit`
- Subscribers leaving → `churn-prevention`
- Want more traffic → `free-tools`, then `content`
- Someone replied to outreach → `sales-enablement`
