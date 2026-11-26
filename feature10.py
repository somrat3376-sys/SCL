import csv
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

records = []


def heading():
    import os
    os.system("clear")
    print(CYAN + r"""
  ███████╗ ██████╗ ███╗   ███╗██████╗  █████╗ ████████╗
  ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝
  ███████╗██║   ██║██╔████╔██║██████╔╝███████║   ██║
  ╚════██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══██║   ██║
  ███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║  ██║   ██║
  ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
""" + RESET)
    print(GREEN + "       SOMRAT VAI YT - CYBER LOOKUP" + RESET)
    print(YELLOW + "       Educational & Public Information Toolkit" + RESET)
    print("-" * 45)
    print(CYAN + "       CALL LOG FORENSICS & INTELLIGENCE" + RESET)
    print("-" * 45)


def mask_number(number):
    number = str(number).strip()
    if len(number) <= 5:
        return "*" * len(number)
    return number[:3] + ("*" * (len(number) - 5)) + number[-2:]


def parse_date(value):
    value = str(value).strip()
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def normalize_type(value):
    value = str(value).strip().lower()
    aliases = {
        "incoming": "incoming", "in": "incoming", "received": "incoming",
        "outgoing": "outgoing", "out": "outgoing", "dialed": "outgoing",
        "missed": "missed", "miss": "missed",
        "rejected": "missed", "no answer": "missed",
    }
    return aliases.get(value)


def import_csv():
    global records
    print("\n" + YELLOW + "IMPORT YOUR OWN CALL-LOG CSV" + RESET)
    print("Expected columns: date, number, type, duration_seconds")
    print("Date example: 2026-11-26 14:30:00")
    print("Type: incoming / outgoing / missed")
    print("Use a CSV exported from your own device.")
    path_text = input("\nLocal CSV file path: ").strip().strip('"').strip("'")

    if not path_text or "://" in path_text:
        print(RED + "Invalid path. A local CSV file is required." + RESET)
        return

    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path

    if not path.is_file() or path.suffix.lower() != ".csv":
        print(RED + "CSV file not found. Check the file path." + RESET)
        return

    imported = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                print(RED + "CSV header row is missing." + RESET)
                return

            headers = {
                str(name).strip().lower(): name
                for name in reader.fieldnames if name
            }

            date_key = next((headers[k] for k in
                             ("date", "datetime", "timestamp", "call_date")
                             if k in headers), None)
            number_key = next((headers[k] for k in
                               ("number", "phone", "phone_number", "caller")
                               if k in headers), None)
            type_key = next((headers[k] for k in
                             ("type", "call_type", "status")
                             if k in headers), None)
            duration_key = next((headers[k] for k in
                                 ("duration_seconds", "duration", "seconds")
                                 if k in headers), None)

            if not all((date_key, number_key, type_key)):
                print(RED + "Required columns missing: date, number, type." + RESET)
                return

            for row in reader:
                dt = parse_date(row.get(date_key, ""))
                number = str(row.get(number_key, "")).strip()
                call_type = normalize_type(row.get(type_key, ""))
                raw_duration = str(row.get(duration_key, "0")).strip() if duration_key else "0"

                if not dt or not number or not call_type:
                    continue
                try:
                    duration = max(0, int(float(raw_duration or 0)))
                except (ValueError, TypeError):
                    duration = 0

                imported.append({
                    "date": dt,
                    "number": number,
                    "type": call_type,
                    "duration": duration,
                })

    except (OSError, UnicodeError, csv.Error) as exc:
        print(RED + f"Could not read CSV: {exc}" + RESET)
        return

    if not imported:
        print(YELLOW + "No valid call records found in this CSV." + RESET)
        return

    records = imported
    print(GREEN + f"\nSuccessfully imported {len(records)} valid records." + RESET)
    print(YELLOW + "Records remain in memory only and are not uploaded." + RESET)


def last_seven_days():
    now = datetime.now()
    start = now - timedelta(days=7)
    return [r for r in records if start <= r["date"] <= now]


def require_data():
    data = last_seven_days()
    if not data:
        print(YELLOW + "No records found for the last 7 days." + RESET)
        print("Import your own call-log CSV first.")
        return None
    return data


def show_summary():
    data = require_data()
    if data is None:
        return
    counts = Counter(r["type"] for r in data)
    total_seconds = sum(r["duration"] for r in data)
    print("\n" + GREEN + "LAST 7 DAYS SUMMARY" + RESET)
    print(f"Total records : {len(data)}")
    print(f"Incoming      : {counts['incoming']}")
    print(f"Outgoing      : {counts['outgoing']}")
    print(f"Missed        : {counts['missed']}")
    print(f"Total duration: {total_seconds} seconds")


def show_type(call_type, title):
    data = require_data()
    if data is None:
        return
    selected = [r for r in data if r["type"] == call_type]
    print(f"\n{CYAN}{title}{RESET}")
    print(f"Total: {len(selected)}")
    for r in sorted(selected, key=lambda x: x["date"], reverse=True):
        print(f"{r['date']} | {mask_number(r['number'])} | {r['duration']} sec")


def repeated_numbers():
    data = require_data()
    if data is None:
        return
    counts = Counter(r["number"] for r in data)
    repeated = [(n, c) for n, c in counts.items() if c > 1]
    print("\n" + CYAN + "REPEATED NUMBER SUMMARY" + RESET)
    if not repeated:
        print("No repeated numbers found.")
        return
    for number, count in sorted(repeated, key=lambda x: x[1], reverse=True):
        print(f"{mask_number(number)} : {count} records")


def timeline():
    data = require_data()
    if data is None:
        return
    print("\n" + CYAN + "CALL TIMELINE" + RESET)
    for r in sorted(data, key=lambda x: x["date"]):
        print(f"{r['date']} | {r['type'].upper()} | {mask_number(r['number'])}")


def duration_stats():
    data = require_data()
    if data is None:
        return
    durations = [r["duration"] for r in data]
    total = sum(durations)
    print("\n" + CYAN + "CALL DURATION STATISTICS" + RESET)
    print(f"Total seconds : {total}")
    print(f"Longest call  : {max(durations)} seconds")
    print(f"Shortest call : {min(durations)} seconds")
    print(f"Average       : {total / len(durations):.1f} seconds")


def pattern_analysis():
    data = require_data()
    if data is None:
        return
    counts = Counter(r["number"] for r in data)
    print("\n" + CYAN + "PATTERN REVIEW (HEURISTIC ONLY)" + RESET)
    flagged = False
    for number, count in counts.items():
        if count >= 5:
            print(f"Repeated contact pattern: {mask_number(number)} ({count} records)")
            flagged = True
    missed = Counter(r["number"] for r in data if r["type"] == "missed")
    for number, count in missed.items():
        if count >= 3:
            print(f"Multiple missed calls: {mask_number(number)} ({count} records)")
            flagged = True
    if not flagged:
        print("No repeated-call pattern met the review thresholds.")
    print(YELLOW + "These are statistical flags, not proof of fraud or wrongdoing." + RESET)


def bangladesh_format():
    data = require_data()
    if data is None:
        return
    print("\n" + CYAN + "BANGLADESH NUMBER FORMAT REVIEW" + RESET)
    for r in data:
        digits = re.sub(r"\D", "", r["number"])
        valid = (
            (len(digits) == 11 and digits.startswith("01")) or
            (len(digits) == 13 and digits.startswith("8801")) or
            (len(digits) == 14 and digits.startswith("008801"))
        )
        status = "Bangladesh-style format" if valid else "Other / unrecognized format"
        print(f"{mask_number(r['number'])} : {status}")
    print(YELLOW + "Format checking does not identify a subscriber or verify ownership." + RESET)


def generate_report():
    data = require_data()
    if data is None:
        return
    folder = Path("call_log_reports")
    folder.mkdir(exist_ok=True)
    filename = folder / ("call_log_report_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt")
    counts = Counter(r["type"] for r in data)
    with filename.open("w", encoding="utf-8") as report:
        report.write("CALL LOG SUMMARY REPORT - LAST 7 DAYS\n")
        report.write("Generated: " + datetime.now().isoformat(timespec="seconds") + "\n")
        report.write("Privacy: phone numbers masked; local report only.\n\n")
        report.write(f"Total records: {len(data)}\n")
        report.write(f"Incoming: {counts['incoming']}\n")
        report.write(f"Outgoing: {counts['outgoing']}\n")
        report.write(f"Missed: {counts['missed']}\n\n")
        report.write("RECORDS\n")
        for r in sorted(data, key=lambda x: x["date"]):
            report.write(
                f"{r['date']} | {r['type']} | {mask_number(r['number'])} | "
                f"{r['duration']} seconds\n"
            )
    print(GREEN + f"Masked report saved locally: {filename}" + RESET)


def privacy_audit():
    print("\n" + CYAN + "PRIVACY AUDIT" + RESET)
    print("1. This feature reads only the CSV file you select.")
    print("2. No Android call-log permission is requested.")
    print("3. No network upload or remote lookup is performed.")
    print("4. Phone numbers are masked in on-screen results and reports.")
    print("5. Imported records stay in memory until this feature exits.")
    print("6. Reports contain masked numbers and are saved locally.")
    print(YELLOW + "Only import records you own or are authorized to analyze." + RESET)


def own_call_log_analysis():
    while True:
        heading()
        print("[01] Import Own Call Log (CSV)")
        print("[02] Last 7 Days Call Summary")
        print("[03] Incoming Call Analysis")
        print("[04] Outgoing Call Analysis")
        print("[05] Missed Call Analysis")
        print("[06] Repeated Number Analysis")
        print("[07] Date & Time Timeline")
        print("[08] Call Duration Statistics")
        print("[09] Suspicious Pattern Review")
        print("[10] Bangladesh Number Format Analysis")
        print("[11] Evidence & Masked Report Generator")
        print("[12] Privacy Audit")
        print("[00] Back to Main Menu")
        choice = input("\nSelect Feature: ").strip()

        actions = {
            "1": import_csv, "01": import_csv,
            "2": show_summary, "02": show_summary,
            "3": lambda: show_type("incoming", "INCOMING CALLS"), "03": lambda: show_type("incoming", "INCOMING CALLS"),
            "4": lambda: show_type("outgoing", "OUTGOING CALLS"), "04": lambda: show_type("outgoing", "OUTGOING CALLS"),
            "5": lambda: show_type("missed", "MISSED CALLS"), "05": lambda: show_type("missed", "MISSED CALLS"),
            "6": repeated_numbers, "06": repeated_numbers,
            "7": timeline, "07": timeline,
            "8": duration_stats, "08": duration_stats,
            "9": pattern_analysis, "09": pattern_analysis,
            "10": bangladesh_format,
            "11": generate_report,
            "12": privacy_audit,
        }

        if choice in ("00", "0"):
            return
        action = actions.get(choice)
        if action:
            action()
            input("\nPress Enter to continue...")
        else:
            print(RED + "Invalid option. Select 00-12." + RESET)
            input("Press Enter to retry...")
