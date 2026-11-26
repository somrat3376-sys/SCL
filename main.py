from voice_assistant import welcome, speak_result
from feature07 import impersonation_safety_check
from feature06 import fake_profile_safety_check
from feature08 import post_evidence_collector
from feature09 import link_safety_analyzer
import os
import time
import platform
import shutil
import subprocess
import phonenumbers
import urllib.parse
from phonenumbers import geocoder, carrier, PhoneNumberType

GREEN = "\033[92m"
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def loading(label="INITIALIZING", color=CYAN):
    blocks = 12
    print(f"\n{color}╭─[ {label} ]{RESET}")
    for i in range(blocks + 1):
        bar = "▰" * i + "▱" * (blocks - i)
        percent = i * 100 // blocks
        print(f"\r{color}╰─ {bar} {percent:3d}%{RESET}", end="", flush=True)
        time.sleep(0.025)
    print("\n")


def banner():
    os.system("clear")
    print(CYAN + r"""
╭──────────────────────────────────────────────────────────╮
│   ███████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ████████╗│
│   ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝│
│   ███████╗██║   ██║██╔████╔██║██████╔╝███████║   ██║   │
│   ╚════██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║   ██║   │
│   ███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   │
│   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   │
╰──────────────────────────────────────────────────────────╯
""" + RESET)
    print(GREEN + "          SOMRAT VAI YT // CYBER LOOKUP" + RESET)
    print(YELLOW + "       PUBLIC INFORMATION & SAFETY TOOLKIT" + RESET)
    print(CYAN + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + RESET)


def get_android_property(prop):
    try:
        result = subprocess.run(
            ["getprop", prop],
            capture_output=True,
            text=True,
            timeout=3
        )
        return result.stdout.strip() or "Information unavailable"
    except Exception:
        return "Information unavailable"


def device_information():
    banner()
    print(CYAN + "       DEVICE INFORMATION" + RESET)
    print("-" * 45)

    manufacturer = get_android_property("ro.product.manufacturer")
    model = get_android_property("ro.product.model")
    android = get_android_property("ro.build.version.release")
    sdk = get_android_property("ro.build.version.sdk")

    print(f"{GREEN}Manufacturer :{RESET} {manufacturer}")
    print(f"{GREEN}Device Model :{RESET} {model}")
    print(f"{GREEN}Android      :{RESET} {android}")
    print(f"{GREEN}Android SDK  :{RESET} {sdk}")
    print(f"{GREEN}Python       :{RESET} {platform.python_version()}")
    print(f"{GREEN}Architecture :{RESET} {platform.machine()}")
    print(f"{GREEN}CPU Cores    :{RESET} {os.cpu_count()}")

    print("\n" + CYAN + "RAM INFORMATION" + RESET)

    try:
        with open("/proc/meminfo") as f:
            memory = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    memory[parts[0].rstrip(":")] = int(parts[1])

        total = memory.get("MemTotal", 0) / 1024
        available = memory.get("MemAvailable", 0) / 1024

        print(f"Total RAM     : {total:.0f} MB")
        print(f"Available RAM : {available:.0f} MB")
    except Exception:
        print("RAM information unavailable.")

    print("\n" + CYAN + "STORAGE INFORMATION" + RESET)

    try:
        usage = shutil.disk_usage(os.path.expanduser("~"))
        print(f"Total Storage : {usage.total / (1024**3):.2f} GB")
        print(f"Free Storage  : {usage.free / (1024**3):.2f} GB")
    except Exception:
        print("Storage information unavailable.")

    print("\n" + YELLOW +
          "Battery information requires separate Android access." +
          RESET)
    print("-" * 45)

    ram_summary = (
        f"মোট র‍্যাম {total:.0f} মেগাবাইট এবং "
        f"ব্যবহারযোগ্য র‍্যাম {available:.0f} মেগাবাইট।"
        if "total" in locals() and "available" in locals()
        else "র‍্যামের তথ্য পাওয়া যায়নি।"
    )

    storage_summary = (
        f"মোট স্টোরেজ {usage.total / (1024**3):.2f} জিবি এবং "
        f"ফাঁকা স্টোরেজ {usage.free / (1024**3):.2f} জিবি।"
        if "usage" in locals()
        else "স্টোরেজের তথ্য পাওয়া যায়নি।"
    )

    speak_result(
        f"আপনার ডিভাইসের তথ্য পাওয়া গেছে। "
        f"নির্মাতা {manufacturer}, মডেল {model}, "
        f"অ্যান্ড্রয়েড সংস্করণ {android}, "
        f"পাইথন সংস্করণ {platform.python_version()}, "
        f"প্রসেসর কোর {os.cpu_count()}। "
        f"{ram_summary} {storage_summary}"
    )



def number_lookup():
    banner()
    print(CYAN + "       NUMBER LOOKUP" + RESET)
    print("-" * 45)
    print(YELLOW + "Public number information only." + RESET)

    raw = input("\nPhone Number (+880...): ").strip()

    try:
        cleaned = raw.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if not cleaned:
            raise ValueError("Phone number is required.")

        if not cleaned.lstrip("+").isdigit() or cleaned.count("+") > 1 or ("+" in cleaned and not cleaned.startswith("+")):
            raise ValueError("Invalid phone number format.")

        region = None if cleaned.startswith("+") else "BD"
        number = phonenumbers.parse(cleaned, region)

        if not phonenumbers.is_possible_number(number):
            raise ValueError("Invalid phone number length.")

        print("\n" + CYAN + "NUMBER INFORMATION" + RESET)
        print("-" * 45)

        country = geocoder.description_for_number(number, "en") or "Unknown"
        region_code = phonenumbers.region_code_for_number(number) or "Unknown"

        types = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed Line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line / Mobile",
            PhoneNumberType.TOLL_FREE: "Toll Free",
            PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            PhoneNumberType.SHARED_COST: "Shared Cost",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            PhoneNumberType.PAGER: "Pager",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "Voicemail",
        }

        number_kind = types.get(phonenumbers.number_type(number), "Unknown")
        carrier_name = carrier.name_for_number(number, "en")

        print(f"{GREEN}International :{RESET} {phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"{GREEN}National      :{RESET} {phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)}")
        print(f"{GREEN}Country       :{RESET} {country}")
        print(f"{GREEN}Region Code   :{RESET} {region_code}")
        print(f"{GREEN}Calling Code  :{RESET} +{number.country_code}")
        print(f"{GREEN}Number Type   :{RESET} {number_kind}")
        print(f"{GREEN}Valid Number  :{RESET} {'Yes' if phonenumbers.is_valid_number(number) else 'No'}")

        print(f"{GREEN}Carrier Label :{RESET} {carrier_name or 'Not available'}")
        if carrier_name:
            print(YELLOW + "Note: Carrier label is database-based; it does not confirm the current operator." + RESET)

        print("-" * 45)

    except phonenumbers.NumberParseException:
        print(RED + "\nInvalid phone number format." + RESET)
    except ValueError as error:
        print(RED + "\n" + str(error) + RESET)
    except Exception as error:
        print(RED + "\nLookup error: " + str(error) + RESET)




def public_number_search():
    from urllib.parse import quote_plus

    banner()
    print(CYAN + "       PUBLIC NUMBER SEARCH" + RESET)
    print("-" * 45)
    print(YELLOW + "Search publicly listed organization contact information only." + RESET)

    name = input("\nOrganization Name: ").strip()

    if not name:
        print(RED + "Organization name is required." + RESET)
        return

    queries = [
        ("Public Contact Search",
         'https://www.google.com/search?q=' +
         quote_plus('"' + name + '" official contact phone')),
        ("Official Website Contact",
         'https://www.google.com/search?q=' +
         quote_plus('"' + name + '" official website contact')),
        ("Public Directory Search",
         'https://www.google.com/search?q=' +
         quote_plus('"' + name + '" public contact number')),
    ]

    print("\n" + CYAN + "PUBLIC SEARCH LINKS" + RESET)
    print("-" * 45)

    for title, url in queries:
        print("\n" + GREEN + title + RESET)
        print(url)

    print("\n" + YELLOW +
          "Verify results using the organization's official website." +
          RESET)
    print("This tool does not independently verify phone numbers.")
    print("-" * 45)



def spam_check():
    banner()
    print(CYAN + "       SPAM CHECK" + RESET)
    print("-" * 45)

    raw = input("Phone Number (+880...): ").strip()

    try:
        cleaned = raw.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if not cleaned or not cleaned.lstrip("+").isdigit():
            raise ValueError("Invalid phone number format.")

        region = None if cleaned.startswith("+") else "BD"
        number = phonenumbers.parse(cleaned, region)

        if not phonenumbers.is_valid_number(number):
            raise ValueError("Invalid phone number.")

        phone = phonenumbers.format_number(
            number, phonenumbers.PhoneNumberFormat.E164
        )

        query = urllib.parse.quote_plus(
            '"' + phone + '" spam OR scam OR fraud'
        )

        searches = [
            ("Google Public Spam Search",
             "https://www.google.com/search?q=" + query),
            ("Google Exact Number Search",
             "https://www.google.com/search?q=" +
             urllib.parse.quote_plus('"' + phone + '"')),
            ("Bing Public Search",
             "https://www.bing.com/search?q=" + query),
        ]

        print("\n" + CYAN + "PUBLIC SPAM SEARCH RESULTS" + RESET)
        print("-" * 45)
        print("Number:", phone)
        print("Number Format: Valid")
        print("Verified Spam Reports: Not available")
        print("Public Report Count: Not independently verified")

        for title, url in searches:
            print("\n" + GREEN + title + RESET)
            print(url)

        print("\n" + YELLOW +
              "WARNING: Search results are not proof of fraud." + RESET)
        print("User-submitted reports may be inaccurate or unverified.")
        print("Verify information before making any judgement.")
        print("-" * 45)

    except (ValueError, phonenumbers.NumberParseException) as error:
        print(RED + "\nInvalid Input: " + str(error) + RESET)
    except Exception as error:
        print(RED + "\nSpam Check Error: " + str(error) + RESET)




def public_facebook_post_search():
    from urllib.parse import quote_plus

    print("\\n[04] Public Keyword Search")
    keyword = input("Enter public topic keyword: ").strip()

    if not keyword:
        print("Keyword is empty.")
        return

    q = quote_plus(keyword)

    print("\\nFacebook Search:")
    print("https://www.facebook.com/search/posts/?q=" + q)

    print("\\nGoogle Search:")
    print("https://www.google.com/search?q=site%3Afacebook.com+" + q)

    print("\\nBing Search:")
    print("https://www.bing.com/search?q=site%3Afacebook.com+" + q)


from feature10 import own_call_log_analysis
from feature13 import whatsapp_lookup
from api_config import feature_status


def menu():
    options = [
        "NUMBER LOOKUP",
        "PUBLIC NUMBER SEARCH",
        "SPAM CHECK",
        "PUBLIC FACEBOOK POST SEARCH",
        "PROFILE LINK FINDER",
        "FAKE PROFILE CHECK",
        "IMPERSONATION CHECK",
        "POST EVIDENCE COLLECTOR",
        "LINK SAFETY ANALYZER",
        "OWN CALL LOG ANALYSIS",
        "DEVICE INFORMATION",
        "REPORT ASSISTANT",
        "WHATSAPP LOOKUP",
        "API CONFIGURATION",
    ]

    while True:
        banner()
        loading("MAIN MENU", CYAN)

        print(CYAN + "╭────────────────────── MAIN MENU ──────────────────────╮" + RESET)

        for i, option in enumerate(options, 1):
            color = GREEN if i % 2 else CYAN
            print(f"│  {color}[{i:02d}]{RESET} {option:<45}│")

        print(CYAN + "├───────────────────────────────────────────────────────┤" + RESET)
        print(f"│  {RED}[00]{RESET} EXIT{' '*48}│")
        print(CYAN + "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯" + RESET)

        choice = input(GREEN + "\n╰─ SELECT OPTION: " + RESET).strip()

        if choice == "00":
            loading("SHUTTING DOWN", RED)
            print(YELLOW + "Session closed. Goodbye!" + RESET)
            break

        if choice.isdigit() and 1 <= int(choice) <= len(options):
            choice = f"{int(choice):02d}"
            selected = options[int(choice) - 1]

            print(f"\n{CYAN}╭─ SELECTED: {selected}{RESET}")
            loading("LOADING FEATURE", GREEN)

            if choice == "01":
                try:
                    number_lookup()
                except KeyboardInterrupt:
                    print("\\n" + YELLOW + "NUMBER LOOKUP CANCELLED" + RESET)
                except Exception as error:
                    print(RED + "NUMBER LOOKUP ERROR: " + str(error) + RESET)
            elif choice == "02":
                public_number_search()
            elif choice == "03":
                spam_check()
            elif choice == "04":
                banner()
                loading("PUBLIC POST SEARCH", CYAN)
                public_facebook_post_search()
            elif choice == "05":
                profile_link_finder()
            elif choice == "06":
                fake_profile_safety_check()
            elif choice == "07":
                impersonation_safety_check()
            elif choice == "08":
                post_evidence_collector()
            elif choice == "09":
                link_safety_analyzer()
            elif choice == "10":
                own_call_log_analysis()
            elif choice == "11":
                device_information()
            elif choice == "12":
                print(YELLOW + "REPORT ASSISTANT: Handler not connected." + RESET)
            elif choice == "13":
                whatsapp_lookup()
            elif choice == "14":
                banner()
                loading("API CONFIGURATION", CYAN)
                feature_status()

            voice_summaries = {
                "01": "নাম্বার তথ্য পরীক্ষা সম্পন্ন হয়েছে। সাধারণ নম্বরের তথ্য স্ক্রিনে দেখানো হয়েছে।",
                "02": "পাবলিক নম্বর সার্চ সম্পন্ন হয়েছে। প্রতিষ্ঠানের প্রকাশ্য যোগাযোগের সার্চ লিংক দেখানো হয়েছে।",
                "03": "স্প্যাম চেক সম্পন্ন হয়েছে। পাবলিক সার্চের ফলাফল দেখানো হয়েছে। এগুলো নিশ্চিত প্রমাণ নয়।",
                "04": "পাবলিক পোস্ট সার্চ সম্পন্ন হয়েছে। সার্চ লিংক স্ক্রিনে দেখানো হয়েছে।",
                "05": "প্রোফাইল লিংক সার্চ সম্পন্ন হয়েছে। প্রকাশ্য প্রোফাইলের সার্চ লিংক দেখানো হয়েছে।",
                "06": "প্রোফাইল নিরাপত্তা পরীক্ষা সম্পন্ন হয়েছে। সতর্কতার লক্ষণগুলো স্ক্রিনে দেখুন।",
                "07": "ডোমেইন তথ্য সংগ্রহ সম্পন্ন হয়েছে। সংগৃহীত তথ্য স্ক্রিনে দেখানো হয়েছে।",
                "08": "ইভিডেন্স ব্যবস্থাপনা সম্পন্ন হয়েছে। আপনার নির্বাচিত কাজের ফলাফল স্ক্রিনে দেখানো হয়েছে।",
                "09": "লিংক নিরাপত্তা পরীক্ষা সম্পন্ন হয়েছে। ফলাফল ও সতর্কতা স্ক্রিনে দেখুন।",
                "10": "কল লগ বিশ্লেষণ সম্পন্ন হয়েছে। ব্যক্তিগত তথ্য গোপন রেখে ফলাফল স্ক্রিনে দেখুন।",
                            "14": "এপিআই কনফিগারেশন পরীক্ষা সম্পন্ন হয়েছে। কনফিগারেশনের অবস্থা স্ক্রিনে দেখানো হয়েছে। গোপন তথ্য পড়ে শোনানো হবে না।"
            }

            if choice in voice_summaries:
                speak_result(voice_summaries[choice])

            input(CYAN + "\n╰─ Press Enter to return to Main Menu..." + RESET)

        else:
            print(RED + "\n╭─ INVALID OPTION" + RESET)
            input(YELLOW + "╰─ Press Enter to try again..." + RESET)



def profile_link_finder():
    banner()
    print(CYAN + "       OFFICIAL PROFILE LINK FINDER" + RESET)
    print("-" * 45)
    print("Search public organization or brand pages only.")

    name = input("\nOrganization/Brand Name: ").strip()
    if not name:
        print(RED + "Name is required." + RESET)
        return

    q = urllib.parse.quote_plus('"' + name + '" official')
    sites = [
        ("Facebook", "https://www.google.com/search?q=" + urllib.parse.quote_plus("site:facebook.com " + name + " official")),
        ("Instagram", "https://www.google.com/search?q=" + urllib.parse.quote_plus("site:instagram.com " + name + " official")),
        ("LinkedIn", "https://www.google.com/search?q=" + urllib.parse.quote_plus("site:linkedin.com " + name + " official")),
        ("Website", "https://www.google.com/search?q=" + q),
    ]

    print("\n" + CYAN + "PUBLIC SEARCH LINKS" + RESET)
    for title, url in sites:
        print("\n" + GREEN + title + RESET)
        print(url)

    print("\n" + YELLOW + "Verify links manually. They do not confirm identity." + RESET)
    print("-" * 45)

if __name__ == "__main__":
    welcome()
    menu()
