import os
import re
import json
import ssl
import socket
import ipaddress
import shutil
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qsl

BASE = Path(__file__).resolve().parent
HISTORY = BASE / "url_analysis_history.json"
REPORT_DIR = BASE / "url_reports"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"

LAST_RESULT = None

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly",
    "rb.gy", "shorturl.at", "ow.ly", "buff.ly",
    "rebrand.ly", "lnkd.in", "goo.gl"
}

REDIRECT_PARAMS = {
    "url", "redirect", "redirect_url", "next", "return",
    "return_url", "target", "dest", "destination",
    "continue", "goto", "redir"
}

def progress(message, status="INFO"):
    colors = {
        "INFO": CYAN,
        "OK": GREEN,
        "WARN": YELLOW,
        "ERROR": RED
    }
    print(colors.get(status, WHITE) +
          "  [" + status + "] " + message + RESET,
          flush=True)

def banner():
    os.system("clear")
    print(CYAN + BOLD + r"""
╔══════════════════════════════════════════════╗
║       SOMRAT VAI YT — CYBER LOOKUP          ║
║                                              ║
║       🔐 LINK SECURITY INTELLIGENCE         ║
║       ⚡ ADVANCED URL ANALYSIS ENGINE        ║
╚══════════════════════════════════════════════╝
""" + RESET)
    print(GREEN + " [SYSTEM] " + RESET + "Analysis Engine: READY")
    print(CYAN + " [MODE]   " + RESET + "Ethical & Defensive Analysis")
    print("-" * 48)

def section(title):
    print("\n" + YELLOW + BOLD + "╔══ " + title + " ══╗" + RESET)

def info(label, value):
    print(CYAN + "  " + f"{label:<24}" + RESET + str(value), flush=True)

def pause():
    input(YELLOW + "\nPress ENTER to continue..." + RESET)

def load_history():
    try:
        if HISTORY.exists():
            data = json.loads(HISTORY.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        progress("History file could not be read.", "ERROR")
    return []

def save_history(result):
    try:
        records = load_history()
        records.append(result)
        HISTORY.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return True
    except OSError as exc:
        progress("History save failed: " + str(exc), "ERROR")
        return False

def extract_registered_domain(host):
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass

    parts = host.lower().strip(".").split(".")
    if len(parts) <= 2:
        return host.lower()

    common_suffixes = {
        "co.uk", "org.uk", "com.au", "net.au",
        "co.in", "com.bd", "com.pk", "co.jp"
    }
    last_two = ".".join(parts[-2:])
    if last_two in common_suffixes and len(parts) >= 3:
        return ".".join(parts[-3:])
    return last_two

def get_host(value):
    value = value.strip()
    if not value:
        raise ValueError("Input cannot be empty.")

    if any(ch.isspace() for ch in value):
        raise ValueError("Do not enter spaces in the domain or URL.")

    if "://" not in value:
        value = "https://" + value

    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid URL or port.") from exc

    if parsed.scheme.lower() not in ("http", "https") or not host:
        raise ValueError("Enter a valid HTTP/HTTPS URL or domain.")

    host = host.rstrip(".").lower()

    try:
        ipaddress.ip_address(host)
    except ValueError:
        try:
            host = host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise ValueError("Invalid international domain.") from exc

        if len(host) > 253 or "." not in host:
            raise ValueError("Enter a valid public domain name.")

        for label in host.split("."):
            if (not label or len(label) > 63 or
                not re.fullmatch(r"[a-z0-9-]+", label) or
                label.startswith("-") or label.endswith("-")):
                raise ValueError("Invalid domain label: " + label)

    return host

def analyze_url(raw_url):
    raw_url = raw_url.strip()

    if not raw_url:
        raise ValueError("URL cannot be empty.")
    if any(ch.isspace() for ch in raw_url):
        raise ValueError("URL must not contain spaces.")
    if len(raw_url) > 4096:
        raise ValueError("URL is too long.")
    if not re.match(r"^https?://", raw_url, re.I):
        raise ValueError("Enter a complete URL beginning with http:// or https://")

    try:
        parsed = urlsplit(raw_url)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid URL or port number.") from exc

    if parsed.scheme.lower() not in ("http", "https") or not host:
        raise ValueError("A valid HTTP/HTTPS website URL is required.")

    host = host.rstrip(".").lower()
    is_ip = False
    ip_version = None

    try:
        ip_obj = ipaddress.ip_address(host)
        is_ip = True
        ip_version = ip_obj.version
    except ValueError:
        try:
            ascii_host = host.encode("idna").decode("ascii")
            if len(ascii_host) > 253:
                raise ValueError("Domain name is too long.")
            for label in ascii_host.split("."):
                if (not label or not re.fullmatch(r"[a-zA-Z0-9-]+", label)
                    or label.startswith("-") or label.endswith("-")):
                    raise ValueError("Invalid domain format.")
        except UnicodeError as exc:
            raise ValueError("Invalid international domain.") from exc

    domain = extract_registered_domain(host)
    labels = host.split(".")
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    findings = []
    score = 0

    def flag(points, message):
        nonlocal score
        score += points
        findings.append(message)

    if parsed.scheme.lower() != "https":
        flag(15, "Website uses HTTP instead of HTTPS.")
    if is_ip:
        flag(20, "URL uses an IP address instead of a domain.")
    if host.startswith("xn--") or ".xn--" in host:
        flag(20, "Internationalized Punycode domain detected.")
    if host in SHORTENERS:
        flag(10, "Known URL shortening service detected.")
    if len(labels) > 4:
        flag(10, "Unusually deep subdomain structure detected.")
    if len(host) > 60:
        flag(10, "Unusually long hostname detected.")
    if host.count("-") >= 3:
        flag(10, "Multiple hyphens detected in hostname.")
    if labels[-1] in {"zip", "mov", "click", "top", "work", "rest", "gq", "tk", "ml"}:
        flag(5, "Less common TLD detected; this alone does not prove risk.")
    if "@" in raw_url:
        flag(20, "URL contains an @ character.")
    if "\\" in raw_url:
        flag(15, "Backslash character detected in URL.")
    if "%" in raw_url:
        flag(5, "Percent-encoded characters detected.")
    if parsed.username or parsed.password:
        flag(20, "Embedded username or password detected.")
    if port and port not in (80, 443):
        flag(5, "Non-standard URL port detected.")
    if any(ord(ch) > 127 for ch in raw_url):
        flag(10, "Non-ASCII characters detected.")

    redirect_matches = [
        key for key, value in query_items
        if key.lower() in REDIRECT_PARAMS
    ]
    if redirect_matches:
        flag(10, "Redirect-related query parameters detected.")

    score = min(score, 100)
    if score >= 70:
        risk = "HIGH"
    elif score >= 30:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": raw_url,
        "scheme": parsed.scheme.lower(),
        "domain": domain,
        "hostname": host,
        "path": parsed.path,
        "port": port or "Default",
        "is_ip_based": is_ip,
        "ip_version": ip_version,
        "is_shortener": host in SHORTENERS,
        "https_enabled": parsed.scheme.lower() == "https",
        "subdomain_count": max(0, len(labels) - 2),
        "redirect_parameters": redirect_matches,
        "findings": findings,
        "risk_score": score,
        "risk_level": risk,
        "assessment": (
            "Suspicious indicators detected."
            if findings else "No obvious suspicious indicators found."
        ),
        "assessment_type": "Heuristic indicator score; not a verified threat verdict."
    }

def display_result(result):
    section("URL INTELLIGENCE REPORT")
    info("Website / Domain:", result["domain"])
    info("Full Hostname:", result["hostname"])
    info("Protocol:", result["scheme"].upper())
    info("HTTPS Enabled:", result["https_enabled"])
    info("IP-Based URL:", result["is_ip_based"])
    info("IP Version:", result["ip_version"] or "N/A")
    info("URL Shortener:", result["is_shortener"])
    info("Subdomain Count:", result["subdomain_count"])
    info("Port:", result["port"])
    info("URL Path:", result["path"] or "/")

    section("SECURITY FINDINGS")
    if result["findings"]:
        for index, finding in enumerate(result["findings"], 1):
            print(YELLOW + f"  [{index:02}] ⚠ {finding}" + RESET)
    else:
        progress("No obvious suspicious indicators found.", "OK")

    section("RISK ASSESSMENT")
    color = {"LOW": GREEN, "MEDIUM": YELLOW, "HIGH": RED}.get(
        result["risk_level"], WHITE
    )
    print(color + BOLD + "  RISK LEVEL: " + result["risk_level"] + RESET)
    info("Indicator Score:", str(result["risk_score"]) + "/100")
    info("Assessment:", result["assessment"])
    print(YELLOW + "\n  This is a heuristic assessment, not proof of safety or malware.")
    print("  No website page was opened or downloaded." + RESET)

def analyze_single():
    global LAST_RESULT
    section("SINGLE URL ANALYSIS")
    print(CYAN + "INPUT TYPE: Complete website URL" + RESET)
    print(YELLOW + "Example: https://example.com/login" + RESET)
    url = input(GREEN + "\nWebsite URL: " + RESET).strip()

    try:
        progress("Validating URL format...")
        result = analyze_url(url)
        progress("Parsing hostname and URL components...", "OK")
        progress("Checking local suspicious indicators...", "OK")
        LAST_RESULT = result
        display_result(result)
        if save_history(result):
            progress("Analysis saved to history.", "OK")
    except ValueError as exc:
        progress("Invalid URL: " + str(exc), "ERROR")

def request_json(url, headers=None, timeout=7):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read(1024 * 1024).decode("utf-8", "replace"))

def dns_lookup(host):
    records = {}
    for record_type in ("A", "AAAA", "MX", "NS", "TXT", "CNAME"):
        try:
            query = urllib.parse.urlencode({
                "name": host,
                "type": record_type
            })
            url = "https://cloudflare-dns.com/dns-query?" + query
            data = request_json(
                url,
                {"accept": "application/dns-json",
                 "user-agent": "SomratCyberLookup/1.0"},
                timeout=6
            )
            answers = data.get("Answer", [])
            records[record_type] = [
                item.get("data", "") for item in answers
                if item.get("data")
            ]
            if data.get("Status") not in (0, None):
                records[record_type + "_status"] = "DNS response status " + str(data.get("Status"))
        except Exception as exc:
            records[record_type + "_error"] = str(exc)[:140]
    return records

def tls_lookup(host):
    result = {"status": "UNKNOWN", "hostname": host}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=6) as raw:
            with context.wrap_socket(raw, server_hostname=host) as conn:
                cert = conn.getpeercert()
                result["status"] = "VERIFIED"
                result["tls_version"] = conn.version()
                result["cipher"] = conn.cipher()[0] if conn.cipher() else "Unknown"
                result["issuer"] = cert.get("issuer", ())
                result["subject"] = cert.get("subject", ())
                result["not_before"] = cert.get("notBefore", "Unknown")
                result["not_after"] = cert.get("notAfter", "Unknown")
                result["subject_alt_name"] = cert.get("subjectAltName", ())
                return result
    except Exception as exc:
        result["status"] = "VERIFICATION_OR_CONNECTION_ERROR"
        result["error"] = str(exc)[:180]
        try:
            unverified = ssl._create_unverified_context()
            with socket.create_connection((host, 443), timeout=5) as raw:
                with unverified.wrap_socket(raw, server_hostname=host) as conn:
                    cert = conn.getpeercert()
                    result["certificate_observed"] = bool(cert)
                    result["tls_version"] = conn.version()
                    result["not_after"] = cert.get("notAfter", "Unknown")
        except Exception as second:
            result["certificate_observed"] = False
            result["detail"] = str(second)[:140]
    return result

def rdap_lookup(domain):
    url = "https://rdap.org/domain/" + urllib.parse.quote(domain, safe=".-")
    try:
        data = request_json(url, {"user-agent": "SomratCyberLookup/1.0"}, timeout=7)
        events = data.get("events", [])
        nameservers = [
            item.get("ldhName", "") for item in data.get("nameservers", [])
        ]
        return {
            "status": "AVAILABLE",
            "name": data.get("ldhName", domain),
            "handle": data.get("handle", "Unknown"),
            "status_list": data.get("status", []),
            "nameservers": nameservers,
            "events": events
        }
    except Exception as exc:
        return {"status": "UNAVAILABLE", "error": str(exc)[:180]}

def domain_intelligence():
    section("DOMAIN INTELLIGENCE")
    print(CYAN + "INPUT TYPE: Website URL or Domain Name" + RESET)
    print(YELLOW + "URL example: https://example.com/login" + RESET)
    print(YELLOW + "Domain example: example.com" + RESET)
    print(RED + "This performs DNS/TLS/RDAP metadata queries, not a webpage visit." + RESET)

    value = input(GREEN + "\nDomain / Website URL: " + RESET).strip()

    try:
        host = get_host(value)
    except ValueError as exc:
        progress(str(exc), "ERROR")
        return

    try:
        ipaddress.ip_address(host)
        progress("IP address entered; domain registration lookup is not applicable.", "WARN")
        info("IP Address:", host)
        return
    except ValueError:
        pass

    domain = extract_registered_domain(host)
    info("Input Hostname:", host)
    info("Estimated Registered Domain:", domain)
    info("Subdomain Count:", max(0, len(host.split(".")) - len(domain.split("."))))

    print(YELLOW + "\n[NOTICE] The following lookups contact public DNS/RDAP services and the host's TLS port. No web page is requested." + RESET)
    consent = input(GREEN + "Continue with these metadata lookups? (y/n): " + RESET).strip().lower()
    if consent not in ("y", "yes"):
        progress("Lookup cancelled. No network lookup performed.", "WARN")
        return

    progress("Step 1/3 — Querying public DNS records...")
    dns = dns_lookup(host)
    progress("DNS lookup step finished.", "OK")

    progress("Step 2/3 — Checking TLS certificate handshake...")
    tls = tls_lookup(host)
    progress("TLS check step finished.", "OK")

    progress("Step 3/3 — Requesting public RDAP registration data...")
    rdap = rdap_lookup(domain)
    progress("RDAP lookup step finished.", "OK")

    section("DNS INTELLIGENCE")
    for record_type in ("A", "AAAA", "MX", "NS", "TXT", "CNAME"):
        values = dns.get(record_type, [])
        info(record_type + " Records:", " | ".join(values) if values else "UNKNOWN / NO RECORD")
        if dns.get(record_type + "_error"):
            print(YELLOW + "    Lookup note: " + dns[record_type + "_error"] + RESET)

    section("TLS / CERTIFICATE INTELLIGENCE")
    info("Verification:", tls.get("status"))
    info("TLS Version:", tls.get("tls_version", "UNKNOWN"))
    info("Cipher:", tls.get("cipher", "UNKNOWN"))
    info("Certificate Expiry:", tls.get("not_after", "UNKNOWN"))
    info("Issuer:", tls.get("issuer", "UNKNOWN"))
    if tls.get("error"):
        print(YELLOW + "  TLS note: " + tls["error"] + RESET)

    section("DOMAIN REGISTRATION (RDAP)")
    info("RDAP Status:", rdap.get("status"))
    info("Registered Name:", rdap.get("name", "UNKNOWN"))
    info("Registry Handle:", rdap.get("handle", "UNKNOWN"))
    info("Nameservers:", ", ".join(rdap.get("nameservers", [])) or "UNKNOWN")
    if rdap.get("events"):
        for event in rdap["events"]:
            info(event.get("eventAction", "Event"), event.get("eventDate", "Unknown"))
    if rdap.get("error"):
        print(YELLOW + "  RDAP note: " + rdap["error"] + RESET)

    section("DATA LIMITATIONS")
    info("Hosting Provider:", "UNKNOWN — no hosting API configured")
    info("GeoIP / Country:", "UNKNOWN — no GeoIP provider configured")
    info("Threat Verdict:", "NOT CHECKED — no threat provider configured")

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "domain_intelligence",
        "input": value,
        "hostname": host,
        "registered_domain_estimate": domain,
        "dns": dns,
        "tls": tls,
        "rdap": rdap
    }
    try:
        records = load_history()
        records.append(record)
        HISTORY.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
        progress("Domain intelligence record saved.", "OK")
    except OSError as exc:
        progress("Could not save domain record: " + str(exc), "ERROR")

def phishing_indicators():
    if not LAST_RESULT:
        progress("Analyze a URL first using option 01.", "WARN")
        return
    section("PHISHING & SUSPICIOUS INDICATORS")
    info("Website:", LAST_RESULT["hostname"])
    if LAST_RESULT["findings"]:
        for index, item in enumerate(LAST_RESULT["findings"], 1):
            print(YELLOW + f"  [{index:02}] ⚠ {item}" + RESET)
    else:
        progress("No obvious URL-level indicators found.", "OK")
    print(YELLOW + "\nThis is heuristic analysis, not a confirmed phishing verdict." + RESET)

def threat_status():
    section("THREAT INTELLIGENCE STATUS")
    info("Provider:", "Not configured")
    info("API Reputation:", "UNAVAILABLE")
    info("Blacklist Status:", "UNKNOWN")
    info("Malware Domain Status:", "UNKNOWN")
    print(YELLOW + "\nNo malicious or safe verdict is invented. Configure an authorized provider before reputation checks." + RESET)

def view_last():
    if not LAST_RESULT:
        progress("No current URL analysis. Use option 01 first.", "WARN")
        return
    display_result(LAST_RESULT)

def view_history():
    records = load_history()
    section("SAVED ANALYSIS HISTORY")
    if not records:
        progress("No saved analysis records found.", "WARN")
        return
    for item in reversed(records[-20:]):
        print(CYAN + "\nType: " + RESET + item.get("type", "url_analysis"))
        print("Domain: " + item.get("domain", item.get("hostname", "Unknown")))
        print("Input: " + item.get("url", item.get("input", "Unknown")))
        print("Risk: " + item.get("risk_level", "Not assessed"))
        print("Date: " + item.get("timestamp", "Unknown"))
    info("Total saved records:", len(records))

def search_history():
    records = load_history()
    if not records:
        progress("No saved records available.", "WARN")
        return
    print(CYAN + "INPUT TYPE: Domain, URL, or keyword to search saved history" + RESET)
    keyword = input(GREEN + "History Search Query: " + RESET).strip().lower()
    if not keyword:
        progress("Search query cannot be empty.", "ERROR")
        return
    matches = [
        item for item in records
        if keyword in json.dumps(item, ensure_ascii=False).lower()
    ]
    section("HISTORY SEARCH RESULTS")
    if not matches:
        progress("No matching saved record found.", "WARN")
        return
    for item in matches[-30:]:
        info("Type:", item.get("type", "url_analysis"))
        info("Input:", item.get("url", item.get("input", "Unknown")))
        info("Risk:", item.get("risk_level", "Not assessed"))
        info("Date:", item.get("timestamp", "Unknown"))
        print("-" * 40)

def generate_report():
    if not LAST_RESULT:
        progress("Analyze a URL first using option 01.", "WARN")
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = REPORT_DIR / f"url_report_{timestamp}.json"
    txt_file = REPORT_DIR / f"url_report_{timestamp}.txt"
    try:
        json_file.write_text(
            json.dumps(LAST_RESULT, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        lines = [
            "SOMRAT VAI YT — LINK SECURITY REPORT",
            "=" * 45,
            "Date: " + LAST_RESULT["timestamp"],
            "URL: " + LAST_RESULT["url"],
            "Domain: " + LAST_RESULT["domain"],
            "HTTPS: " + str(LAST_RESULT["https_enabled"]),
            "Risk Level: " + LAST_RESULT["risk_level"],
            "Risk Score: " + str(LAST_RESULT["risk_score"]) + "/100",
            "",
            "SECURITY FINDINGS",
            "-" * 25
        ]
        lines.extend(LAST_RESULT["findings"] or ["No obvious indicators found."])
        lines.extend([
            "",
            "Disclaimer: Heuristic passive URL analysis.",
            "This is not a guarantee of website safety."
        ])
        txt_file.write_text("\n".join(lines), encoding="utf-8")
        progress("JSON Report: " + str(json_file), "OK")
        progress("TXT Report: " + str(txt_file), "OK")
    except OSError as exc:
        progress("Report generation failed: " + str(exc), "ERROR")

def copy_last_url():
    if not LAST_RESULT:
        progress("Analyze a URL first using option 01.", "WARN")
        return
    url = LAST_RESULT["url"]
    clipboard = shutil.which("termux-clipboard-set")
    if clipboard:
        try:
            subprocess.run([clipboard], input=url, text=True, check=True, timeout=5)
            progress("URL copied to clipboard.", "OK")
            return
        except (OSError, subprocess.SubprocessError):
            pass
    progress("Clipboard command unavailable. Copy manually:", "WARN")
    print(url)

def link_safety_analyzer():
    actions = {
        "1": analyze_single,
        "2": domain_intelligence,
        "3": phishing_indicators,
        "4": threat_status,
        "5": view_last,
        "6": view_history,
        "7": search_history,
        "8": generate_report,
        "9": copy_last_url
    }

    while True:
        banner()
        print(MAGENTA + BOLD + """
 [01] 🔎 Analyze Single URL
 [02] 🌐 Domain Intelligence — DNS / TLS / RDAP
 [03] 🛡️  Phishing & Suspicious Indicators
 [04] ⚠️  Threat Intelligence Status
 [05] 📊 View Last Analysis
 [06] 📁 View Analysis History
 [07] 🔍 Search Previous Analysis
 [08] 📄 Generate Security Report
 [09] 📋 Copy URL for Manual Review
 [00] ↩ Back to Main Menu
""" + RESET)

        choice = input(CYAN + "Select Option: " + RESET).strip()

        if choice in ("0", "00"):
            break

        action = actions.get(choice.lstrip("0"))
        if action:
            print()
            action()
            pause()
        else:
            progress("Invalid option. Choose 00–09.", "ERROR")
            pause()
