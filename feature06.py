from urllib.parse import urlparse

def fake_profile_safety_check():
    data = {
        "username": "",
        "url": "",
        "age": "Unknown",
        "photo": "Unknown",
        "bio": "Unknown",
        "verification": "Unknown",
        "links": "Unknown",
        "money": "Unknown",
        "otp": "Unknown",
        "messages": "Unknown"
    }

    while True:
        print("\n===== FAKE PROFILE SAFETY CHECK =====")
        print("[01] Search by Username")
        print("[02] Enter Public Profile URL")
        print("[03] Check Profile Details")
        print("[04] Suspicious Activity Check")
        print("[05] Generate Safety Report")
        print("[00] Back to Main Menu")

        choice = input("\nSelect Option: ").strip()

        if choice in ("0", "00"):
            return

        elif choice in ("1", "01"):
            data["username"] = input("Enter Public Username: ").strip()
            print("Username saved for safety assessment.")

        elif choice in ("2", "02"):
            url = input("Enter Public Profile URL: ").strip()
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                data["url"] = url
                print("URL format is valid. Link was not opened.")
            else:
                print("Invalid URL format.")

        elif choice in ("3", "03"):
            data["age"] = input("Account Age (Known/Unknown): ").strip()
            data["photo"] = input("Photo (Original/Reused/Unknown): ").strip()
            data["bio"] = input("Bio (Consistent/Inconsistent/Unknown): ").strip()
            data["verification"] = input("Verification (Verified/Not Verified/Unknown): ").strip()
            print("Profile details saved.")

        elif choice in ("4", "04"):
            data["links"] = input("Suspicious Links? (Yes/No/Unknown): ").strip()
            data["money"] = input("Money Requests? (Yes/No/Unknown): ").strip()
            data["otp"] = input("OTP Requests? (Yes/No/Unknown): ").strip()
            data["messages"] = input("Unusual Messages? (Yes/No/Unknown): ").strip()
            print("Activity details saved.")

        elif choice in ("5", "05"):
            print("\n===== PROFILE SAFETY REPORT =====")
            for key, value in data.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

            indicators = 0
            if data["photo"].lower() == "reused":
                indicators += 1
            if data["bio"].lower() == "inconsistent":
                indicators += 1
            for key in ("links", "money", "otp", "messages"):
                if data[key].lower() == "yes":
                    indicators += 1

            print("\nReported Warning Indicators:", indicators)
            print("Assessment: Review the reported warning signs.")
            print("Identity Verification: Not performed.")
            print("This report is not proof of a fake account.")

        else:
            print("Invalid option. Enter 1, 2, 3, 4, 5 or 0.")

        input("\nPress Enter to continue...")
