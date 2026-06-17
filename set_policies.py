"""
NasriTools - Set Shop Policies
Sets return policy, FAQ, and custom policies for digital products.

Run: python set_policies.py
"""
import json, time, os, requests
from pathlib import Path

CLIENT_ID  = "pluc0garrgcjzhim0hawxf0k"
SECRET     = "hc89hlqkd6"
API        = "https://api.etsy.com/v3/application"
SHOP_ID    = 66526082
TOKEN_FILE = Path(os.path.expanduser("~")) / "etsy_token.json"

REFUND_POLICY = (
    "Because our products are instant digital downloads, we are unable to accept returns "
    "or exchanges once the file has been downloaded.\n\n"
    "However, we want you to be 100% satisfied. If you experience any of the following, "
    "please message us within 14 days of purchase and we will make it right:\n\n"
    "• The file is corrupted or won't open\n"
    "• The file is significantly different from what was described\n"
    "• You received the wrong file\n\n"
    "We do NOT offer refunds for:\n"
    "• Change of mind after download\n"
    "• Lack of the required software (Google Sheets or Microsoft Excel)\n"
    "• Issues caused by your device or software settings\n\n"
    "All our templates work in Google Sheets (free) and Microsoft Excel 2016+. "
    "If you need help getting started, just message us!"
)

SHIPPING_POLICY = (
    "This is a DIGITAL DOWNLOAD — nothing will be shipped to you.\n\n"
    "After purchase, your file is available immediately in your Etsy account under "
    "Purchases & Reviews. You can download it as many times as you need, on any device.\n\n"
    "No waiting, no shipping costs, no customs."
)

ADDITIONAL_INFO = (
    "ABOUT OUR TEMPLATES\n\n"
    "All NasriTools templates are designed to work in:\n"
    "✅ Google Sheets (free - recommended)\n"
    "✅ Microsoft Excel 2016 or newer\n\n"
    "HOW TO USE\n"
    "1. Download the .xlsx file from your Etsy Purchases\n"
    "2. Open in Google Sheets: File → Import → Upload\n"
    "3. Fill in the yellow/highlighted cells\n"
    "4. Your dashboard updates automatically!\n\n"
    "NEED HELP?\n"
    "Message us on Etsy — we respond within 24 hours, 7 days a week."
)


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


def main():
    print("\n" + "=" * 55)
    print("  NasriTools - Shop Policies Setup")
    print("=" * 55 + "\n")

    token = get_token()
    headers = {**auth(token), "Content-Type": "application/json"}

    # Set return policy via shop update
    print("Setting shop policies...")
    r = requests.put(
        API + "/shops/" + str(SHOP_ID),
        headers=headers,
        json={
            "policy_refunds":        REFUND_POLICY,
            "policy_shipping_info":  SHIPPING_POLICY,
            "policy_additional":     ADDITIONAL_INFO,
        },
    )
    if r.ok:
        print("  Policies: OK")
    else:
        print("  Policies: ERR " + r.text[:200])

    time.sleep(0.5)

    # Verify
    r2 = requests.get(API + "/shops/" + str(SHOP_ID), headers=auth(token))
    if r2.ok:
        shop = r2.json()
        has_refund = bool(shop.get("policy_refunds", "").strip())
        has_ship   = bool(shop.get("policy_shipping_info", "").strip())
        print(f"  Refund policy   : {'SET' if has_refund else 'MISSING'}")
        print(f"  Shipping policy : {'SET' if has_ship else 'MISSING'}")
    else:
        print("  Verify: ERR " + r2.text[:100])

    print("\n" + "=" * 55)
    print("  Done! Policies are live on your shop.")
    print("=" * 55 + "\n")
    print("Next steps:")
    print("  1. Add shop logo (500x500px) in Etsy dashboard")
    print("  2. Add shop banner (3360x840px) in Etsy dashboard")
    print("  3. Run: python verify_shop.py")


if __name__ == "__main__":
    main()
