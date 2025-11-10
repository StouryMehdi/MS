import sys, subprocess, platform, os
from concurrent.futures import ThreadPoolExecutor

# Check a single host for activity
def check_host(ip):
    # choose correct ping flag for the OS
    ping_flag = "-n" if platform.system().lower().startswith("win") else "-c"
    try:
        # increase timeout a bit and rely on returncode (works cross-platform)
        res = subprocess.run(["ping", ping_flag, "1", ip], timeout=1.5, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            return ip
    except Exception:
        pass
    return None

if __name__ == '__main__':
    # Basic argument check
    if len(sys.argv) != 3:
        script = os.path.basename(sys.argv[0])
        print(f"Usage: python {script} <subnet_prefix> <output_filename>")
        print(f"Example: python {script} 192.168.1 live_ips.txt")
        sys.exit(1)

    subnet, filename = sys.argv[1], sys.argv[2]
    
    # Generate list of IPs to scan (1 to 254)
    ips = [f"{subnet}.{addr}" for addr in range(1, 255)]
    print(f"Scanning {subnet}.1 - {subnet}.254...")

    # Run checks concurrently using 50 workers
    with ThreadPoolExecutor(max_workers=50) as executor:
        # executor.map applies check_host to all IPs and returns results in order
        live_ips = [ip for ip in executor.map(check_host, ips) if ip]

    # Write results to file
    if live_ips:
        with open(filename, "w") as f:
            f.write('\n'.join(sorted(live_ips)) + '\n')
        print(f"Successfully wrote {len(live_ips)} live IP(s) to {filename}")
    else:
        print("No live hosts found.")