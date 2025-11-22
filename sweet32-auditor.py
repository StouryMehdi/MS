import sys
import os
import socket
import ssl
import re
from contextlib import closing
import time
import logging

# --- Configuration ---
# Setting the SSL context to ONLY allow the weak 3DES cipher suites.
WEAK_3DES_CIPHERS = "3DES" 
TIMEOUT_SECONDS = 3

# List of SSL/TLS protocol contexts to test for maximum coverage (Reintroducing the advanced check)
PROTOCOL_CONTEXTS = [
    ssl.PROTOCOL_TLS_CLIENT, 
    ssl.PROTOCOL_TLSv1, 
    ssl.PROTOCOL_TLSv1_1, 
]

# --- Setup Logging ---
log_file = f"sweet32_audit_{time.strftime('%Y%m%d_%H%M%S')}.log"
# Set up logging to output to console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode='w')
    ]
)

# Define logger helper functions for color coding and reporting
def log_terminal(message):
    """Prints message to console only (including colors)."""
    print(message, end='')
    sys.stdout.flush()

def log_report(ip, port_status, vul_status, cipher_evidence):
    """Logs the final result to both console (with color) and file (without color)."""
    
    # 1. Console Output (with color)
    if "VULNERABLE" in vul_status:
        color_code = "\033[0;31m" # Red
    elif "No Vulnerability" in vul_status:
        color_code = "\033[0;32m" # Green
    else:
        color_code = "\033[0;33m" # Yellow/Filtered
        
    term_output_line = ""
    if cipher_evidence:
        term_output_line = f"{color_code}%-30s\033[0m | {color_code}%-30s\033[0m\n" % (vul_status, cipher_evidence)
    else:
        term_output_line = f"{color_code}%-30s\033[0m | %-30s\n" % (vul_status, "N/A")

    log_terminal(term_output_line)
    
    # 2. File Output (without color)
    file_output = "%-20s | %-12s | %-30s | %-30s" % (ip, port_status, vul_status, cipher_evidence if cipher_evidence else "N/A")
    logging.info(file_output)
    
def check_open_port(ip, port):
    """Performs a fast TCP connection check."""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(TIMEOUT_SECONDS)
            sock.connect((ip, port))
            return True
    except socket.error:
        return False

def check_sweet32_vulnerability(ip, port):
    """
    Attempts to establish an SSL/TLS connection using only 3DES across multiple protocols.
    Returns the negotiated cipher name (string) if vulnerable, or None otherwise.
    """
    for protocol in PROTOCOL_CONTEXTS:
        ssl_sock = None
        try:
            # Create SSL context specific to the protocol version
            context = ssl.SSLContext(protocol)
            context.set_ciphers(WEAK_3DES_CIPHERS)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(TIMEOUT_SECONDS)
                sock.connect((ip, port))
                ssl_sock = context.wrap_socket(sock, server_hostname=ip)
                
                # Success: Vulnerability confirmed!
                negotiated_cipher = ssl_sock.cipher()
                if negotiated_cipher:
                    return negotiated_cipher[0]
                
        except ssl.SSLError:
            continue # Protocol failed, try the next one
        except socket.error:
            return None # Connection issue
        finally:
            if ssl_sock:
                ssl_sock.close()
    
    return None # No vulnerability found across all tested protocols


def auditor_main():
    """Main function to control the audit process and display results."""
    
    logging.info("\n--- Simplified SWEET32 Cipher Auditor (No Scapy/No Sudo Required) ---")
    
    # Check for the required input file
    if not os.path.exists("ip-list.txt"):
        print("[CRITICAL ERROR] 'ip-list.txt' not found.")
        print("Please create this file and populate it with target IP addresses (one per line).")
        sys.exit(1)
    
    # User input for the target port
    try:
        port_input = input("Please enter the target port number (e.g., 443, 8443): ")
        target_port = int(port_input)
        if not 1 <= target_port <= 65535:
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid port number.")
        sys.exit(1)

    # Output header
    logging.info("-" * 97)
    print("\n%-20s | %-12s | %-30s | %-30s" % ("IP Address", "Port Status", "Vulnerability Status", "Negotiated Cipher (Evidence)"))
    print("-" * 97)
    
    logging.info(f"[*] Audit results will be logged to {log_file}")

    try:
        with open("ip-list.txt", 'r') as f:
            for line in f:
                ip = line.strip()
                if not ip or ip.startswith('#'):
                    continue

                log_terminal("%-20s | " % ip)

                # 1. SCAN: Check if the port is open
                if not check_open_port(ip, target_port):
                    log_report(ip, "Filtered/Closed", "N/A", "N/A")
                    continue
                
                log_terminal("\033[0;32m%-12s\033[0m | " % "Open")

                # 2. IDENTIFY + ACTION: Run the vulnerability check and extract evidence
                negotiated_cipher = check_sweet32_vulnerability(ip, target_port)
                
                # 3. Report Generation
                if negotiated_cipher:
                    log_report(ip, "Open", "VULNERABLE (3DES ACCEPTED)", negotiated_cipher)
                else:
                    log_report(ip, "Open", "No Vulnerability Found", "N/A")
            
            logging.info("-" * 97)
            logging.info("[AUDIT COMPLETE] Please review the log file for clean results.")


    except KeyboardInterrupt:
        print("\n[STOPPED] Audit interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    auditor_main()