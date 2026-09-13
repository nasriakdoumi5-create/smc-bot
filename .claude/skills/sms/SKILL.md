---
name: sms
description: Use SMS and push-style messaging for time-critical notifications only. For this product Telegram is the primary push channel, so this skill mostly governs when NOT to use SMS.
---

# sms

Read `product-marketing` first.

## Position

Telegram already is our push channel, and it is better than SMS for this
purpose: free, rich formatting, instant, and where the audience already is.
SMS therefore has one narrow job — **reaching a subscriber when Telegram
cannot**.

## Legitimate SMS uses

1. Payment failed / access about to lapse, and the Telegram invite has
   already expired (they are out of the channel, so we cannot reach them).
2. A service incident affecting live alerts during a session.
3. Two-factor or access confirmation, if ever implemented.

That is the complete list. No marketing broadcasts, no "signal alert" SMS
upsells, no re-engagement campaigns.

## Why so restricted

- SMS marketing for financial products is heavily regulated (TCPA in the US
  and equivalents elsewhere), carries real per-message fines, and requires
  documented express written consent.
- Costs scale per message with no engagement benefit over Telegram.
- Our audience reads unsolicited trading SMS as a pump-and-dump marker.

## If SMS is used

- [ ] Express opt-in captured and stored with timestamp and the exact consent
      wording.
- [ ] Sender identifies the business in message one.
- [ ] STOP honored immediately and permanently.
- [ ] No trading claims of any kind — 160 characters cannot carry the
      required disclaimers, so the claims must not be made.
- [ ] Never sent during a kill zone unless it is about that session's alerts.
- [ ] Quiet hours respected in the recipient's timezone, not ours.

## Telegram push, done well

The real work is in the Telegram messages `bot.js` sends:
- Alert format is fixed and identical every time — traders act on pattern
  recognition under time pressure.
- Never send marketing into the signals channel during a session. It breaks
  the signal-to-noise contract subscribers are paying for.
- Status messages (session open/closed, system health) are welcome; promotions
  are not.

## Cross-references

- `emails` — the correct channel for anything non-urgent.
- `churn-prevention` — the lapse flows that may justify an SMS.
- `onboarding` — sets expectations for what arrives where.
