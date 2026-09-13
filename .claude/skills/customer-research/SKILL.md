---
name: customer-research
description: Learn what buyers actually think, in their own words — interviews, cancellation reasons, channel questions, and message mining. The upstream input to copywriting, cro, and competitors.
---

# customer-research

Read `product-marketing` first.

## Why this is upstream of everything

Every other skill needs three things it cannot invent: the objection, the
buyer's own words, and the real alternative set. Guessing at them produces
copy that sounds plausible and converts badly. At our traffic levels,
research is also strictly better than testing (`ab-testing`) — five
conversations beat an underpowered experiment.

## Sources we already have

Ranked by signal density, and all of them are free:

1. **Cancellation reasons** (`revops`, `churn-prevention`). The highest-signal
   data in the business. Record verbatim, never paraphrase into categories.
2. **Channel questions** (`community`). What subscribers ask reveals what
   onboarding failed to explain and what the sales page should pre-answer.
3. **Pre-purchase DMs.** The objection, stated plainly, before we have
   influenced it.
4. **Sales conversations** (`sales-enablement`).
5. **The "how did you find us" field** (`analytics`).
6. **Competitor community threads** — what their members complain about is
   our positioning gap (`competitors`), observed publicly and ethically
   (`competitor-profile`).

## Interview method

Aim for five conversations, 20 minutes each. Ask about behavior, never about
preference — people predict their own future behavior badly.

Good questions:
- "Walk me through the last trade you took from a signal. What did you do
  first?"
- "What were you using before this? Why did you stop?"
- "What nearly stopped you from paying?"
- "When was the last time you ignored an alert? What made you skip it?"
- "If this disappeared tomorrow, what would you use instead?"

Bad questions: "Would you pay for X?", "Do you like the new page?", "What
features do you want?" — all three produce confident, useless answers.

## Capture discipline

Record the **exact words**. "I'm scared of blowing the funded account on one
bad day" is usable copy (`copywriting`); "concerned about risk management" is
a paraphrase that helps nobody. Keep a running quote file organized by theme:
fear, objection, alternative, moment of value.

## The output

Research is not done until it produces:
- The top 5 objections, ranked, in buyer language → `cro` FAQ, `sales-enablement`.
- The activation moment, described concretely → `onboarding`.
- The real alternative set → `competitors`.
- A quote file → `copywriting`.

## Cadence

Five interviews per quarter, cancellation reasons logged continuously,
channel questions reviewed weekly. Small and constant beats an annual survey.

## Cross-references

- `customer-research` → `copywriting`, `cro`, `competitors` — the primary
  downstream paths.
- `churn-prevention` — exit interviews.
- `marketing-psychology` — interprets what the research surfaces.
