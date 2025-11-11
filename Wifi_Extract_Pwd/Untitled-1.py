with open(r"c:\Users\dll\Desktop\BAT FILES\Wifi_Extract_Pwd\WiFi_Passwords_Only_2025-11-11.txt", "r") as file:
    lines = file.readlines()

with open(r"c:\Users\dll\Desktop\BAT FILES\Wifi_Extract_Pwd\WiFi_Passwords_Only_2025-11-11.txt", "w") as file:
    for line in lines:
        # Remove space after every word
        modified_line = ' '.join(word.strip() for word in line.split())
        file.write(modified_line + '\n')