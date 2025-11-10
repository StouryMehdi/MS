#!/usr/bin/python3
import socket

# Config
IP = "0.0.0.0"
PORT = 6996
BUFSIZE = 100

print(f"Starting server on {IP}:{PORT}...")

# 1. Setup and Listen
try:
    s = socket.socket() # socket.AF_INET and socket.SOCK_STREAM are default
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allows immediate port reuse
    s.bind((IP, PORT))
    s.listen(1)
    print("Listening for a connection (Press Ctrl+C to stop)...")

    # 2. Accept single client
    conn, addr = s.accept()
    print(f'✅ Connected to: {addr}')

    # 3. Receive and Echo loop
    while True:
        data = conn.recv(BUFSIZE)
        if not data:
            print(f"Client {addr} disconnected.")
            break
        print(f"Received: {data.decode().strip()}")
        conn.sendall(data) # Use sendall for guaranteed sending

# 4. Handle Shutdown Signals
except KeyboardInterrupt:
    print("\n🛑 Server shutting down due to Ctrl+C...")
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")

# 5. Cleanup
finally:
    # Ensure all sockets are closed, regardless of how the script terminates
    if 'conn' in locals() and conn:
        conn.close()
        print("Client connection closed.")
    if 's' in locals() and s:
        s.close()
        print("Server socket closed.")
    
    print("Program terminated.")