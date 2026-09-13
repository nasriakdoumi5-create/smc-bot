---
name: cold-email
description: Write and sequence cold outreach to prospects — prop firms, trading educators, communities, and bot-as-a-service leads. Use for one-to-one or small-batch outreach, never for bulk blasting.
---

# cold-email

Read `product-marketing` first.

## Who cold email is for here

Not retail subscribers — they come from `content`, `community` and `social`.
Cold outreach targets **partners and higher-ticket buyers**:

- Trading educators and small communities who want a signal feed for members.
- Prop-firm-adjacent tool vendors for `co-marketing`.
- Traders with their own Pine strategy who want it wired to Telegram
  (bot-as-a-service, the highest-ticket thing we sell).
- Newsletter owners in the futures niche.

## Structure

Four sentences. If it needs more, the research was not done.

1. **Proof of specificity** — something only someone who looked would know.
   "Your MNQ kill-zone thread from last Tuesday" beats any compliment.
2. **The relevance bridge** — why that makes this email make sense.
3. **The ask** — one, small, concrete.
4. **The exit** — an easy no.

```
Subject: your MNQ kill-zone thread

Saw your breakdown of the 09:40 PDH sweep on Tuesday — you called the
rejection before the retest.

I run a Pine + webhook system that flags exactly that pattern (PDH/PDL,
Asia H/L, swing) and pushes entry/SL/TP to Telegram. Session-gated to
London and NY only.

Worth 10 minutes to see if a feed like that is useful for your members?

If not, no follow-up — just tell me and I'll drop it.
```

## Rules

- Under 90 words. Plain text, no images, no tracking pixel.
- No links in email one. Links depress deliverability and raise suspicion in
  a niche full of scams.
- No performance claims (`product-marketing`). Cold email is the *worst*
  surface to make one — unsolicited profit promises are exactly what
  regulators and spam filters look for.
- Two follow-ups maximum, 4 and 11 days out, each adding new information
  rather than "bumping this".
- Send from a real personal address, signed with a real name.
- Volume is capped by research capacity. 15 researched emails beat 500
  templated ones, and 500 templated ones will burn the domain.

## Deliverability basics

SPF, DKIM, DMARC configured. Warm a new domain for 3+ weeks. Never send bulk
from the domain that carries subscriber transactional mail — if it gets
flagged, access-grant emails stop arriving and `signup-flow` breaks.

## Cross-references

- `prospecting` — who to write to and the research that fills sentence one.
- `sales-enablement` — what to send once they reply.
- `revops` — where replies are tracked.
- `co-marketing` — the most common successful outcome of this outreach.
