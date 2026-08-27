"""
store_agent.py — NasriTools store manager
One command that watches the shop and tells you what needs attention.

    python store_agent.py            full report
    python store_agent.py health     account + billing only
    python store_agent.py stats      listings + sales only
    python store_agent.py plan       what to do next

Read-only. It never changes anything.

Needs the wider scopes — if billing shows "no access", run:
    python etsy_reauth.py
"""
import json, os, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
API        = "https://api.etsy.com/v3/application"
STATE_FILE = Path(__file__).parent / "agent_state.json"

STATES = ["active", "inactive", "draft", "expired", "sold_out"]
RENEW_FEE = 0.20          # USD per listing renewal
WARN_DAYS = 21            # warn about listings expiring within N days

C = {"g": "\033[92m", "y": "\033[93m", "r": "\033[91m",
     "b": "\033[94m", "d": "\033[2m", "x": "\033[0m"}
if os.name == "nt" and not os.environ.get("WT_SESSION"):
    C = {k: "" for k in C}          # plain output on old consoles

def hdr(t):
    print(f"\n{C['b']}{'─' * 62}{C['x']}")
    print(f"{C['b']}  {t}{C['x']}")
    print(f"{C['b']}{'─' * 62}{C['x']}")

def ok(m):    print(f"  {C['g']}✓{C['x']} {m}")
def warn(m):  print(f"  {C['y']}⚠{C['x']} {m}")
def bad(m):   print(f"  {C['r']}✗{C['x']} {m}")
def info(m):  print(f"    {C['d']}{m}{C['x']}")

# ── auth ────────────────────────────────────────────────────────────────
def get_token():
    if not TOKEN_FILE.exists():
        bad(f"No token at {TOKEN_FILE} — run: python etsy_reauth.py")
        sys.exit(1)
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        if not r.ok:
            bad(f"Token refresh failed ({r.status_code}) — run: python etsy_reauth.py")
            sys.exit(1)
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def H(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def api(token, path, **params):
    r = requests.get(f"{API}{path}", headers=H(token), params=params, timeout=30)
    return (r.json() if r.ok else None), r.status_code

# ── data ────────────────────────────────────────────────────────────────
def fetch_listings(token):
    out, seen = [], set()
    for state in STATES:
        offset = 0
        while True:
            d, code = api(token, f"/shops/{SHOP_ID}/listings",
                          state=state, limit=100, offset=offset)
            if not d:
                break
            batch = d.get("results", [])
            for l in batch:
                if l["listing_id"] not in seen:
                    seen.add(l["listing_id"])
                    l["_state"] = state
                    out.append(l)
            if len(batch) < 100:
                break
            offset += 100
            time.sleep(0.3)
        time.sleep(0.2)
    return out

def price_of(l):
    p = l.get("price", {}) or {}
    return float(p.get("amount", 0)) / max(p.get("divisor", 100), 1)

def days_left(l):
    ts = l.get("ending_timestamp") or l.get("expiry_timestamp")
    if not ts:
        return None
    return (datetime.fromtimestamp(ts, timezone.utc) - datetime.now(timezone.utc)).days

# ── sections ────────────────────────────────────────────────────────────
def section_health(token, listings):
    hdr("1 · ACCOUNT HEALTH")

    shop, code = api(token, f"/shops/{SHOP_ID}")
    if shop:
        ok(f"Shop reachable — {shop.get('shop_name')}")
        info(f"favourites: {shop.get('num_favorers', 0)}  ·  "
             f"active listings (Etsy count): {shop.get('listing_active_count', 0)}")
        if shop.get("is_vacation"):
            bad("Shop is in VACATION MODE — buyers cannot purchase")
    else:
        bad(f"Cannot read shop ({code}) — account may be suspended")
        return

    # billing / ledger — the thing that caused the suspension
    led, code = api(token, f"/shops/{SHOP_ID}/payment-account/ledger-entries",
                    limit=25, min_created=0)
    if led and led.get("results"):
        entries = led["results"]
        bal = entries[0].get("balance")
        cur = entries[0].get("currency", "")
        if bal is not None:
            b = bal / 100
            if b < 0:
                bad(f"BALANCE OWED: {b:.2f} {cur} — pay it or the shop gets suspended")
                info("https://www.etsy.com/your/account/payments")
            else:
                ok(f"Balance: {b:.2f} {cur}")
        info(f"last {len(entries)} ledger entries readable")
    elif code in (401, 403):
        warn("No billing access — run: python etsy_reauth.py  (adds billing scope)")
        info("Until then check manually: etsy.com/your/account/payments")
    else:
        info("No ledger entries yet")

    # upcoming renewal cost
    soon = [l for l in listings
            if l["_state"] == "active" and (days_left(l) or 999) <= WARN_DAYS]
    if soon:
        cost = len(soon) * RENEW_FEE
        warn(f"{len(soon)} listing(s) renew within {WARN_DAYS} days → ~${cost:.2f} in fees")
        for l in soon[:5]:
            info(f"{days_left(l)}d · {l.get('title','')[:48]}")
    else:
        ok(f"No renewals due in the next {WARN_DAYS} days")

def section_stats(token, listings):
    hdr("2 · LISTINGS & SALES")

    by_state = {}
    for l in listings:
        by_state[l["_state"]] = by_state.get(l["_state"], 0) + 1
    for s in STATES:
        n = by_state.get(s, 0)
        if n:
            (ok if s == "active" else info)(f"{s:10} {n}")

    active = [l for l in listings if l["_state"] == "active"]
    if active:
        prices = [price_of(l) for l in active]
        favs = sum(l.get("num_favorers", 0) for l in active)
        print()
        info(f"price range: {min(prices):.2f} – {max(prices):.2f}   "
             f"avg {sum(prices)/len(prices):.2f}")
        info(f"total favourites across listings: {favs}")

        ranked = sorted(active, key=lambda l: l.get("num_favorers", 0), reverse=True)
        print(f"\n  {C['d']}Most favourited:{C['x']}")
        for l in ranked[:5]:
            print(f"    {l.get('num_favorers',0):3} ♥  {price_of(l):6.2f}  "
                  f"{l.get('title','')[:44]}")

    # sales
    rec, code = api(token, f"/shops/{SHOP_ID}/receipts", limit=25)
    print()
    if rec:
        n = rec.get("count", 0)
        ok(f"Orders (all time): {n}")
        for r in rec.get("results", [])[:5]:
            when = datetime.fromtimestamp(r.get("created_timestamp", 0)).strftime("%Y-%m-%d")
            total = (r.get("grandtotal", {}) or {}).get("amount", 0) / 100
            info(f"{when} · {total:.2f} · {r.get('status','')}")
    elif code in (401, 403):
        warn("No transaction access — run: python etsy_reauth.py")
    else:
        info("No orders yet")

def section_plan(listings):
    hdr("3 · WHAT TO DO NEXT")

    active = [l for l in listings if l["_state"] == "active"]
    favs   = sum(l.get("num_favorers", 0) for l in active)
    n      = len(active)

    steps = []
    if n == 0:
        steps.append("Shop has no active listings → python publish_premium.py")
    if n and n < 10:
        steps.append(f"Only {n} active listings. 15–25 is the sweet spot for "
                     "Etsy search — add products in your strongest niche.")
    if favs == 0 and n:
        steps.append("Zero favourites → nobody is finding the shop yet. "
                     "Traffic is the bottleneck, not the products.")

    steps += [
        "Pinterest: upload the 3 pins in pins/ (captions in pin_captions.txt)",
        "Reddit: post the r/googlesheets draft in marketing/launch_pack.md",
        "TikTok: film script #1 (30s screen recording, no face needed)",
        "Trading Journal: post in r/Daytrading or r/options as a real user — "
        "you actually trade MNQ, that story sells better than any ad",
        "Check etsy.com/your/account/payments weekly so fees never pile up again",
    ]

    for i, s in enumerate(steps, 1):
        print(f"  {C['y']}{i}.{C['x']} {s}")

def save_snapshot(listings):
    snap = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "active": len([l for l in listings if l["_state"] == "active"]),
        "total": len(listings),
        "favourites": sum(l.get("num_favorers", 0) for l in listings),
    }
    hist = []
    if STATE_FILE.exists():
        try:
            hist = json.loads(STATE_FILE.read_text()).get("history", [])
        except Exception:
            hist = []
    if hist:
        prev = hist[-1]
        d_fav = snap["favourites"] - prev.get("favourites", 0)
        if d_fav:
            print(f"\n  {C['d']}since last check ({prev['checked_at'][:10]}): "
                  f"{d_fav:+d} favourites{C['x']}")
    hist.append(snap)
    STATE_FILE.write_text(json.dumps({"history": hist[-60:]}, indent=2))

def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()

    print(f"\n{C['b']}{'═' * 62}{C['x']}")
    print(f"{C['b']}  NASRITOOLS — STORE AGENT{C['x']}")
    print(f"{C['d']}  {datetime.now().strftime('%Y-%m-%d %H:%M')}{C['x']}")
    print(f"{C['b']}{'═' * 62}{C['x']}")

    token = get_token()
    print(f"\n  {C['d']}fetching shop data…{C['x']}")
    listings = fetch_listings(token)

    if mode in ("all", "health"):
        section_health(token, listings)
    if mode in ("all", "stats"):
        section_stats(token, listings)
    if mode in ("all", "plan"):
        section_plan(listings)
    if mode == "all":
        save_snapshot(listings)

    print(f"\n{C['b']}{'═' * 62}{C['x']}\n")

if __name__ == "__main__":
    main()
