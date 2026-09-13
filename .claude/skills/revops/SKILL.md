---
name: revops
description: Run the revenue operations layer — the subscriber source of truth, the manual provisioning queue, renewals, and the pipeline. Use when fulfillment, billing, or pipeline tracking needs designing or fixing.
---

# revops

Read `product-marketing` first — manual fulfillment is the defining
constraint of this business, and this skill owns it.

## The source of truth

One record per subscriber, one place. At this scale a single sheet is correct;
what is wrong is scattering the truth across Telegram's member list,
TradingView's access panel, and PayPal.

Required fields:

| Field | Why |
|---|---|
| Email | The channel we own |
| TradingView username | Provisioning; the most error-prone field |
| Telegram handle / user ID | Channel access |
| Plan | Indicator / channel / bundle / full |
| Amount, currency, method | PayPal vs USDT margins differ |
| Paid on / Access granted on | The SLA gap (`analytics`) |
| Renews on | Drives the renewal notices |
| Source | "How did you find us" (`analytics`) |
| Referred by | `referrals` |
| Status | active / lapsed / cancelled + reason |

Cancellation reasons are the input to `churn-prevention` and
`customer-research`. Record them verbatim.

## The provisioning queue

```
Payment cleared → verify TradingView username → grant script access
                → generate 30-day single-use Telegram invite
                → send access email (onboarding)
                → record grant timestamp
```

- **SLA: 12 hours, target 2.** State it at checkout (`signup-flow`) and beat it.
- Batch the work at fixed times daily rather than reacting — but never let a
  payment sit overnight without at least the automated confirmation.
- Invalid username is the #1 delay; validate at checkout, and have a single
  pre-written follow-up ready.

## Renewals

Manual billing means renewals are an operational process, not a background
job. Weekly, work the list of subscribers renewing in the next 7 days:
send notice at T-5, expiry warning at T-3, recovery at T+1 and T+7
(`emails`, `churn-prevention`). Involuntary churn is pure waste and it is
entirely preventable at our volume.

## Capacity planning

Know the ceiling before marketing raises demand: at roughly 10 minutes of
manual work per new subscriber plus renewals, one person sustains perhaps
60–80 active subscribers before fulfillment degrades. Campaigns are paced to
that number (`ads`, `co-marketing`), or the ceiling is raised first by
automating provisioning.

## Pipeline (for partners and BaaS)

Lightweight stages: contacted → replied → call → proposal → closed. Anything
over 14 days without movement is closed-lost; a stale pipeline lies about the
state of the business.

## Cross-references

- `signup-flow` — the front half of this pipeline.
- `sales-enablement` ↔ `revops` ↔ `cold-email` — one pipeline, three views.
- `analytics` — the SLA and churn numbers originate here.
- `pricing` — plan definitions.
