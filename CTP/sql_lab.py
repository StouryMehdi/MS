# sqli_lab.py
from typing import List

class SQLInjectionLab:
    """Module for demonstrating SQL Injection techniques safely."""

    def __init__(self):
        self.vulnerable_template = (
            "SELECT user_id, username, role FROM users "
            "WHERE username = '{username}' AND password = '{password}'"
        )

    def demonstrate_injection(self, username_input: str, password_input: str) -> List[str]:
        """
        Simulates the formation of a malicious SQL query.
        """
        
        # Benign Query
        benign_query = self.vulnerable_template.format(
            username=username_input, 
            password=password_input
        )
        
        # Malicious Payload (Authentication Bypass: ' OR '1'='1' -- )
        payload = "admin' OR '1'='1' -- " 

        malicious_query = self.vulnerable_template.format(
            username=payload,
            password=""
        )
        
        return [benign_query, malicious_query]

    def run_lab(self):
        """Runs the interactive SQLi demonstration lab."""
        print("\n--- RUNNING SQL INJECTION DEMONSTRATION LAB (Safe Simulation) ---")
        
        # Standard input simulation
        print("\n[STEP 1: Standard Benign Login]")
        benign_username = input("Enter standard username (e.g., testuser): ")
        benign_password = input("Enter standard password: ")
        
        benign_result, _ = self.demonstrate_injection(benign_username, benign_password)
        print("\nGenerated Query (Benign):")
        print(f"  {benign_result}")

        # Injection simulation
        print("\n[STEP 2: Authentication Bypass Attack]")
        input("Press Enter to demonstrate the classic ' OR '1'='1' -- injection...")
        
        malicious_username = "admin' OR '1'='1' -- "
        malicious_password = "any_password"
        
        _, malicious_result = self.demonstrate_injection(malicious_username, malicious_password)
        
        print("\nGenerated Query (MALICIOUS PAYLOAD):")
        print(f"  Payload: {malicious_username}")
        print(f"  Resulting Query (Database Execution):")
        print(f"  {malicious_result}")
        print("\n*** IMPACT: This query bypasses authentication, granting access. ***")
        print("Blue Team Fix: Use Parameterized Queries!")