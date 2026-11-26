import json
import os
import uuid
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

# SOMRAT CYBER LOOKUP - FEATURE 08
# Evidence Organizer

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

DATA_FILE = "evidence_cases.json"


def banner():
    os.system("clear")
    print(CYAN + r"""
  ____ ___  __  __ ____      _  _____
 / ___/ _ \|  \/  |  _ \    / \|_   _|
| |  | | | | |\/| | |_) |  / _ \ | |
| |__| |_| | |  | |  __/  / ___ \| |
 \____\___/|_|  |_|_|    /_/   \_\_|

""" + RESET)
    print(YELLOW + "       SOMRAT VAI YT - FEATURE 08" + RESET)
    print(GREEN + "          DIGITAL EVIDENCE CENTER" + RESET)
    print("-" * 48)


def load_cases():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print(RED + "Error: Evidence database could not be read." + RESET)
        return None


def save_cases(cases):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(cases, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        print(RED + "Error: Could not save evidence database." + RESET)
        return False


def pause():
    input("\nPress Enter to continue...")


def find_case(cases, case_id):
    for case in cases:
        if case.get("case_id", "").upper() == case_id.upper():
            return case
    return None


def create_case(cases):
    banner()
    print(YELLOW + "CREATE NEW EVIDENCE CASE" + RESET)

    title = input("Case Title: ").strip()
    if not title:
        print(RED + "Invalid Input: Case title is required." + RESET)
        return

    description = input("Evidence Description: ").strip()
    incident_date = input("Incident Date (YYYY-MM-DD): ").strip()

    if incident_date:
        try:
            datetime.strptime(incident_date, "%Y-%m-%d")
        except ValueError:
            print(RED + "Invalid Input: Use YYYY-MM-DD." + RESET)
            return

    screenshot = input("Screenshot Description: ").strip()
    links_text = input("Reference Links (comma separated): ").strip()
    notes = input("Personal Notes: ").strip()

    links = [x.strip() for x in links_text.split(",") if x.strip()]

    case = {
        "case_id": uuid.uuid4().hex[:8].upper(),
        "title": title,
        "description": description,
        "incident_date": incident_date,
        "screenshot_description": screenshot,
        "reference_links": links,
        "personal_notes": notes,
        "profile_records": [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "updated_at": datetime.now().isoformat(timespec="seconds")
    }

    cases.append(case)

    if save_cases(cases):
        print(GREEN + "\n[SUCCESS] Evidence case saved." + RESET)
        print("Case ID:", case["case_id"])


def display_case(case):
    print(CYAN + "\n" + "=" * 48 + RESET)
    print(YELLOW + "CASE ID: " + RESET + case["case_id"])
    print("Title:", case.get("title", ""))
    print("Incident Date:", case.get("incident_date", ""))
    print("Description:", case.get("description", ""))
    print("Screenshot:", case.get("screenshot_description", ""))
    print("Reference Links:")

    for link in case.get("reference_links", []):
        print(" -", link)

    print("Personal Notes:", case.get("personal_notes", ""))

    records = case.get("profile_records", [])
    print("\nFake Profile Records:", len(records))

    for record in records:
        print(" - Name:", record.get("name", ""))
        print("   Link:", record.get("link", ""))
        print("   Notes:", record.get("notes", ""))

    print(CYAN + "=" * 48 + RESET)


def view_cases(cases):
    banner()
    print(YELLOW + "SAVED EVIDENCE CASES" + RESET)

    if not cases:
        print(YELLOW + "No saved cases found." + RESET)
        return

    for case in cases:
        display_case(case)


def search_case(cases):
    banner()
    print(YELLOW + "SEARCH EVIDENCE BY CASE ID" + RESET)

    case_id = input("Enter Case ID: ").strip()
    case = find_case(cases, case_id)

    if case:
        display_case(case)
    else:
        print(RED + "Error: Case not found." + RESET)


def update_case(cases):
    banner()
    print(YELLOW + "UPDATE EXISTING CASE" + RESET)

    case_id = input("Enter Case ID: ").strip()
    case = find_case(cases, case_id)

    if not case:
        print(RED + "Error: Case not found." + RESET)
        return

    print("""
[1] Case Title
[2] Evidence Description
[3] Incident Date
[4] Screenshot Description
[5] Reference Links
[6] Personal Notes
[0] Cancel
""")

    choice = input("Select Field: ").strip()

    fields = {
        "1": "title",
        "2": "description",
        "4": "screenshot_description",
        "6": "personal_notes"
    }

    if choice in fields:
        value = input("Enter New Value: ").strip()
        if not value:
            print(RED + "Invalid Input." + RESET)
            return
        case[fields[choice]] = value

    elif choice == "3":
        value = input("New Incident Date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            print(RED + "Invalid Input: Use YYYY-MM-DD." + RESET)
            return
        case["incident_date"] = value

    elif choice == "5":
        value = input("New Reference Links (comma separated): ")
        case["reference_links"] = [
            x.strip() for x in value.split(",") if x.strip()
        ]

    elif choice == "0":
        return
    else:
        print(RED + "Invalid Input." + RESET)
        return

    case["updated_at"] = datetime.now().isoformat(timespec="seconds")

    if save_cases(cases):
        print(GREEN + "[SUCCESS] Case updated." + RESET)


def delete_case(cases):
    banner()
    print(RED + "DELETE EVIDENCE CASE" + RESET)

    case_id = input("Enter Case ID: ").strip()
    case = find_case(cases, case_id)

    if not case:
        print(RED + "Error: Case not found." + RESET)
        return

    print("Case:", case.get("title", ""))
    confirm = input("Type DELETE to confirm: ").strip()

    if confirm != "DELETE":
        print(YELLOW + "Deletion cancelled." + RESET)
        return

    cases.remove(case)

    if save_cases(cases):
        print(GREEN + "[SUCCESS] Case deleted." + RESET)


def add_profile_record(cases):
    banner()
    print(YELLOW + "FAKE PROFILE EVIDENCE RECORD" + RESET)

    case_id = input("Enter Case ID: ").strip()
    case = find_case(cases, case_id)

    if not case:
        print(RED + "Error: Case not found." + RESET)
        return

    name = input("Displayed Profile/Page Name: ").strip()
    link = input("Public Profile/Page URL: ").strip()
    notes = input("Why is this profile suspicious?: ").strip()

    if not name or not link:
        print(RED + "Invalid Input: Name and link are required." + RESET)
        return

    if not link.startswith(("https://", "http://")):
        print(RED + "Invalid Input: Enter a valid HTTP/HTTPS link." + RESET)
        return

    record = {
        "name": name,
        "link": link,
        "notes": notes,
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "status": "Unverified"
    }

    case.setdefault("profile_records", []).append(record)
    case["updated_at"] = datetime.now().isoformat(timespec="seconds")

    if save_cases(cases):
        print(GREEN + "[SUCCESS] Profile evidence saved." + RESET)
        print(YELLOW + "Status: Unverified - manual review required." + RESET)


def public_name_search():
    banner()
    print(YELLOW + "PUBLIC FACEBOOK NAME SEARCH" + RESET)

    name = input("Enter Name to Search: ").strip()

    if not name:
        print(RED + "Invalid Input." + RESET)
        return

    query = quote_plus('"' + name + '"')

    links = [
        "https://www.facebook.com/search/people/?q=" + query,
        "https://www.google.com/search?q=" +
        quote_plus("site:facebook.com " + '"' + name + '"'),
        "https://www.bing.com/search?q=" +
        quote_plus("site:facebook.com " + '"' + name + '"')
    ]

    print(CYAN + "\nPUBLIC SEARCH LINKS" + RESET)

    for number, link in enumerate(links, 1):
        print(f"\n[{number}] {link}")

    print(YELLOW + "\nSearch results are not a complete database.")
    print("Matching names do not prove an account is fake.")
    print("Review results manually and record relevant public links." + RESET)

    open_choice = input("\nOpen a search link? (1-3 / 0): ").strip()

    if open_choice in ("1", "2", "3"):
        webbrowser.open(links[int(open_choice) - 1])
        print(GREEN + "Search link requested." + RESET)
    elif open_choice != "0":
        print(RED + "Invalid Input." + RESET)


def generate_report(cases):
    banner()
    print(YELLOW + "EVIDENCE SUMMARY REPORT" + RESET)

    case_id = input("Enter Case ID: ").strip()
    case = find_case(cases, case_id)

    if not case:
        print(RED + "Error: Case not found." + RESET)
        return

    lines = [
        "SOMRAT CYBER LOOKUP - EVIDENCE SUMMARY",
        "=" * 48,
        "Case ID: " + case["case_id"],
        "Title: " + case.get("title", ""),
        "Incident Date: " + case.get("incident_date", ""),
        "Description: " + case.get("description", ""),
        "Screenshot Description: " +
        case.get("screenshot_description", ""),
        "Personal Notes: " + case.get("personal_notes", ""),
        "",
        "REFERENCE LINKS:"
    ]

    lines.extend(case.get("reference_links", []))
    lines.extend(["", "PROFILE RECORDS:"])

    for record in case.get("profile_records", []):
        lines.append("Name: " + record.get("name", ""))
        lines.append("Link: " + record.get("link", ""))
        lines.append("Status: " + record.get("status", "Unverified"))
        lines.append("Notes: " + record.get("notes", ""))
        lines.append("")

    lines.extend([
        "=" * 48,
        "Note: This report records submitted information.",
        "It does not independently verify allegations."
    ])

    filename = "evidence_report_" + case["case_id"] + ".txt"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        print(GREEN + "[SUCCESS] Report generated: " + filename + RESET)

    except OSError:
        print(RED + "Error: Could not generate report." + RESET)


def post_evidence_collector():
    while True:
        cases = load_cases()

        if cases is None:
            pause()
            return

        banner()

        print(YELLOW + "          EVIDENCE ORGANIZER MENU" + RESET)
        print(CYAN + "[01] Create New Evidence Case")
        print("[02] View Saved Evidence")
        print("[03] Search Evidence by Case ID")
        print("[04] Update Existing Case")
        print("[05] Delete Case")
        print("[06] Generate Evidence Summary Report")
        print("[07] Add Fake Profile Evidence")
        print("[08] Public Facebook Name Search")
        print(RED + "[00] Back to Main Menu" + RESET)
        print("-" * 48)

        choice = input(GREEN + "Select Option: " + RESET).strip()

        if choice == "00":
            break
        elif choice == "01":
            create_case(cases)
        elif choice == "02":
            view_cases(cases)
        elif choice == "03":
            search_case(cases)
        elif choice == "04":
            update_case(cases)
        elif choice == "05":
            delete_case(cases)
        elif choice == "06":
            generate_report(cases)
        elif choice == "07":
            add_profile_record(cases)
        elif choice == "08":
            public_name_search()
        else:
            print(RED + "\nInvalid Input." + RESET)

        pause()


if __name__ == "__main__":
    post_evidence_collector()
