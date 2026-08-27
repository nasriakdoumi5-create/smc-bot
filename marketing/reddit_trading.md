# Reddit — Trading Communities

The strongest free-traffic play you have: you actually trade MNQ. Post as a
trader sharing a system, not as a seller. Reddit punishes the second one hard.

**The rule that makes this work:** give the entire thing away in the post.
No links, no product mention in the body. The shop link lives in your profile.
People who want the pre-built version will find it. People who build it
themselves still remember your name.

---

## Before you post — 3 things

1. **Warm up the account.** Comment usefully on 5–10 posts over 2–3 days
   first. A brand-new account posting a long guide gets auto-removed.
2. **Put the link in your profile**, not the post. Reddit → Settings →
   Profile → Website: `https://nasritools.etsy.com`
3. **Read the subreddit rules.** r/Daytrading allows educational posts;
   several trading subs ban any commercial account outright.

Post at **13:00–15:00 UTC** on a weekday (US market open = peak traffic).

---

## POST 1 — r/Daytrading

**Title:**
> I journaled 200 trades before I realised I was tracking the wrong thing

**Body:**

For about a year my "journal" was a note on my phone: date, instrument, and
whether I made or lost money. I had 200 entries and learned exactly nothing
from them.

The problem is that P&L is an outcome, not information. A €400 winner from a
setup I have no business trading is worse for me than a small loss taken
correctly — but in a P&L-only log they look like +400 and -80, and the wrong
one looks better.

What actually changed things was adding two columns: **Setup** and **R**.

**R** is your risk unit. If your stop is 20 points away and you exit 40 points
in profit, that's +2R. Same trade with a 40-point stop is +1R. Normalising to R
lets you compare a scalp to a swing and stops position size from hiding your
real skill.

**Setup** is just a short tag — how you'd describe the trade to another trader.
Mine are things like `ORB`, `VWAP-reclaim`, `liquidity-sweep`, `revenge`
(yes, that's a real tag and yes it earned its own row).

Then you sort by Setup and average the R column. That's the whole trick.

For me the result was uncomfortable: **two of my six setups produced all of the
profit.** The other four were roughly break-even before fees and consistently
negative after. I wasn't a losing trader — I was a profitable trader funding
four hobbies.

---

**The sheet I use now — 12 columns, nothing more:**

| Column | Why it earns its place |
|---|---|
| Date | Group by day-of-week and time later |
| Symbol | Most people are good at one instrument and bad at the rest |
| Direction | Long/short bias is real and shows up fast |
| Entry / Stop / Target | Lets R be calculated, not guessed |
| Exit | The gap between Target and Exit is where discipline lives |
| Result | Win / Loss / Breakeven |
| **R:R** | `=(Exit-Entry)/(Entry-Stop)` — the number that matters |
| P&L | For taxes and the equity curve, not for decisions |
| **Setup** | The column that finds your edge |
| **Notes / Emotion** | One line. "Chased", "sized up after two wins", "felt fine" |

The dashboard on top is four formulas:

```
Win rate   = COUNTIF(Result,"Win") / COUNTA(Result)
Avg R      = AVERAGE(R:R column)
Net P&L    = SUM(P&L column)
Equity     = running SUM of P&L, plotted as a line
```

That's it. Win rate alone is meaningless — 40% at +2.5R beats 70% at +0.4R all
day. Look at win rate and average R together or don't look at all.

---

**Two habits that made it stick:**

**Log within 5 minutes of closing the trade.** If you batch it on Sunday you'll
reconstruct the version of events where you were rational. The Emotion column
is worthless written from memory.

**Review Sunday, 15 minutes.** Sort by Setup, average R per setup. Any setup
below 0R over 20+ trades stops trading for a month. That's the entire review.

---

Three months of this and I cut two setups completely and doubled size on one.
My win rate went *down*. My equity curve went up and to the right for the first
time.

Happy to answer questions about the formulas or how I tag setups — the
structure above is everything you need to build it in an afternoon.

---

## POST 2 — r/options (variant, post a week later)

**Title:**
> A journal column that changed how I pick option strategies

**Body:**

Most options journals I've seen track premium collected and P&L. Useful for
taxes, useless for improvement, because those numbers mix two very different
questions: *was the thesis right* and *was the structure right*.

The fix was one column: **Setup** — but tagged by structure, not ticker.
`credit-spread`, `long-call`, `IC`, `earnings-play`, `0DTE`.

Then average R (return in units of max risk) per tag over 20+ trades.

Mine, roughly:

- credit spreads: consistently positive, boring, small
- long calls on momentum: high variance, slightly negative
- earnings plays: negative every single quarter I've tracked
- 0DTE: the tag with the worst average R and the most entries — a pattern I'd
  bet a lot of people here share

None of that was visible in a P&L column. It only appeared once trades were
tagged by structure and normalised to risk.

The full column list I use: Date · Symbol · Direction · Entry · Stop · Target ·
Exit · Result · **R:R** · P&L · **Setup** · Notes/Emotion. Twelve columns, four
formulas on top (win rate, avg R, net P&L, equity curve).

Build it in Sheets in an afternoon. The uncomfortable part isn't the
spreadsheet, it's reading it honestly after 30 trades.

---

## Replies you'll need

**"Why not just use TraderVue / Tradezella?"**
> They're good and I've used them. Two reasons I went back to a sheet: it costs
> nothing, and I can add a column the moment I notice something worth tracking.
> The tagging is the part that matters — the tool is secondary. If you'd rather
> pay for automatic broker sync, that's a completely reasonable trade-off.

**"Can you share the sheet?"**
> Every column and formula is in the post — that's genuinely all of it. I keep a
> tidied-up version with the dashboard and equity curve pre-built (it's in my
> profile), but you'll understand it better if you build it yourself once.

**"What's R exactly?"**
> Your risk on the trade, as one unit. Stop 20 points away = 1R is 20 points.
> Exit +40 points = +2R. Exit -20 = -1R. It makes a scalp and a swing directly
> comparable and stops position size from flattering your results.

**"Win rate isn't everything"**
> Exactly the point — that's why avg R sits next to it on the dashboard. 40% at
> +2.5R is a business. 70% at +0.4R is a treadmill.

---

## What NOT to do

- Don't link the shop in the post body. Instant removal in most trading subs.
- Don't post the same text in 5 subs on the same day.
- Don't argue with sceptics — answer the technical question and move on.
- Don't post screenshots of profits. That flags you as a seller immediately.

## After it lands

Reply to every comment for the first 6 hours — that's what drives the ranking.
Check Etsy Stats → Traffic sources 24h later to see what Reddit actually sent.
