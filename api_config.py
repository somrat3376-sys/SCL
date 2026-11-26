import os

FEATURES = {
    1: "NUMBER LOOKUP",
    2: "PUBLIC NUMBER SEARCH",
    3: "SPAM CHECK",
    4: "PUBLIC FACEBOOK POST SEARCH",
    5: "PROFILE LINK FINDER",
    6: "FAKE PROFILE CHECK",
    7: "IMPERSONATION CHECK",
    8: "POST EVIDENCE COLLECTOR",
    9: "LINK SAFETY ANALYZER",
    10: "OWN CALL LOG ANALYSIS",
    11: "DEVICE INFORMATION",
    12: "REPORT ASSISTANT",
}

API_CONFIG = {
    "phone_metadata": os.getenv("PHONE_METADATA_API_KEY", ""),
    "reputation": os.getenv("REPUTATION_API_KEY", ""),
    "domain_security": os.getenv("DOMAIN_SECURITY_API_KEY", ""),
    "business_api": os.getenv("BUSINESS_API_TOKEN", ""),
}

def feature_status():
    print("=" * 45)
    print("CENTRAL API CONFIGURATION")
    print("=" * 45)

    for number, name in FEATURES.items():
        print(f"[{number:02}] {name}")

    print("\nAPI STATUS")

    for name, value in API_CONFIG.items():
        status = "CONFIGURED" if value else "NOT CONFIGURED"
        print(f"{name.upper():24} : {status}")

    print("\nLOCAL / DEVICE DATA")
    print("Call history           : LOCAL CSV ONLY")
    print("Device information     : LOCAL DEVICE")
    print("Phone format checking  : OFFLINE LIBRARY")
    print("Private account lookup : NOT SUPPORTED")
    print("=" * 45)

def get_api_key(provider):
    return API_CONFIG.get(provider, "")

if __name__ == "__main__":
    feature_status()
