---
name: emails
description: Design lifecycle and broadcast email — welcome sequences, renewal notices, win-backs, and the list newsletter. Use for anything sent to people who already gave us their address.
---

# emails

Read `product-marketing` first.

## The three jobs

1. **Transactional** — access granted, payment received, renewal due,
   invite link expiring. These are the most-read emails we send and the most
   neglected. Fix these before writing a newsletter.
2. **Lifecycle** — onboarding sequence (`onboarding`), win-back
   (`churn-prevention`), upgrade nudges.
3. **Broadcast** — the weekly recap to the free list.

## Transactional set (build first)

| Trigger | Timing | Must contain |
|---|---|---|
| Payment received | instant | What happens next, the expected wait, risk line |
| Access granted | on grant | TradingView confirmation, Telegram invite + its expiry, the payload guide |
| Renewal due | T-5 days | Exact amount, exact date, how to cancel |
| Invite expiring | T-3 days | New link or the renewal path |
| Payment failed | instant | One clear action, no blame language |

The renewal notice is where manual billing either retains or loses people. A
subscriber surprised by an expired link churns and tells others we vanished.

## The weekly recap (broadcast)

The highest-leverage broadcast we can send, because it writes itself from data
we already produce:

- Setups flagged this week, by star rating.
- What happened, wins and losses both.
- One teaching note from a losing trade.
- One line on what the system did *not* fire on, and why.

Send it to the free list. It is simultaneously proof, education, and the
soft conversion path off `paywalls`' delayed feed.

## Rules

- Subject lines are descriptive, not curiosity-baited. `Week of Mar 3 — 11
  setups, 4 stopped` outperforms `You won't believe this week`.
- Plain-text-leaning HTML. Heavy templates land in Promotions.
- One CTA per email (`cro`).
- Risk disclosure in the footer of every marketing email.
- Real unsubscribe link, honored immediately.
- Segment at minimum: free list vs active subscriber vs lapsed. Sending an
  active subscriber a "come back" email is a churn trigger, not a save.

## Measurement

Track opens with skepticism (privacy proxies inflate them), clicks honestly,
and replies as the real engagement signal. Route reply content into
`customer-research`.

## Cross-references

- `onboarding` — the first sequence.
- `churn-prevention` — renewal and win-back flows.
- `copy-edit` — every email passes through it.
- `lead-magnets` — how the free list gets built.
