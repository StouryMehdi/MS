import subprocess
import datetime
import os
import re

# --- Configuration ---
# Create a unique, dated filename
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"File_List_Only_{date_str}.txt"
temp_file = "temp_file_list.txt"
full_output_path = os.path.join(os.getcwd(), output_file)
full_temp_path = os.path.join(os.getcwd(), temp_file)

print("File Listing Utility")
print("====================")
print(f"[*] Listing files to: {output_file}")
print("-" * 30)

# --- 1. Equivalent of netsh wlan show profiles (Listing Directory Contents) ---
# We use 'ls' (Linux/macOS) or 'dir' (Windows) to get system data
try:
    if os.name == 'nt': # Windows
        command = ['cmd', '/c', 'dir', '/b']
    else: # Linux/macOS
        command = ['ls']
        
    # Execute the command
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    directory_list = result.stdout.splitlines()

except subprocess.CalledProcessError as e:
    print(f"[ERROR] Failed to run system command: {e}")
    directory_list = []
    
# --- 2. Equivalent of Saving Passwords (Saving File List to Temp File) ---
extracted_items = []

print("[*] Processing items (Listing files and folders)...")
for item in directory_list:
    # Example "extraction" and cleanup logic
    if item.strip() and not item.startswith(temp_file):
        extracted_items.append(item.strip())
        print(f"    Found: {item.strip()}")

# Write to temporary file
with open(full_temp_path, "w") as f:
    for item in extracted_items:
        f.write(item + "\n")


# --- 3. Equivalent of Removing Duplicates and Creating Final File ---
unique_items = []
seen_items = set()

# Read, sort, and filter unique items
with open(full_temp_path, 'r') as f:
    # Sort the lines first, then iterate for uniqueness
    for line in sorted(f.readlines()):
        current_item = line.strip()
        if current_item and current_item not in seen_items:
            unique_items.append(current_item)
            seen_items.add(current_item)

# Write final output
with open(full_output_path, "w") as f:
    f.write("System File List (unique)\n")
    f.write("=========================\n")
    f.write('\n'.join(unique_items) + '\n')

# Clean up temporary file
os.remove(full_temp_path)

print("\n" + "-" * 30)
print(f"[*] All unique items saved to: {full_output_path}")
print("Press Enter to exit.")
input()