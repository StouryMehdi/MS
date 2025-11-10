import socket
import threading
import rsa
import sys

# --- Configuration ---
# Use localhost IP (127.0.0.1) for testing on the same machine.
# If connecting across a network, replace "127.0.0.1" with the host's actual private IP address.
HOST_IP = "127.0.0.1" 
PORT = 55556

# --- 1. Key Generation ---
# Generate our own public and private keys using 1024 bits for the RSA algorithm.
public_key, private_key = rsa.newkeys(1024)
partner_public_key = None

# --- 2. Encrypted Messaging Functions ---
def sending_messages(client_socket, partner_pk):
    """Handles sending messages, encrypting them with the partner's public key."""
    while True:
        try:
            message = input("You: ")
            if message.lower() == 'exit':
                break
            
            # Encrypt the message using the partner's public key (RSA.encrypt)
            encrypted_message = rsa.encrypt(message.encode('utf-8'), partner_pk)
            client_socket.sendall(encrypted_message)
            
        except Exception as e:
            print(f"\n[ERROR] Disconnected or failed to send message: {e}")
            break

def receiving_messages(client_socket, own_pk):
    """Handles receiving messages, decrypting them with our private key."""
    while True:
        try:
            # Receive the encrypted message
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                print("\nPartner disconnected.")
                break
                
            decrypted_message = rsa.decrypt(encrypted_message, own_pk).decode('utf-8')
            print(f"\nPartner: {decrypted_message}")
            
        except Exception as e:
            print(f"\n[ERROR] Disconnected or failed to receive message: {e}")
            break

# --- 3. Host/Connect Choice and Setup ---

def exchange_keys(client_socket, is_host):
    """Handles the public key exchange."""
    try:
        if is_host:
            # 1. Host sends its public key to the client
            client_socket.send(public_key.save_pkcs1('PEM'))
            # 2. Host receives the partner's public key
            partner_public_key_raw = client_socket.recv(1024)
        else:
            # 1. Client receives the partner's public key from the host
            partner_public_key_raw = client_socket.recv(1024)
            # 2. Client sends its public key to the host
            client_socket.send(public_key.save_pkcs1('PEM'))
            
        return rsa.PublicKey.load_pkcs1(partner_public_key_raw)
    except Exception as e:
        print(f"[CRITICAL ERROR] Key exchange failed: {e}")
        sys.exit()

def close_connection(client_socket):
    """Closes the client socket."""
    if client_socket:
        client_socket.close()
        print("--- Connection Closed ---")

def start_chat_threads(client_socket, partner_pk, own_pk):
    """Initializes and starts the sending and receiving threads."""
    print("--- Chat Started ---")
    print("Enter your messages and press Enter. Type 'exit' to close the connection.")

    send_thread = threading.Thread(target=sending_messages, args=(client_socket, partner_pk))
    send_thread.daemon = True
    send_thread.start()

    receive_thread = threading.Thread(target=receiving_messages, args=(client_socket, own_pk))
    receive_thread.daemon = True
    receive_thread.start()

    # Keep the main thread alive to allow daemon threads to run
    while send_thread.is_alive() and receive_thread.is_alive():
        pass

    print("--- Chat Ended ---")

# ... (rest of the code remains the same)

# --- 4. Start Communication ---
if __name__ == "__main__":
    client_socket = None
    partner_public_key = None
    try:
        choice = input(f"Do you want to host (1) or to connect (2) to {HOST_IP}:{PORT}?: ")

        if choice == "1":
            # --- Host Logic (Server) ---
            print("Starting host...")
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server.bind((HOST_IP, PORT))
                server.listen(1)
                print(f"Listening on {HOST_IP}:{PORT}...")
                client_socket, address = server.accept()
                print(f"Connection established with {address}")
                partner_public_key = exchange_keys(client_socket, is_host=True)
            except Exception as e:
                print(f"[CRITICAL ERROR] Failed to host: {e}")
                sys.exit()

        elif choice == "2":
            # --- Connect Logic (Client) ---
            print("Connecting to host...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((HOST_IP, PORT))
                print("Connection established.")
                partner_public_key = exchange_keys(client_socket, is_host=False)
            except Exception as e:
                print(f"[CRITICAL ERROR] Failed to connect: {e}")
                sys.exit()

        else:
            print("Invalid choice. Exiting.")
            sys.exit()

        # --- 4. Start Communication ---
        if client_socket and partner_public_key:
            start_chat_threads(client_socket, partner_public_key, private_key)

    except KeyboardInterrupt:
        print("\n--- Chat Interrupted by user ---")
    finally:
        close_connection(client_socket)
