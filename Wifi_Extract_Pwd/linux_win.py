import subprocess
import datetime
import os
import re

# --- Configuration ---
# Create a unique, dated filename
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"WiFi_Passwords_Only_{date_str}_Linux.txt"
temp_file = "temp_passwords.txt"
full_output_path = os.path.join(os.getcwd(), output_file)
full_temp_path = os.path.join(os.getcwd(), temp_file)

# NOTE: This script requires NetworkManager (nmcli) and root privileges (sudo)
# to access the password keys, as configuration files are usually protected.
# You MUST run this script using 'sudo python3 your_script_name.py'

print("Linux WiFi Password Extractor (Requires 'sudo')")
print("==============================================")
print(f"[*] Extracting WiFi passwords to: {output_file}")
print("-" * 30)

# --- 1. Get WiFi Connections (Profiles) ---
extracted_passwords = []
ssids = []

try:
    # Use nmcli to list connection names. -t for terse output, -f for field list
    result = subprocess.run(
        ['nmcli', '-t', '-f', 'NAME', 'connection', 'show'],
        capture_output=True,
        text=True,
        check=True
    )
    # The output is newline-separated connection names
    ssids = [line.strip() for line in result.stdout.splitlines() if line.strip()]

    print(f"[*] Found {len(ssids)} NetworkManager connections (profiles)")
    print()

    # --- 2. Extract passwords for each connection ---
    for ssid in ssids:
        print(f"[*] Extracting password for: {ssid}")
        try:
            # Get connection details. This is the command that will require 'sudo'
            # The password is often found in the '802-11-wireless-security.psk' field
            result = subprocess.run(
                ['nmcli', '-s', 'connection', 'show', ssid],
                capture_output=True,
                text=True,
                check=True
            )
            profile_output = result.stdout

            # Extract the password (psk content) using regex
            # Look for the Pre-Shared Key (psk) in the security section
            key_pattern = r'802-11-wireless-security\.psk:\s*(.+)'
            password_match = re.search(key_pattern, profile_output)

            if password_match:
                password = password_match.group(1).strip()
                if password:
                    extracted_passwords.append(password)
                    print(f"    Password found: {password}")
            else:
                # Password might be stored in a different format or the connection is open/enterprise
                print("    No PSK (pre-shared key) found (might be open, enterprise, or stored elsewhere)")

        except subprocess.CalledProcessError as e:
            # This is a common error if the script isn't run with 'sudo'
            if 'Error: Failed to connect' in e.stderr:
                print(f"    [ERROR] Failed to connect to NetworkManager. Did you use 'sudo'?")
            else:
                print(f"    [ERROR] Failed to extract password for {ssid}")
                print(f"    Details: {e.stderr.strip()}")
            
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Failed to run nmcli command: {e}")
    print("[!] Ensure NetworkManager is installed and running.")

# --- 3. Write to temporary file ---
with open(full_temp_path, "w") as f:
    for password in extracted_passwords:
        f.write(password + "\n")

# --- 4. Remove Duplicates and Create Final File ---
unique_passwords = []
seen_passwords = set()

# Read, sort, and filter unique passwords
try:
    with open(full_temp_path, 'r') as f:
        for line in sorted(f.readlines()):
            current_password = line.strip()
            if current_password and current_password not in seen_passwords:
                unique_passwords.append(current_password)
                seen_passwords.add(current_password)

    # Write final output
    with open(full_output_path, "w") as f:
        f.write("WiFi Passwords (unique)\n")
        f.write("======================\n")
        f.write("\n")
        f.write('\n'.join(unique_passwords) + '\n')

    # Clean up temporary file
    os.remove(full_temp_path)

    print("\n" + "-" * 30)
    print(f"[*] All unique passwords saved to: {full_output_path}")
    print("[!] Total unique passwords: " + str(len(unique_passwords)))
    print("Press Enter to exit.")
    input()

except FileNotFoundError:
    print("\n[!] No passwords were successfully extracted to process/save.")