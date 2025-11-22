import sys
import os
import re
import ipaddress
import time

# Attempt to import Scapy, required for raw packet manipulation
try:
    from scapy.all import IPv6, ICMPv6EchoRequest, TCP, sr1, sr, IP
except ImportError:
    print("\n[INIT ERROR] The 'scapy' library is not installed.")
    print("Please run the provided 'install.sh' script first.")
    sys.exit(1)

# --- Configuration ---
# Standard ports for checking open services on a target
AUDIT_PORTS = [22, 80, 443, 3389, 5985] 
TIMEOUT_PER_PACKET = 1.0 # Timeout for ICMPv6 reachability test
SCAN_TIMEOUT = 3.0 # Total timeout for the TCP scan
REACHABILITY_ATTEMPTS = 3

def validate_input(ipv4_address):
    """Ensure the input is a valid IPv4 address."""
    try:
        ipaddress.IPv4Address(ipv4_address)
        return True
    except ipaddress.AddressValueError:
        print(f"[ERROR] Invalid IPv4 address format or value: {ipv4_address}")
        sys.exit(1)

def calculate_6to4_address(ipv4_address):
    """
    Calculates the 6to4 IPv6 address entirely in Python.
    Format: 2002: <ipv4_hex> :: <ipv4_hex>
    """
    print(f"[*] Calculating 6to4 address from IPv4: {ipv4_address}")
    
    try:
        # Convert IPv4 dotted decimal to hexadecimal format
        ip_parts = [int(x) for x in ipv4_address.split('.')]
        ipv4_hex_segment = f"{ip_parts[0]:02x}{ip_parts[1]:02x}:{ip_parts[2]:02x}{ip_parts[3]:02x}"
        
        # Construct the 6to4 relay anycast address (the common test target)
        target_6to4_address = f"2002:{ipv4_hex_segment}::{ipv4_hex_segment}"
        print(f"[+] Generated 6to4 IPv6 Target: {target_6to4_address}")
        return target_6to4_address
        
    except Exception as e:
        print(f"[ERROR] Failed to convert IPv4 address: {e}")
        return None

def test_reachability(interface, ipv6_target):
    """
    Tests reachability using Scapy to send raw ICMPv6 Echo Request packets.
    Includes retry logic for robustness.
    """
    print(f"[*] Testing reachability via {interface} (ICMPv6, {REACHABILITY_ATTEMPTS} attempts)...")
    
    for attempt in range(1, REACHABILITY_ATTEMPTS + 1):
        # Craft the ICMPv6 Echo Request packet
        packet = IPv6(dst=ipv6_target) / ICMPv6EchoRequest()
        
        # Send the packet and wait for a single response
        response = sr1(packet, timeout=TIMEOUT_PER_PACKET, iface=interface, verbose=0)
        
        if response and response.haslayer(ICMPv6EchoRequest):
            print(f"\n[VULNERABILITY CONFIRMED] Target is REACHABLE via Shadow IPv6 Tunnel!")
            return True
        
        time.sleep(0.5) # Short delay before next attempt

    print("\n[INFO] Target is NOT REACHABLE via 6to4 tunnel or tunnel is disabled.")
    return False

def scan_ipv6_ports(ipv6_target, interface):
    """
    Performs a raw TCP SYN port scan on the reachable IPv6 address using Scapy.
    """
    ports_str = ",".join(map(str, AUDIT_PORTS))
    print(f"\n[+] PIVOTING: Performing TCP SYN scan on ports ({ports_str}) on {ipv6_target}...")
    
    # Craft the packet list: IPv6 header + TCP SYN flag for each port
    packet = IPv6(dst=ipv6_target) / TCP(dport=AUDIT_PORTS, flags="S")
    
    # Send and receive packets with a combined timeout
    answered, unanswered = sr(packet, timeout=SCAN_TIMEOUT, iface=interface, verbose=0)
    
    open_ports = []
    
    for sent_packet, received_packet in answered:
        # Check for TCP SYN-ACK response (flags=0x12)
        if received_packet.haslayer(TCP) and received_packet[TCP].flags == 0x12:
            open_ports.append(sent_packet[TCP].dport)
            
    print("\n--- Custom IPv6 Scan Results ---")
    if open_ports:
        print(f"[SUCCESS] Open Ports Found: {', '.join(map(str, sorted(open_ports)))}")
    else:
        print("[INFO] No common ports found open on the Shadow IPv6 interface.")
    print("----------------------------")
    
def display_syntax():
    print("\nSyntax: sudo python3 shadow_ipv6_auditor.py <interface> <ipv4_address>")
    print("Example: sudo python3 shadow_ipv6_auditor.py eth0 192.168.1.10")
    print("\n!!! NOTE: This tool requires 'sudo' (root) and the 'scapy' library. !!!")
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        display_syntax()
        
    interface = sys.argv[1]
    ipv4_address = sys.argv[2]
    
    # 1. Critical Checks
    validate_input(ipv4_address)
    if os.geteuid() != 0:
        print("\n[CRITICAL] This tool uses raw sockets (Scapy) and MUST be run with 'sudo' (root privileges).")
        sys.exit(1)
    
    print("\n--- Unique Shadow IPv6 Tunnel Auditor (6to4) ---")
    
    try:
        # 2. Calculation
        ipv6_target = calculate_6to4_address(ipv4_address)
        if not ipv6_target: return

        print("\n" + "=" * 60)
        print(f"AUDITING: Interface={interface}, IPv4 Target={ipv4_address}")
        print("=" * 60)
        
        # 3. Reachability Test
        is_reachable = test_reachability(interface, ipv6_target)

        # 4. Automatic Port Scan Pivot
        if is_reachable:
            scan_ipv6_ports(ipv6_target, interface)
            print("\n[REPORTING NOTE]")
            print("The client's network is susceptible to an unmonitored IPv6 attack surface.")
            print("Mitigation requires disabling the 6to4 tunneling mechanism on the target host.")

    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted the audit process.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[CRITICAL ERROR] An unexpected error occurred: {e}")
        sys.exit(1)
    
if __name__ == "__main__":
    main()