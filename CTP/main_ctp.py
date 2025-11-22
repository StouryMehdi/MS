# main_ctp.py
from vulnerability_scanner import AIScanner
from file_simulator import RansomwareLab
from sqli_lab import SQLInjectionLab
import sys

# Hypothetical vulnerable code to scan
CODE_TO_SCAN = [
    "def login(u, p):",
    "    query = 'SELECT * FROM users WHERE u = ' + u + ' AND p = ' + p", 
    "    conn = db.connect(user='root', password='password')",
    "def get_api():",
    "    SECRET_KEY = 'hardcoded-value'" 
]

def print_menu():
    """Displays the main program menu with all choices."""
    print("\n" + "="*60)
    print("      CYBERSECURITY TRAINING PLATFORM (CTP) - Main Menu")
    print("="*60)
    print("📚 Blue Team / Analysis Modules (Defensive)")
    print("1. Run AI Vulnerability Scanner (Simulates rapid code analysis)")
    print("-" * 60)
    print("🧪 Red Team / Pentesting Modules (Ethical Labs)")
    print("2. Run Ransomware Lab Simulation (Simulates file encryption impact)")
    print("3. Run SQL Injection Lab (Demonstrates exploit payload creation)")
    print("-" * 60)
    print("4. Exit Program")
    print("=" * 60)

def main():
    """Main function to control the CTP."""
    scanner = AIScanner()
    ransom_lab = RansomwareLab()
    sqli_lab = SQLInjectionLab()

    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            print("\n--- RUNNING MODULE 1: AI VULNERABILITY SCANNER ---")
            scanner.run_scan(CODE_TO_SCAN)
        
        elif choice == '2':
            print("\n--- RUNNING MODULE 2: RANSOMWARE LAB SIMULATION ---")
            
            # Phase 1: Attack (Encryption and Note creation)
            encryption_key = ransom_lab.encrypt_files()
            
            # Phase 2: Recovery
            input("\n[LAB] **Simulated Recovery Phase:** Press Enter to decrypt files using the stored key...")
            ransom_lab.decrypt_files(encryption_key)

        elif choice == '3':
            sqli_lab.run_lab()
            
        elif choice == '4':
            print("Exiting CTP. Happy learning!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()