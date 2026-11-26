import json
import socket
import urllib.request
import urllib.parse
import urllib.error
import time
from datetime import datetime
from urllib.parse import urlparse

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def fetch_json(url, timeout=12):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "SOMRAT-CYBER-LOOKUP/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except Exception:
        return None

def get_domain():
    while True:
        raw = input(YELLOW + "\nEnter Domain: " + RESET).strip()

        if not raw or any(c.isspace() for c in raw):
            print(RED + "Invalid Domain." + RESET)
            continue

        if "://" not in raw:
            raw = "https://" + raw

        try:
            parsed = urlparse(raw)
            host = parsed.hostname

            if (parsed.scheme not in ("http", "https")
                    or not host or "." not in host
                    or not parsed.username
                    and not parsed.password):
                if parsed.scheme not in ("http", "https") or not host or "." not in host:
                    raise ValueError

            host = host.encode("idna").decode("ascii").lower().rstrip(".")
            if len(host) > 253 or any(
                not label or len(label) > 63
                or label.startswith("-") or label.endswith("-")
                for label in host.split(".")
            ):
                raise ValueError

            return host

        except Exception:
            print(RED + "Invalid Domain. Try Again." + RESET)

def show(title, value):
    if value is None or value == "" or value == []:
        print(RED + "− " + YELLOW + title + RESET + ": Unavailable\n")
    else:
        if isinstance(value, (list, dict)):
            value = json.dumps(value, indent=2, ensure_ascii=False)
        print(GREEN + "Ⓥ " + YELLOW + title + RESET + ":")
        print(str(value)[:5000])
        print()

def dns_lookup(domain, record_type):
    url = "https://dns.google/resolve?" + urllib.parse.urlencode({
        "name": domain,
        "type": record_type
    })
    data = fetch_json(url)
    if not data or data.get("Status") != 0:
        return None
    answers = data.get("Answer", [])
    return [item.get("data") for item in answers if item.get("data")]

def run_scan(domain):
    print(YELLOW + "\n========== DOMAIN INTELLIGENCE REPORT ==========" + RESET)
    print(CYAN + "Target: " + domain + RESET + "\n")

    tasks = [
        ("A Records / Public IPv4", "A"),
        ("AAAA Records / Public IPv6", "AAAA"),
        ("MX Records", "MX"),
        ("NS Records / Nameservers", "NS"),
        ("TXT Records", "TXT"),
        ("CNAME Records", "CNAME")
    ]

    dns_results = {}

    for title, record_type in tasks:
        print(CYAN + "[Loading] " + title + "..." + RESET)
        result = dns_lookup(domain, record_type)
        dns_results[record_type] = result
        show(title, result)

    print(CYAN + "[Loading] Domain Registration / RDAP..." + RESET)
    rdap = fetch_json("https://rdap.org/domain/" + urllib.parse.quote(domain))
    if rdap:
        show("Domain Name", rdap.get("ldhName"))
        show("Registrar / Registration Entities", [
            e.get("vcardArray", [None, []])[1][1][3][3]
            for e in rdap.get("entities", [])
            if e.get("vcardArray")
        ] or None)
        show("Domain Status", rdap.get("status"))
        show("Nameservers", [
            n.get("ldhName") for n in rdap.get("nameservers", [])
        ] or None)

        events = {}
        for event in rdap.get("events", []):
            action = event.get("eventAction", "")
            date = event.get("eventDate", "")
            if action and date:
                events[action] = date
        show("Registration / Expiry Events", events or None)
    else:
        show("Domain RDAP Information", None)

    ips = dns_results.get("A") or []
    if ips:
        print(CYAN + "[Loading] Public IP Registration Information..." + RESET)
        for ip in ips[:5]:
            print(YELLOW + "\nIP Address: " + ip + RESET)
            ip_data = fetch_json("https://rdap.org/ip/" + urllib.parse.quote(ip))
            if ip_data:
                show("IP Network Name", ip_data.get("name"))
                show("IP Network Handle", ip_data.get("handle"))
                show("IP Country", ip_data.get("country"))
                show("IP Range", str(ip_data.get("startAddress", "")) +
                     " - " + str(ip_data.get("endAddress", "")))
            else:
                show("IP Registration", None)
    else:
        show("Public IP Registration", None)

    print(CYAN + "[Loading] Public Certificate Transparency Information..." + RESET)
    ct_url = "https://crt.sh/?" + urllib.parse.urlencode({
        "q": domain,
        "output": "json"
    })
    certificates = fetch_json(ct_url)
    if isinstance(certificates, list):
        show("Public Certificate Records Found", len(certificates))
        if certificates:
            latest = max(
                certificates,
                key=lambda x: x.get("not_before", "")
            )
            show("Latest Listed Certificate Start", latest.get("not_before"))
            show("Latest Listed Certificate Expiry", latest.get("not_after"))
    else:
        show("Certificate Transparency Records", None)

    print(CYAN + "[Loading] Additional Security Information..." + RESET)
    show("HTTPS / Live TLS Verification",
         "Not tested. No direct connection made.")
    show("Open / Closed Port Status",
         "Not scanned. No unauthorized port scan performed.")
    show("Historical DNS Database",
         "Unavailable through the selected public sources.")
    show("Exact Hosting Provider",
         "Cannot be confirmed from DNS alone; IP network information is shown above.")

    print(YELLOW + "\n========== FINAL SUMMARY ==========" + RESET)
    print("Domain:", domain)
    print("DNS A Records:", len(dns_results.get("A") or []))
    print("DNS AAAA Records:", len(dns_results.get("AAAA") or []))
    print("Assessment: Public information collection completed.")
    print("Identity Status: Not independently verified.")
    print("A matching domain or certificate does not prove trustworthiness.")

def impersonation_safety_check():
    print(YELLOW + "\n===== DOMAIN INTELLIGENCE SCANNER =====" + RESET)
    print("Public domain information only.")
    domain = get_domain()

    while True:
        choice = input(YELLOW + "\nStart Collection? (Y/N): " + RESET).strip().lower()
        if choice == "y":
            break
        if choice == "n":
            print("Cancelled.")
            return
        print(RED + "Invalid Input. Enter Y or N." + RESET)

    print(YELLOW + "\nStarting sequential information collection..." + RESET)
    run_scan(domain)
    input(YELLOW + "\nPress Enter to return to Main Menu..." + RESET)

