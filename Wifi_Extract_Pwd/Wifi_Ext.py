import subprocess
import datetime
import os
import re
import platform 
import sys 

# --- Configuration & File Setup ---
os_name = platform.system().lower() 
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"WiFi_Passwords_Only_{date_str}_{os_name.capitalize()}.txt"
temp_file = "temp_passwords_temp.txt"
full_output_path = os.path.join(os.getcwd(), output_file)
full_temp_path = os.path.join(os.getcwd(), temp_file)

# Set commands and regex based on the operating system
if platform.system() == "Windows":
    PRINT_TITLE = "Windows WiFi Password Extractor"
    PROFILE_LIST_CMD = ['netsh', 'wlan', 'show', 'profiles']
    PROFILE_LIST_REGEX = r'All User Profile\s*:\s*(.+?)\s*$' 
    def get_profile_detail_cmd(ssid):
        return ['netsh', 'wlan', 'show', 'profile', f'name={ssid}', 'key=clear']
    DETAIL_PASSWORD_REGEX = r'Key Content\s*:\s*(.+)'

elif platform.system() == "Linux":
    PRINT_TITLE = "Linux WiFi Password Extractor (Requires 'sudo')"
    PROFILE_LIST_CMD = ['nmcli', '-t', '-f', 'NAME', 'connection', 'show']
    PROFILE_LIST_REGEX = r'^(.+)$' 
    def get_profile_detail_cmd(ssid):
        return ['nmcli', '-s', 'connection', 'show', ssid]
    DETAIL_PASSWORD_REGEX = r'802-11-wireless-security\.psk:\s*(.+)'

else:
    print(f"Unsupported OS: {platform.system()}")
    sys.exit(1)

print(PRINT_TITLE)
print("=" * len(PRINT_TITLE))
print(f"[*] Extracting WiFi passwords to: {output_file}")
print("-" * 30)
print(f"[*] Running on: {platform.system()}")
print("Press Ctrl+C at any time to stop the process.")

extracted_passwords = []
ssids = []
process_successful = False
try:
    # --- 1. Get WiFi Profiles ---
    result = subprocess.run(
        PROFILE_LIST_CMD,
        capture_output=True,
        text=True,
        check=True
    )
    profiles_output = result.stdout

    # Extract SSID names
    ssids = re.findall(PROFILE_LIST_REGEX, profiles_output, re.MULTILINE)
    ssids = [s.strip() for s in ssids if s.strip()]

    print(f"[*] Found {len(ssids)} network profiles/connections")
    print()

    # --- 2. Extract passwords for each profile ---
    for ssid in ssids:
        print(f"[*] Extracting password for: {ssid}")
        try:
            result = subprocess.run(
                get_profile_detail_cmd(ssid),
                capture_output=True,
                text=True,
                check=True
            )
            profile_output = result.stdout

            password_match = re.search(DETAIL_PASSWORD_REGEX, profile_output)

            if password_match:
                password = password_match.group(1).strip()
                if password:
                    extracted_passwords.append(password)
                    print(f"    Password found: {password}")
            else:
                print("    No password found (open network, enterprise, or stored elsewhere)")

        except subprocess.CalledProcessError as e:
            if platform.system() == "Linux" and 'Error: Failed to connect' in e.stderr:
                 print(f"    [ERROR] Failed to connect to NetworkManager. Did you use 'sudo'?")
            else:
                 print(f"    [ERROR] Failed to extract details for {ssid}")
            
except subprocess.CalledProcessError as e:
    print(f"\n[CRITICAL ERROR] Failed to run initial command: {e}")
    if platform.system() == "Windows":
        print("[!] Note: This script may require administrator privileges on Windows.")
    elif platform.system() == "Linux":
        print("[!] Note: This script requires 'nmcli' and may need 'sudo' on Linux.")
    
except KeyboardInterrupt:
    print("\n[STOPPED] User interrupted the extraction process.")
    
finally:
    # --- 3. Final Processing and Cleanup (Always Runs) ---
    if extracted_passwords:
        try:
            with open(full_temp_path, "w") as f:
                for password in extracted_passwords:
                    f.write(password + "\n")

            unique_passwords = []
            seen_passwords = set()

            with open(full_temp_path, 'r') as f:
                for line in sorted(f.readlines()):
                    current_password = line.strip()
                    if current_password and current_password not in seen_passwords:
                        unique_passwords.append(current_password)
                        seen_passwords.add(current_password)

            # Write final output file
            with open(full_output_path, "w") as f:
                f.write(f"WiFi Passwords (unique - Extracted from {platform.system()})\n")
                f.write("=" * 40 + "\n")
                f.write('\n'.join(unique_passwords) + '\n')
            
            process_successful = True

        except Exception as e:
            print(f"\n[ERROR] Failed to write final files: {e}")
            
        finally:
            # Clean up temporary file if it exists
            if os.path.exists(full_temp_path):
                os.remove(full_temp_path)

    # --- Final Console Output ---
    print("\n" + "-" * 30)
    if process_successful:
        print(f"[*] All unique passwords saved to: {full_output_path}")
        print("[!] Total unique passwords: " + str(len(unique_passwords)))
    elif extracted_passwords:
        print("[!] Process interrupted. Partial results were saved.")
    else:
        print("[!] No passwords were successfully extracted.")

    print("Press Enter to exit.")
    input()
    sys.exit(0)