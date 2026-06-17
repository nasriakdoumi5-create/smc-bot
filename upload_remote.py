import json, time, os, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
RAW        = "https://raw.githubusercontent.com/nasriakdoumi5-create/smc-bot/claude/digital-products-knowledge-yzpw50/output"
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"
PUB_FILE   = Path(os.path.expanduser("~")) / "etsy_published.json"
DONE_FILE  = Path(os.path.expanduser("~")) / "etsy_uploaded.json"
SLOTS      = ["_01_hero", "_02_included", "_03_how", "_04_features", "_05_cta"]


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
    for rank, slot in enumerate(SLOTS, 1):
        url = RAW + "/" + slug + "/" + slug + slot + ".jpg"
        img = requests.get(url, timeout=30)
        if img.status_code != 200:
            print("  img" + str(rank) + ": download ERR " + str(img.status_code))
            ok = False
            continue
        r = requests.post(
            API + "/shops/" + str(SHOP_ID) + "/listings/" + str(lid) + "/images",
            headers=auth(token),
            data={"rank": rank, "overwrite": "true"},
            files={"image": (slug + slot + ".jpg", img.content, "image/jpeg")},
        )
        if r.ok:
            print("  img" + str(rank) + ": OK")
        else:
            print("  img" + str(rank) + ": ERR " + r.text[:80])
            ok = False
        time.sleep(0.4)
    if ok:
        done[slug] = lid
        DONE_FILE.write_text(json.dumps(done, indent=2))
    time.sleep(0.2)

print("\nDONE: " + str(len(done)) + "/" + str(total))
