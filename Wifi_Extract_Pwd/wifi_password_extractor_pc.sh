import subprocess
import datetime
import os
import sys

# --- Configuration (Equivalent to shell variables) ---
date_str = datetime.datetime.now().strftime("%Y-%m-%d")
output_file = f"PROCESS_OUTPUT_Only_{date_str}.txt"
temp_file = "temp_output.txt"

def execute_and_extract():
    """
    Executes a harmless system command (like 'ls' or 'dir /b') 
    and simulates extracting data lines.
    """
    if os.name == 'nt':
        # Windows equivalent to listing files
        command = ['cmd', '/c', 'dir', '/b']
    else:
        # Linux/macOS equivalent to listing files
        command = ['ls', '-a']

    print(f"[*] Executing system command: {' '.join(command)}")
    
    try:
        # Run the command and capture output
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, # Raise error if command fails
            timeout=5
        )
        # Simulate extracted data lines
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    except FileNotFoundError:
        print("[ERROR] Command not found on system.")
        return []
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed with error:\n{e.stderr}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return []

def cleanup_and_save(extracted_data):
    """Sorts, filters for uniqueness, and writes the final output."""
    print("\n[+] Removing duplicates and saving results...")
    
    # 1. Write raw data to temporary file
    with open(temp_file, "w") as f:
        f.write('\n'.join(extracted_data) + '\n')

    # 2. Sort and filter for uniqueness (Python equivalent of `sort tempfile | uniq`)
    unique_items = []
    seen = set()
    
    # Reading sorted data is cleaner for complex scenarios, but for simplicity:
    sorted_data = sorted(extracted_data) 
    
    for item in sorted_data:
        if item not in seen and item:
            unique_items.append(item)
            seen.add(item)
            
    # 3. Write final output file
    with open(output_file, "w") as f:
        f.write("System Command Output (Unique Items)\n")
        f.write("===================================\n")
        f.write('\n'.join(unique_items) + '\n')
    
    # 4. Clean up temp file
    os.remove(temp_file)
    
    print(f"[*] Found {len(unique_items)} unique items.")
    print(f"[*] All results saved to: {output_file}")


if __name__ == '__main__':
    print("System Command Executor and Filter")
    print("==================================")
    
    # Simulate extraction
    data_lines = execute_and_extract()
    
    if data_lines:
        cleanup_and_save(data_lines)
    else:
        print("[!] No data was extracted.")
        
    print("\nPress Enter to exit.")
    try:
        input()
    except EOFError:
        pass