#!/usr/bin/python3
import socket
import subprocess
import re
import sys
from concurrent.futures import ThreadPoolExecutor

# Define common ports globally so all functions can access it
COMMON_PORTS = [
    21, 22, 23, 25, 80, 139, 443, 445, 3389, 8080, 8443
]

def get_connected_network_simple():
    """Get connected network information (local IP and gateway)"""
    try:
        # Get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # Try to get gateway from route command
        gateway = "Unknown"
        try:
            if sys.platform.startswith("win"):  # Windows
                result = subprocess.run(["route", "print", "0.0.0.0"], 
                                        capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if "0.0.0.0" in line and "On-link" not in line:
                        parts = line.split()
                        if len(parts) >= 3 and parts[0] == "0.0.0.0":
                            gateway = parts[2]
                            break
            else:  # Linux/Mac
                result = subprocess.run(["route", "-n"], 
                                        capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if "0.0.0.0" in line or "default" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            gateway = parts[1]
                            break
        except:
            gateway = "Unknown"
        
        return local_ip, gateway
        
    except Exception as e:
        print(f"❌ Network detection failed: {e}")
        return None, None

def get_network_ips_simple():
    """Simple network scanning using ARP and ping sweep"""
    local_ip, gateway = get_connected_network_simple()
    
    if not local_ip:
        return []
    
    print(f"📍 Your IP: {local_ip}")
    if gateway and gateway != "Unknown":
        print(f"📍 Gateway: {gateway}")
    
    network_prefix = '.'.join(local_ip.split('.')[:3]) + '.'
    print(f"🔍 Scanning local network: {network_prefix}1-254")
    print("⏳ This may take a moment...")
    
    ips = []
    
    # ARP scan
    try:
        # Note: 'shell=True' is often needed for 'arp -a' on Windows
        result = subprocess.run(["arp", "-a"], 
                                capture_output=True, text=True, shell=True)
        
        for line in result.stdout.split('\n'):
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match and ip_match.group(1).startswith(network_prefix):
                ips.append(ip_match.group(1))
                
    except Exception as e:
        print(f"⚠️  ARP scan issue: {e}")
    
    # If ARP doesn't find much, try ping sweep
    if len(ips) <= 2:  # Only found gateway and maybe ourselves
        print("🔄 ARP table sparse, performing ping sweep...")
        ips.extend(ping_sweep_simple(network_prefix))
    
    # Remove duplicates and sort
    return sorted(set(ips))

def ping_sweep_simple(network_prefix):
    """Simple ping sweep to find active hosts"""
    active_ips = []
    
    def ping_host(ip):
        try:
            # Determine ping command based on OS
            if sys.platform.startswith("win"):  # Windows
                # CHANGED TIMEOUT to 2000ms (-w 2000)
                result = subprocess.run(
                    ["ping", "-n", "1", "-w", "2000", ip], 
                    capture_output=True,
                    timeout=3 
                )
            else:  # Linux/Mac
                # CHANGED TIMEOUT to 2 seconds (-W 2)
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "2", ip],
                    capture_output=True,
                    timeout=3
                )
            if result.returncode == 0:
                return ip
        except:
            pass
        return None
    
    # Generate IPs to scan (1-254 in the network)
    ip_range = [f"{network_prefix}{i}" for i in range(1, 255)]
    
    # Multi-threaded ping
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(ping_host, ip_range)
        active_ips = [ip for ip in results if ip]
    
    return active_ips

def scan_common_ports(target_ip):
    """Scan only common ports from services list"""
    print(f"\n🔎 Scanning common ports on {target_ip}...")
    print("⏳ This may take a few seconds...")
    
    open_ports = []
    
    def check_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
        except:
            pass
    
    # Multi-threaded port scanning using global COMMON_PORTS
    with ThreadPoolExecutor(max_workers=200) as executor:
        executor.map(check_port, COMMON_PORTS)
    
    return sorted(open_ports)

def get_service_name(port):
    """Get common service name for port"""
    services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS",
        143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP",
        5900: "VNC", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }
    return services.get(port, "Unknown")

def main():
    print("🌐 Network IP Scanner with Common Port Scanning")
    print("=" * 50)
    
    target_ip = None
    original_target_input = None
    
    # --- PROMPT for Local or External Scan ---
    while True:
        scan_choice = input("🔎 Scan local network (L) or enter a specific target (S)? (L/S/q): ").lower()
        if scan_choice == 'q':
            print("👋 Goodbye!")
            return
        elif scan_choice in ['l', 's']:
            break
        else:
            print("❌ Invalid choice. Please enter 'L', 'S', or 'q'.")

    if scan_choice == 'l':
        # --- Local Scan Logic (Original Behavior) ---
        ips = get_network_ips_simple()
        
        if not ips:
            print("❌ No IP addresses found in network.")
            return
        
        print(f"\n📱 Found {len(ips)} IP addresses:")
        print("-" * 40)
        for i, ip in enumerate(ips, 1):
            print(f"{i:2}. {ip}")
        
        # Let user choose target from the list
        while True:
            try:
                choice = input(f"\n🎯 Select IP to scan (1-{len(ips)}) or 'q' to quit: ")
                if choice.lower() == 'q': return
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(ips):
                    target_ip = ips[choice_num - 1]
                    original_target_input = target_ip # Use IP as input name
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(ips)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    else: # User chose 's' - Enter specific target
        # --- External/Specific Target Logic (New Behavior) ---
        while True:
            original_target_input = input("🎯 Enter Target IP or Domain Name: ")
            if not original_target_input: continue
            
            try:
                # Resolve domain name to IP
                target_ip = socket.gethostbyname(original_target_input)
                print(f"✅ Target IP resolved to: {target_ip}")
                break
            except socket.gaierror:
                print(f"❌ Could not resolve hostname/IP: {original_target_input}. Try again.")

    # --- Execution continues only if target_ip is set ---
    if not target_ip:
        print("👋 Quitting.")
        return

    # Scan common ports on selected IP
    open_ports = scan_common_ports(target_ip)
    
    # Display results
    print(f"\n📊 Port Scan Results for {original_target_input} ({target_ip}):")
    print("=" * 50)
    
    if open_ports:
        print(f"✅ Found {len(open_ports)} open ports:")
        print("-" * 40)
        print(f"{'Port':<8} {'Service':<12} {'Status':<10}")
        print("-" * 40)
        for port in open_ports:
            service = get_service_name(port)
            print(f"{port:<8} {service:<12} {'OPEN':<10}")
    else:
        print("❌ No common open ports found")
    
    print(f"\n🎯 Scanned {len(COMMON_PORTS)} common ports")
    
    # Option to scan another IP
    while True:
        another = input("\n🔄 Scan another target? (y/n): ").lower()
        if another == 'y':
            main()  # Restart
            break
        elif another == 'n':
            break
        else:
            print("❌ Please enter 'y' or 'n'")

if __name__ == "__main__":
    main()