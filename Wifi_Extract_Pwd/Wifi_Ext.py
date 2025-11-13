import subprocess
import datetime
import os
import re

# --- Configuration ---
# Create a unique, dated filename
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"WiFi_Passwords_Only_{date_str}.txt"
temp_file = "temp_passwords.txt"
full_output_path = os.path.join(os.getcwd(), output_file)
full_temp_path = os.path.join(os.getcwd(), temp_file)

print("WiFi Password Extractor")
print("=======================")
print(f"[*] Extracting WiFi passwords to: {output_file}")
print("-" * 30)

# --- 1. Get WiFi Profiles ---
extracted_passwords = []

try:
    # Get list of WiFi profiles
    result = subprocess.run(
        ['netsh', 'wlan', 'show', 'profiles'],
        capture_output=True,
        text=True,
        check=True
    )
    profiles_output = result.stdout
    
    # Extract SSID names using regex
    ssid_pattern = r'All User Profile\s*:\s*(.+)'
    ssids = re.findall(ssid_pattern, profiles_output)
    
    print(f"[*] Found {len(ssids)} WiFi profiles")
    print()
    
    # --- 2. Extract passwords for each profile ---
    for ssid in ssids:
        ssid = ssid.strip()
        if ssid:
            print(f"[*] Extracting password for: {ssid}")
            try:
                # Get profile details with key in clear text
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'profile', f'name={ssid}', 'key=clear'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                profile_output = result.stdout
                
                # Extract the password (Key Content value)
                key_pattern = r'Key Content\s*:\s*(.+)'
                password_match = re.search(key_pattern, profile_output)
                
                if password_match:
                    password = password_match.group(1).strip()
                    if password:
                        extracted_passwords.append(password)
                        print(f"    Password found: {password}")
                else:
                    print(f"    No password found (open network)")
                    
            except subprocess.CalledProcessError as e:
                print(f"    [ERROR] Failed to extract password for {ssid}")
    
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Failed to run netsh command: {e}")
    print("[!] Note: This script requires administrator privileges")

# --- 3. Write to temporary file ---
with open(full_temp_path, "w") as f:
    for password in extracted_passwords:
        f.write(password + "\n")

# --- 4. Remove Duplicates and Create Final File ---
unique_passwords = []
seen_passwords = set()

# Read, sort, and filter unique passwords
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