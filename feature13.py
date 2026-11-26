import os
import json
import time
import urllib.parse
import webbrowser
import urllib.request
import urllib.error
from datetime import datetime

import phonenumbers
from phonenumbers import geocoder, carrier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "whatsapp_lookup_data")
EVIDENCE_FILE = os.path.join(DATA_DIR, "evidence.json")

R = "\033[0m"
B = "\033[94m"
C = "\033[96m"
G = "\033[92m"
Y = "\033[93m"
RED = "\033[91m"
P = "\033[95m"
W = "\033[97m"
DIM = "\033[2m"

PAGES = {
    "1": ("NUMBER INTEL", B, "BLUE SCANNER"),
    "2": ("PUBLIC PROFILE", RED, "RED ALERT"),
    "3": ("SCAM THREAT SCAN", G, "MATRIX SEARCH"),
    "4": ("EVIDENCE CENTER", P, "PURPLE CORE"),
    "5": ("BOT API REVIEW", C, "CYAN ANALYSIS")
}

def clear():
    os.system("clear")

def loading(label="INITIALIZING", color=C):
    print(color + f"\n╞══ {label} " + R, end="", flush=True)
    for i in range(12):
        print(color + "▰" + R, end="", flush=True)
        time.sleep(0.045)
    print(color + " 100%" + R)

def header(page):
    clear()
    name, color, tag = PAGES[page]
    print(color + "╭──────────────────────────────╮" + R)
    print(color + "│ SOMRAT // CYBER LOOKUP      │" + R)
    print(color + "│ WHATSAPP MODULE 13          │" + R)
    print(color + "╰──────────────────────────────╯" + R)
    print(color + f"╞═ {tag}" + R)
    print(color + f"╰─ {name}" + R)
    print(color + "─" * 30 + R)

def section(num, title, color=C):
    print(color + f"\n╭─[{num:02}] {title}" + R)
    print(color + "╰" + "─" * 28 + R)

def ask(prompt, color=C):
    return input(color + "╰─╼ " + R + prompt).strip()

def yn(prompt):
    return ask(prompt + " [Y/N]: ").lower() == "y"

def mask_number(number):
    if len(number) <= 6:
        return "*" * len(number)
    return number[:4] + "*" * (len(number) - 6) + number[-2:]

def ask_number():
    raw = ask("Phone (BD local / +country): ")
    cleaned = "".join(ch for ch in raw if ch.isdigit() or ch == "+")

    if not cleaned:
        print(RED + "╰─ NUMBER REQUIRED" + R)
        return None

    try:
        if cleaned.startswith("+"):
            number = phonenumbers.parse(cleaned, None)
        elif cleaned.startswith("00"):
            number = phonenumbers.parse("+" + cleaned[2:], None)
        else:
            number = phonenumbers.parse(cleaned, "BD")

        if not phonenumbers.is_possible_number(number):
            print(RED + "╰─ INVALID NUMBER LENGTH" + R)
            return None

        if not phonenumbers.is_valid_number(number):
            print(RED + "╰─ NUMBER NOT VALID IN PHONENUMBERS DATABASE" + R)
            return None

        return number

    except phonenumbers.NumberParseException:
        print(RED + "╰─ PARSE ERROR: CHECK COUNTRY CODE" + R)
        return None

def page_one():
    header("1")
    section(1, "NUMBER INTELLIGENCE", B)
    print(DIM + "Public / authorized review only" + R)

    number = ask_number()
    if not number:
        return

    loading("VALIDATING FORMAT", B)
    international = phonenumbers.format_number(
        number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )
    e164 = phonenumbers.format_number(
        number, phonenumbers.PhoneNumberFormat.E164
    )

    section(2, "NUMBER RESULT", G)
    print(G + "[01] FORMAT     : VALID" + R)
    print(W + "[02] NUMBER     : " + international + R)
    print(W + "[03] REGION     : " +
          (geocoder.description_for_number(number, "en") or "NOT AVAILABLE") + R)
    print(W + "[04] CARRIER    : " +
          (carrier.name_for_number(number, "en") or "NOT AVAILABLE") + R)

    section(3, "WHATSAPP STATUS", Y)
    print(Y + "[05] ACCOUNT    : NOT VERIFIED" + R)
    print(Y + "[06] API CHECK  : NOT AVAILABLE" + R)
    print(C + "[07] CHAT LINK  : https://wa.me/" + e164.lstrip("+") + R)

    section(4, "PUBLIC DETAILS", P)
    name = ask("Public name (blank = unavailable): ")
    if name:
        print(G + "[08] PUBLIC NAME : " + name + R)
    else:
        print(RED + "[08] PUBLIC NAME : NO NAME PROVIDED" + R)

    section(5, "BOT & BUSINESS", C)
    print(Y + "[09] BOT STATUS      : NOT VERIFIED" + R)
    print(Y + "[10] BUSINESS STATUS : NOT VERIFIED" + R)
    print(DIM + "Only public/authorized evidence can confirm these." + R)

    section(6, "FINAL ACTION", B)
    if yn("Open manual WhatsApp link?"):
        loading("OPENING LINK", B)
        webbrowser.open("https://wa.me/" + e164.lstrip("+"))
        print(Y + "Link does not confirm account registration." + R)
    else:
        print(DIM + "Skipped." + R)

def page_two():
    header("2")
    section(1, "PUBLIC PROFILE INTEL", RED)
    loading("PROFILE REVIEW", RED)

    number = ask("Phone (optional): ")
    name = ask("Public name: ")
    details = ask("Public business details: ")
    website = ask("Public website: ")
    source = ask("Source URL: ")

    section(2, "PROFILE REPORT", RED)
    print("[01] NUMBER :", mask_number(number) if number else "NOT PROVIDED")
    print("[02] NAME   :", name or "NOT AVAILABLE")
    print("[03] INFO   :", details or "NOT AVAILABLE")
    print("[04] WEB    :", website or "NOT AVAILABLE")
    print("[05] SOURCE :", source or "NOT PROVIDED")
    print(Y + "USER-SUPPLIED / NOT INDEPENDENTLY VERIFIED" + R)

def page_three():
    header("3")
    section(1, "SCAM & THREAT SCAN", G)
    print(Y + "Search results are leads, not proof." + R)

    number = ask("Number to search: ")
    if not number:
        print(RED + "NUMBER REQUIRED" + R)
        return

    loading("PREPARING PUBLIC SEARCH", G)
    encoded = urllib.parse.quote_plus('"' + number + '"')
    searches = [
        ("01", "GOOGLE EXACT", "https://www.google.com/search?q=" + encoded),
        ("02", "BING EXACT", "https://www.bing.com/search?q=" + encoded),
        ("03", "SCAM REPORTS", "https://www.google.com/search?q=" +
         urllib.parse.quote_plus('"' + number + '" scam OR fraud OR complaint'))
    ]

    section(2, "SEARCH SOURCES", G)
    for serial, title, url in searches:
        print(G + f"[{serial}] {title}" + R)
        print(DIM + url + R)

    if yn("Open public search in browser?"):
        for _, _, url in searches:
            webbrowser.open(url)
            time.sleep(0.3)

    print(Y + "\n╰─ Verify sources independently." + R)

def load_evidence():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(EVIDENCE_FILE):
        return []
    try:
        with open(EVIDENCE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []

def save_evidence(records):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(EVIDENCE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def page_four():
    header("4")
    section(1, "LOCAL EVIDENCE CENTER", P)
    loading("LOCAL DATABASE", P)

    records = load_evidence()
    print(P + "[1] ADD RECORD" + R)
    print(P + "[2] VIEW RECORDS" + R)
    print(Y + "[0] BACK" + R)

    choice = ask("Select: ")
    if choice == "1":
        case = ask("Case reference: ")
        note = ask("Evidence note: ")
        source = ask("Public source URL: ")
        if not note:
            print(RED + "NOTE REQUIRED" + R)
            return
        loading("SAVING LOCALLY", P)
        records.append({
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "case": case or "LOCAL-CASE",
            "note": note,
            "source": source or "NOT PROVIDED"
        })
        save_evidence(records)
        print(G + "[+] SAVED ON DEVICE" + R)
    elif choice == "2":
        loading("READING RECORDS", P)
        if not records:
            print(Y + "NO RECORDS FOUND" + R)
        for i, item in enumerate(records, 1):
            print(P + f"\n╭─ RECORD {i:02}" + R)
            print("[01] DATE :", item.get("created_at", "?"))
            print("[02] CASE :", item.get("case", "?"))
            print("[03] NOTE :", item.get("note", ""))
            print("[04] SRC  :", item.get("source", ""))

def page_five():
    header("5")
    section(1, "BUSINESS API CONNECTION REVIEW", C)
    loading("CONFIGURATION CHECK", C)

    token = os.environ.get("WA_ACCESS_TOKEN", "").strip()
    phone_id = os.environ.get("WA_PHONE_NUMBER_ID", "").strip()
    version = os.environ.get("META_GRAPH_VERSION", "v27.0").strip()

    print(C + "[01] ACCESS TOKEN     : " +
          ("CONFIGURED" if token else "NOT CONFIGURED") + R)
    print(C + "[02] BUSINESS PHONE ID: " +
          ("CONFIGURED" if phone_id else "NOT CONFIGURED") + R)
    print(C + "[03] GRAPH API VERSION: " + version + R)

    if not token or not phone_id:
        section(2, "CONFIGURATION REQUIRED", Y)
        print(Y + "Set API credentials in your local environment." + R)
        print(DIM + "Do not paste access tokens into chat or screenshots." + R)
        print("This module only reviews your own authorized business API.")
        return

    section(2, "AUTHORIZED API TEST", C)

    if not yn("Check your configured Business phone metadata?"):
        print(Y + "API test skipped." + R)
        return

    endpoint = (
        "https://graph.facebook.com/"
        + version + "/" + urllib.parse.quote(phone_id, safe="")
        + "?fields=id,display_phone_number,verified_name,quality_rating"
    )

    request = urllib.request.Request(
        endpoint,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json"
        },
        method="GET"
    )

    loading("CONNECTING TO BUSINESS API", C)

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        section(3, "API RESPONSE", G)
        print(G + "[01] CONNECTION : SUCCESS" + R)
        print("[02] PHONE ID  :", data.get("id", "NOT RETURNED"))
        print("[03] DISPLAY   :", data.get("display_phone_number", "NOT RETURNED"))
        print("[04] NAME      :", data.get("verified_name", "NOT RETURNED"))
        print("[05] QUALITY   :", data.get("quality_rating", "NOT RETURNED"))
        print(Y + "This confirms API access to the configured business asset only." + R)

    except urllib.error.HTTPError as exc:
        print(RED + "[API ERROR] HTTP STATUS: " + str(exc.code) + R)
        print(Y + "Check your business ID, token, permissions and API version." + R)

    except urllib.error.URLError:
        print(RED + "[CONNECTION ERROR] Network connection failed." + R)

    except (TimeoutError, json.JSONDecodeError, OSError):
        print(RED + "[ERROR] Request failed or response was invalid." + R)

    section(4, "SECURITY", C)
    print(DIM + "Credentials are read from environment variables." + R)
    print(DIM + "The token is never printed by this module." + R)

    if yn("Record a local API review note?"):
        note = ask("Review note: ")
        if note:
            records = load_evidence()
            records.append({
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "case": "BUSINESS-API-REVIEW",
                "note": note,
                "source": "LOCAL AUTHORIZED REVIEW"
            })
            save_evidence(records)
            print(G + "NOTE SAVED LOCALLY" + R)


def whatsapp_lookup():
    actions = {
        "1": page_one,
        "2": page_two,
        "3": page_three,
        "4": page_four,
        "5": page_five
    }

    while True:
        clear()
        print(C + "╭──────────────────────────────╮" + R)
        print(C + "│ SOMRAT // CYBER LOOKUP      │" + R)
        print(C + "│ WHATSAPP MODULE 13          │" + R)
        print(C + "╰──────────────────────────────╯" + R)
        print(C + "╞═ SELECT MODULE" + R)
        print(C + "╰─ 5 PUBLIC / LOCAL TOOLS" + R)
        print("-" * 30)

        for key, (name, color, tag) in PAGES.items():
            print(color + f" [{key}] {name}" + R)

        print(Y + " [0] EXIT MODULE" + R)
        print("-" * 30)

        choice = ask("Module: ", G)

        if choice == "0":
            loading("EXITING MODULE", C)
            break

        if choice in actions:
            loading("LOADING PAGE", PAGES[choice][1])
            actions[choice]()
            ask("Enter to return")
        else:
            print(RED + "INVALID OPTION" + R)
            ask("Enter to retry")

if __name__ == "__main__":
    whatsapp_lookup()
