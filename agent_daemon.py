"""
agent_daemon.py — the autonomous NasriTools store guardian.

Runs unattended (Windows Task Scheduler, once a day). It:
  • checks the shop is alive and not suspended
  • watches the billing balance — the thing that killed the shop once
  • re-activates listings Etsy deactivated on its own
  • tracks favourites / orders and notices when they move
  • writes a dated report to agent_reports/
  • pops a Windows notification ONLY when you need to act

Install once:   powershell -ExecutionPolicy Bypass -File install_agent.ps1
Run manually:   python agent_daemon.py

Safe by default: it never spends money and never deletes anything.
"""
import json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests

# ── config ──────────────────────────────────────────────────────────────
CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
SHOP_ID    = 66526082
API        = "https://api.etsy.com/v3/application"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

ROOT       = Path(__file__).parent
REPORTS    = ROOT / "agent_reports"
STATE      = ROOT / "agent_state.json"

AUTO_REACTIVATE = True    # re-enable listings Etsy switched off (free)
AUTO_RENEW      = False   # renewing costs $0.20 each — stays off on purpose
WARN_DAYS       = 21      # flag renewals coming up within N days

STATES = ["active", "inactive", "draft", "expired", "sold_out"]

log_lines = []
alerts    = []      # things that need the owner

def say(line=""):
    print(line)
    log_lines.append(line)

def alert(line):
    say(f"!! {line}")
    alerts.append(line)

# ── auth ────────────────────────────────────────────────────────────────
def get_token():
    if not TOKEN_FILE.exists():
        alert(f"No Etsy token at {TOKEN_FILE}. Run: python etsy_reauth.py")
        finish(fatal=True)
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0) - 60:
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token", "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        }, timeout=30)
        if not r.ok:
            alert(f"Etsy token refresh failed ({r.status_code}). "
                  "The shop may be suspended. Run: python etsy_reauth.py")
            finish(fatal=True)
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
    return t

def H(token):
    return {"Authorization": "Bearer " + token["access_token"],
            "x-api-key": CLIENT_ID + ":" + SECRET}

def api(token, path, **params):
    try:
        r = requests.get(f"{API}{path}", headers=H(token), params=params, timeout=30)
        return (r.json() if r.ok else None), r.status_code
    except requests.RequestException as e:
        return None, str(e)

# ── checks ──────────────────────────────────────────────────────────────
def check_shop(token):
    shop, code = api(token, f"/shops/{SHOP_ID}")
    if not shop:
        alert(f"Cannot reach the shop (HTTP {code}). Account may be suspended — "
              "open etsy.com/your/account/payments")
        return None
    say(f"shop        : {shop.get('shop_name')} — reachable")
    say(f"favourites  : {shop.get('num_favorers', 0)}")
    say(f"active count: {shop.get('listing_active_count', 0)}")
    if shop.get("is_vacation"):
        alert("Shop is in VACATION MODE — buyers cannot buy anything.")
    return shop

def check_billing(token):
    led, code = api(token, f"/shops/{SHOP_ID}/payment-account/ledger-entries",
                    limit=10, min_created=0)
    if led and led.get("results"):
        e = led["results"][0]
        bal = e.get("balance")
        cur = e.get("currency", "")
        if bal is not None:
            b = bal / 100
            if b < -0.5:
                alert(f"YOU OWE {abs(b):.2f} {cur} TO ETSY. Pay it now or the shop "
                      "gets suspended: etsy.com/your/account/payments")
            else:
                say(f"balance     : {b:.2f} {cur}")
    elif code in (401, 403):
        say("balance     : no billing scope (run python etsy_reauth.py to enable)")
    else:
        say("balance     : nothing on the ledger yet")

def fetch_listings(token):
    out, seen = [], set()
    for state in STATES:
        offset = 0
        while True:
            d, _ = api(token, f"/shops/{SHOP_ID}/listings",
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

def days_left(l):
    ts = l.get("ending_timestamp") or l.get("expiry_timestamp")
    if not ts:
        return None
    return (datetime.fromtimestamp(ts, timezone.utc) - datetime.now(timezone.utc)).days

def check_listings(token, listings, prev):
    by_state = {}
    for l in listings:
        by_state[l["_state"]] = by_state.get(l["_state"], 0) + 1
    say("listings    : " + ", ".join(f"{k} {v}" for k, v in sorted(by_state.items())))

    active   = [l for l in listings if l["_state"] == "active"]
    inactive = [l for l in listings if l["_state"] == "inactive"]

    # something switched our listings off
    known = set(prev.get("published_ids", []))
    unexpected = [l for l in inactive if str(l["listing_id"]) in known] if known else inactive

    if unexpected and AUTO_REACTIVATE:
        alert(f"{len(unexpected)} listing(s) were deactivated — reactivating them")
        fixed = 0
        for l in unexpected:
            r = requests.patch(
                f"{API}/shops/{SHOP_ID}/listings/{l['listing_id']}",
                headers={**H(token), "Content-Type": "application/json"},
                json={"state": "active"}, timeout=30)
            if r.ok:
                fixed += 1
            time.sleep(0.5)
        say(f"reactivated : {fixed}/{len(unexpected)}")
        if fixed < len(unexpected):
            alert("Some listings refused to reactivate — check the shop manually.")
    elif unexpected:
        alert(f"{len(unexpected)} listing(s) are inactive (auto-reactivate is off).")

    soon = [l for l in active if (days_left(l) or 999) <= WARN_DAYS]
    if soon:
        say(f"renewals    : {len(soon)} within {WARN_DAYS}d "
            f"(~${len(soon) * 0.20:.2f} in fees)")
        if len(soon) * 0.20 >= 5:
            alert(f"${len(soon) * 0.20:.2f} of renewal fees are coming up. "
                  "Make sure a payment method is on file.")
    return active

def check_movement(token, active, prev):
    favs = sum(l.get("num_favorers", 0) for l in active)
    say(f"total favs  : {favs}")

    rec, code = api(token, f"/shops/{SHOP_ID}/receipts", limit=5)
    orders = rec.get("count", 0) if rec else None
    if orders is not None:
        say(f"orders      : {orders}")

    p_favs   = prev.get("favourites")
    p_orders = prev.get("orders")

    if p_favs is not None and favs != p_favs:
        say(f"change      : favourites {favs - p_favs:+d} since last check")
    if p_orders is not None and orders is not None and orders > p_orders:
        alert(f"NEW SALE! {orders - p_orders} new order(s) — go say thanks "
              "and make sure the file downloaded fine.")
    return favs, orders

# ── output ──────────────────────────────────────────────────────────────
def notify(title, body):
    """Windows balloon notification — works on every Windows 10/11."""
    if os.name != "nt":
        return
    body  = body.replace("'", " ").replace('"', " ")[:250]
    title = title.replace("'", " ")[:60]
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$n = New-Object System.Windows.Forms.NotifyIcon;"
        "$n.Icon = [System.Drawing.SystemIcons]::Information;"
        f"$n.BalloonTipTitle = '{title}';"
        f"$n.BalloonTipText = '{body}';"
        "$n.Visible = $true; $n.ShowBalloonTip(15000); Start-Sleep -Seconds 12;"
        "$n.Dispose()"
    )
    try:
        subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden",
                        "-Command", ps], timeout=40,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def finish(fatal=False):
    REPORTS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    path  = REPORTS / f"{stamp}.txt"
    header = [
        "NasriTools — store agent",
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        "=" * 52, "",
    ]
    body = header + log_lines
    if alerts:
        body += ["", "=" * 52, "NEEDS YOUR ATTENTION:", ""]
        body += [f"  - {a}" for a in alerts]
    path.write_text("\n".join(body), encoding="utf-8")

    print(f"\nreport: {path}")

    if alerts:
        notify("NasriTools — action needed", alerts[0])
    sys.exit(1 if fatal else 0)

# ── main ────────────────────────────────────────────────────────────────
def main():
    prev = {}
    if STATE.exists():
        try:
            hist = json.loads(STATE.read_text()).get("history", [])
            prev = hist[-1] if hist else {}
        except Exception:
            prev = {}

    say(f"run         : {datetime.now():%Y-%m-%d %H:%M}")
    token = get_token()

    shop = check_shop(token)
    if not shop:
        finish(fatal=True)

    check_billing(token)
    listings = fetch_listings(token)
    active   = check_listings(token, listings, prev)
    favs, orders = check_movement(token, active, prev)

    # persist snapshot
    hist = []
    if STATE.exists():
        try:
            hist = json.loads(STATE.read_text()).get("history", [])
        except Exception:
            hist = []
    hist.append({
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "active": len(active),
        "total": len(listings),
        "favourites": favs,
        "orders": orders,
        "published_ids": [str(l["listing_id"]) for l in active],
    })
    STATE.write_text(json.dumps({"history": hist[-90:]}, indent=2))

    if not alerts:
        say("")
        say("all good — nothing needs you today")
    finish()

if __name__ == "__main__":
    main()
