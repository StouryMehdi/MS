import sys, subprocess, os
import argparse

# Configuration for Nmap
NMAP_OPTIONS = "-sV -O -T4" # Service version, OS detection, aggressive timing

def load_ips_from_file(input_file):
    """Reads IPs from a file, one per line, and returns a list."""
    try:
        with open(input_file, 'r') as f:
            # Clean up IPs: strip whitespace/newlines and filter out empty lines
            ips = [line.strip() for line in f if line.strip()]
        return ips
    except FileNotFoundError:
        print(f"[ERROR] Input file not found: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Could not read file {input_file}: {e}")
        sys.exit(1)

def run_nmap_scan(ip_list, output_file):
    """Executes the Nmap command against the provided list of IPs."""
    if not ip_list:
        print("[!] The list of IPs is empty. Skipping Nmap.")
        return

    print(f"\n[+] Starting Nmap scan on {len(ip_list)} host(s)...")

    try:
        # Construct the command: nmap [OPTIONS] -oN [file] [IPs]
        command = [
            "nmap",
            *NMAP_OPTIONS.split(), 
            "-oN", output_file,   
            *ip_list              
        ]
        
        print(f"[+] Command: {' '.join(command)}")

        # Run Nmap as a blocking external process
        subprocess.run(command, check=True)
        
        print(f"\n[SUCCESS] Nmap results saved to: {output_file}")
        
    except subprocess.CalledProcessError:
        print("\n[ERROR] Nmap failed. Check the command and ensure you have permissions (e.g., run with 'sudo').")
    except FileNotFoundError:
        print("\n[ERROR] Nmap command not found. Please ensure Nmap is installed and in your system PATH.")

def parse_arguments():
    """Handles command line arguments for the Nmap script."""
    parser = argparse.ArgumentParser(
        description='Runs Nmap on a list of hosts read from an input file.',
        epilog=f"Example: python3 {os.path.basename(sys.argv[0])} live_ips.txt -o detailed_scan.txt"
    )

    parser.add_argument('input_file', type=str, help='Path to the file containing one IP per line (e.g., live_ips.txt)')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file for Nmap results')
    
    return parser.parse_args()

if __name__ == '__main__':
    # 1. Parse Arguments
    args = parse_arguments()

    # 2. Load IPs
    live_ips = load_ips_from_file(args.input_file)

    # 3. Run Nmap Scan
    run_nmap_scan(live_ips, args.output)