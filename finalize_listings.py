import json, time, os, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
RAW        = "https://raw.githubusercontent.com/nasriakdoumi5-create/smc-bot/claude/digital-products-knowledge-yzpw50/output"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_finalized.json"


def get_token():
    t = json.loads(TOKEN_FILE.read_text())
    if time.time() >= t.get("expires_at", 0):
        r = requests.post("https://api.etsy.com/v3/public/oauth/token", data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": t["refresh_token"],
        })
        r.raise_for_status()
        t = r.json()
        t["expires_at"] = time.time() + t.get("expires_in", 3600) - 60
        TOKEN_FILE.write_text(json.dumps(t, indent=2))
        print("  Token refreshed")
    return t


def auth(t):
    return {
        "Authorization": "Bearer " + t["access_token"],
        "x-api-key": CLIENT_ID + ":" + SECRET,
    }


published = json.loads(PUB_FILE.read_text())
done = json.loads(DONE_FILE.read_text()) if DONE_FILE.exists() else {}
token = get_token()
items = list(published.items())
total = len(items)
print("Total:" + str(total) + "  Done:" + str(len(done)) + "  Left:" + str(total - len(done)))

for i, (slug, lid) in enumerate(items, 1):
    if slug in done:
        print("[" + str(i) + "/" + str(total) + "] SKIP " + slug)
        continue

    print("[" + str(i) + "/" + str(total) + "] " + slug)

    if i % 40 == 0:
        token = get_token()

    ok = True

    # Step 1: Upload xlsx file
    xlsx_url = RAW + "/" + slug + "/" + slug + ".xlsx"
    xlsx_data = requests.get(xlsx_url, timeout=60)
    if xlsx_data.status_code == 200:
        r = requests.post(
            API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid) + "/files",
            headers=auth(token),
            data={"name": slug + ".xlsx"},
            files={"file": (slug + ".xlsx", xlsx_data.content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        if r.ok:
            print("  file: OK")
        else:
            print("  file: ERR " + r.text[:100])
            ok = False
    else:
        print("  file: download ERR " + str(xlsx_data.status_code))
        ok = False

    time.sleep(0.5)

    # Step 2: Activate listing (Draft -> Active)
    r2 = requests.patch(
        API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid),
        headers={**auth(token), "Content-Type": "application/json"},
        json={"state": "active"},
    )
    if r2.ok:
        print("  activate: OK")
    else:
        print("  activate: ERR " + r2.text[:100])
        ok = False

    time.sleep(0.5)

    if ok:
        done[slug] = lid
        DONE_FILE.write_text(json.dumps(done, indent=2))

    time.sleep(0.3)

print("\nDONE: " + str(len(done)) + "/" + str(total))
print("Listings are now ACTIVE on Etsy!")
