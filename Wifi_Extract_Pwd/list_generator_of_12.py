import itertools
import string
import sys
import os

def generate_wordlist(length):
    """
    Generates a wordlist of a specified fixed length using a comprehensive character set.
    """
    # --- 1. Define the Comprehensive Character Set ---
    
    # 1. Letters (A-Z, a-z)
    all_letters = string.ascii_letters 
    
    # 2. Specific Symbols (from your list)
    # Note: string.punctuation includes many of these, but we'll use your explicit list.
    specific_symbols = r". , ; : ? ! ( ) [ ] { } - _ @ # $ % ^ & * + = / \ | ~"
    # Remove spaces and combine the rest, adding single space back if needed
    symbol_set = "".join(specific_symbols.split()) 
    
    # For a true "all characters" set, we typically add numbers (0-9) as well
    all_numbers = string.digits
    
    # Combine all characters into one set for permutation
    # The set() operation ensures each character is only used once
    CHARACTERS = "".join(sorted(set(all_letters + all_numbers + symbol_set)))
    
    # --- 2. Configuration and Warning ---
    
    output_filename = f"wordlist_len_{length}.txt"
    total_combinations = len(CHARACTERS) ** length
    
    print("=" * 40)
    print("⚠️  WARNING: Generating Large Wordlist ⚠️")
    print(f"Character Set Size: {len(CHARACTERS)}")
    print(f"Total Combinations (Length {length}): {total_combinations:,}")
    print(f"Output File: {output_filename}")
    print("=" * 40)
    
    if length > 7:
        print("For lengths > 7, this will take an EXTREMELY long time.")
        user_confirm = input("Are you sure you want to continue? (y/N): ")
        if user_confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit()

    # --- 3. Generation and File Writing ---
    
    print("\nStarting generation... (Press Ctrl+C to stop)")
    
    try:
        with open(output_filename, 'w') as f:
            # itertools.product generates the Cartesian product (all combinations)
            # The 'repeat=length' ensures the fixed length is used
            for combination in itertools.product(CHARACTERS, repeat=length):
                word = "".join(combination)
                f.write(word + "\n")
                
        print(f"\n✅ Generation complete. Wordlist saved to {os.path.abspath(output_filename)}")

    except Exception as e:
        print(f"\n❌ An error occurred during file writing: {e}")
    except KeyboardInterrupt:
        print("\n\n🛑 Operation interrupted by user (Ctrl+C).")
        print(f"Current progress saved to {output_filename}")


if __name__ == "__main__":
    # >>> CHANGE THE LENGTH HERE <<<
    # Setting this to 12 (as requested) will likely crash your system.
    # Recommended length for testing is 3 or 4.
    FIXED_LENGTH = 4 
    
    generate_wordlist(FIXED_LENGTH)