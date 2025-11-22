import sys
import time
import json
import os
import requests
from requests.exceptions import RequestException
from PIL import Image # Used for Image processing (though mostly handled by exifread)
import exifread # Used for EXIF data extraction
import subprocess # Required to run external commands like 'holehe'

# --- Global Configuration and OPSEC Setup ---
# Tor default SOCKS port. Change if your Tor configuration is different (e.g., 9150).
TOR_PROXY = 'socks5h://localhost:9050' 
OPSEC_ENABLED = False # Global flag for anonymity

# Global dictionary to hold all results for the final report
GLOBAL_RESULTS = {
    "investigation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "targets": {}
}

def get_session():
    """Returns a requests Session object, applying Tor proxy if OPSEC is enabled."""
    session = requests.Session()
    if OPSEC_ENABLED:
        session.proxies = {
            'http': TOR_PROXY,
            'https': TOR_PROXY
        }
        print("🛡️ Using Tor proxy for anonymity...")
    return session

# --- Menu and Core Functions ---

def display_menu():
    """Displays the main menu options."""
    global OPSEC_ENABLED
    opsec_status = "ON (Tor)" if OPSEC_ENABLED else "OFF"
    
    print("\n" + "="*55)
    print("        OSINT FUSION FRAMEWORK v2.1 (Holehe Integrated)")
    print(f"        [OPSEC Status: {opsec_status}]")
    print("="*55)
    print("--- CORE LOOKUPS ---")
    print("1. Username Search (Social Media)")
    print("2. Email Address Lookup (Holehe - 120+ Sites)")
    print("3. Domain/Website Recon (Placeholder)")
    print("--- ADVANCED TOOLS ---")
    print("4. Image Forensics (EXIF Data Extraction)")
    print("--- SETTINGS & EXIT ---")
    print("5. Toggle OPSEC/Anonymity (Tor)")
    print("6. Exit and Generate Final Report (JSON)")
    print("-" * 55)

def username_search():
    """Performs a conceptual username search using requests/OPSEC."""
    target_username = input("Enter username to search: ").strip()
    if not target_username:
        print("Username cannot be empty.")
        return

    print(f"\n🔍 Searching for username: '{target_username}'...")
    results = {}
    
    platforms = {
        "GitHub": f"https://github.com/{target_username}",
        "Twitter (X)": f"https://twitter.com/{target_username}"
    }
    
    session = get_session()
    for name, url in platforms.items():
        try:
            time.sleep(1.5) # Rate limiting
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                results[name] = f"FOUND: {url}"
                print(f"✅ {name}: FOUND")
            elif response.status_code == 404:
                results[name] = "NOT FOUND"
                print(f"❌ {name}: NOT FOUND")
            else:
                results[name] = f"UNKNOWN STATUS ({response.status_code})"
                print(f"⚠️ {name}: UNKNOWN STATUS ({response.status_code})")
        except RequestException as e:
            results[name] = f"NETWORK ERROR: {e}"
            print(f"🛑 Network Error for {name}.")
            
    GLOBAL_RESULTS['targets'].setdefault(target_username, {})['username_search'] = results
    print("\n--- Username search complete. ---")

def email_lookup():
    """Runs the holehe tool for email registration lookup and parses JSON output."""
    target_email = input("Enter email address to look up: ").strip()
    if not target_email:
        print("Email cannot be empty.")
        return

    print(f"\n📧 Starting Holehe check for: '{target_email}'...")
    
    # Base command: run Holehe and force JSON output
    command = ['holehe', target_email, '--json']
    
    # Add proxy flag if OPSEC is enabled
    if OPSEC_ENABLED:
        # Holehe supports its own proxy flag which we use here.
        print("🛡️ Applying proxy flag for Holehe command...")
        # Tor default SOCKS port for Holehe command
        command.extend(['--proxy', 'socks5://127.0.0.1:9050']) 

    try:
        # Execute the command and capture the output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True, # Raise error if holehe fails
            timeout=180 # Set a maximum runtime for the command
        )
        
        # Holehe output is JSON, but might have other logs/warnings. We look for the JSON object.
        output_data = {}
        for line in result.stdout.strip().split('\n'):
            try:
                # The actual JSON object starts with '{'
                if line.strip().startswith('{'):
                    output_data = json.loads(line)
                    break
            except json.JSONDecodeError:
                continue

        if output_data and 'results' in output_data:
            # Filter for sites where the email is confirmed to exist
            used_on = [
                site['name'] for site in output_data['results'] 
                if site.get('exists') is True
            ]
            
            # Print a summary
            print(f"\n✅ Holehe found {len(used_on)} services where the email is registered.")
            for site in used_on:
                print(f"  - {site}")
                
            # Store results in the global report structure
            GLOBAL_RESULTS['targets'].setdefault(target_email, {})['email_lookup'] = output_data['results']
        else:
            print("⚠️ Holehe ran but did not return expected structured data. Check console output for logs.")
            GLOBAL_RESULTS['targets'].setdefault(target_email, {})['email_lookup'] = {"status": "Holehe output structure error"}

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Holehe (Check if installed or email valid): {e.stderr.strip()}")
        GLOBAL_RESULTS['targets'].setdefault(target_email, {})['email_lookup'] = {"status": f"Tool error: {e.stderr.strip()}"}
    except FileNotFoundError:
        print("❌ Error: 'holehe' command not found. Did you run 'pip install holehe'?")
    except subprocess.TimeoutExpired:
        print("❌ Error: Holehe process timed out (180 seconds).")
        
    print("\n--- Email lookup complete. ---")

def domain_recon():
    """Placeholder for domain reconnaissance (e.g., WHOIS)."""
    target = input("Enter domain name (e.g., example.com): ").strip()
    print(f"\n🌐 Starting recon for domain: '{target}'...")
    print("➡️ Placeholder: Integrate python-whois or dnspython logic here.")
    GLOBAL_RESULTS['targets'].setdefault(target, {})['domain_recon'] = {"status": "Placeholder run", "target": target}
    print("\n--- Domain recon complete. ---")

def exif_data_extraction():
    """Extracts EXIF metadata, including GPS, from an image file."""
    image_path = input("Enter path to local image file: ").strip()
    if not os.path.exists(image_path):
        print("❌ Error: File not found at the specified path.")
        return

    print(f"\n📸 Extracting EXIF data from: '{os.path.basename(image_path)}'...")
    results = {}
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        if not tags:
            results['Status'] = "No EXIF tags found."
        else:
            # Filter and format important tags
            for tag_name, tag_value in tags.items():
                if tag_name not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                    results[tag_name] = str(tag_value)
            
            if 'GPS GPSLatitude' in tags:
                results['GPS_COORDINATES'] = f"Latitude: {str(tags['GPS GPSLatitude'])}, Longitude: {str(tags['GPS GPSLongitude'])}"
                print(f"📍 **GPS Coordinates Found!**")
            
            results['Status'] = "EXIF Data Found"
            
    except Exception as e:
        results['Status'] = f"Error processing file: {e}"
        print(f"❌ An error occurred: {e}")

    target_name = os.path.basename(image_path)
    GLOBAL_RESULTS['targets'].setdefault(target_name, {})['exif_data'] = results
    print("\n--- Image Forensics complete. ---")


def toggle_opsec():
    """Toggles the global OPSEC flag for using Tor proxy."""
    global OPSEC_ENABLED
    OPSEC_ENABLED = not OPSEC_ENABLED
    
    if OPSEC_ENABLED:
        print("\n🛡️ **OPSEC (Tor Proxy) is now ON.** All lookups will route through Tor.")
        print("   Ensure the Tor service or Tor Browser is running.")
    else:
        print("\n🛑 **OPSEC (Tor Proxy) is now OFF.** Lookups will use your direct IP.")
        
def generate_report():
    """Saves all collected data to a structured JSON file."""
    if not GLOBAL_RESULTS['targets']:
        print("⚠️ No data collected. Exiting without generating report.")
        sys.exit(0)
        
    filename = f"OSINT_Fusion_Report_{time.strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(GLOBAL_RESULTS, f, indent=4)
        
        print("\n" + "#"*55)
        print(f"✅ **REPORT GENERATED SUCCESSFULLY**")
        print(f"   File: {filename}")
        print(f"   Targets Investigated: {len(GLOBAL_RESULTS['targets'])}")
        print("#"*55)
        
    except Exception as e:
        print(f"\n❌ ERROR saving report: {e}")
        
    sys.exit(0)


def main():
    """Main function to run the menu loop."""
    while True:
        try:
            display_menu()
            choice = input("Enter your choice (1-6): ")

            if choice == '1':
                username_search()
            elif choice == '2':
                email_lookup()
            elif choice == '3':
                domain_recon()
            elif choice == '4':
                exif_data_extraction()
            elif choice == '5':
                toggle_opsec()
            elif choice == '6':
                generate_report()
            else:
                print("\n❌ Invalid choice. Please enter a number between 1 and 6.")
                
        except KeyboardInterrupt:
            print("\nInterrupt detected. Generating final report.")
            generate_report()
        
        input("\nPress Enter to return to the main menu...") 

if __name__ == "__main__":
    main()