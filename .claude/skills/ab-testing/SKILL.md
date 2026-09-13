---
name: ab-testing
description: Design, run, and read experiments honestly — including deciding when traffic is too low to test at all. Use before any "let's test it" instinct turns into a wasted month.
---

# ab-testing

Read `product-marketing` first.

## The uncomfortable first question

**Do we have the traffic?** At our scale, usually not.

To detect a lift from 3% to 4% conversion at 95% confidence with 80% power
you need roughly **3,800 visitors per variant** — about 7,600 total. If the
site sees 400 visitors a month, that test takes 19 months. It is not a test;
it is a decision deferred forever.

Rule: if the test cannot conclude within 4 weeks at current traffic, **do not
A/B test it.** Use these instead:

- **Sequential testing** — run A for two weeks, B for two weeks, compare, and
  accept the noise. Weak evidence, but honest and fast.
- **Judgment plus principles** — apply `cro` and `copywriting` and ship.
- **Qualitative** — five user interviews (`customer-research`) beat an
  underpowered test, and they explain *why*.
- **Painted door** — measure clicks on an offer before building it.

Underpowered tests are worse than no tests: they produce confident-looking
noise, and teams then build on it.

## When a real test is warranted

Only where volume exists: email subject lines across the whole list, social
post formats, and anything measured in impressions rather than subscribers.

## Test design checklist

- [ ] One variable. If two changed, the result is uninterpretable.
- [ ] Hypothesis written *before* launch: "Because [research finding], changing
      [X] will increase [metric] because [mechanism]."
- [ ] Primary metric declared in advance — and it is a business metric
      (paid subscribers), not a proxy (clicks) whenever possible.
- [ ] Sample size and end date computed before launch.
- [ ] Guardrail metrics named (refund rate, churn, bounce).

## Reading results honestly

- No peeking-and-stopping. Stopping when it looks good manufactures
  significance. Fix the end date and honor it.
- Run full weeks. Trader behavior differs sharply Monday vs Friday, and by
  session.
- A "win" under 5% relative lift at our sample sizes is noise. Treat it as
  inconclusive and keep the simpler variant.
- Negative results are results. Log them; they prevent re-testing the same
  idea next quarter.

## Log everything

Keep a running test log: hypothesis, dates, sample, result, decision. Without
it the same ideas get re-tested annually and nothing compounds.

## Cross-references

- `cro` ↔ `copywriting` ↔ `ab-testing` — the loop.
- `analytics` — the measurement layer this depends on.
- `customer-research` — the better tool at low traffic.
