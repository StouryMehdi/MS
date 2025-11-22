#!/bin/bash

# Custom Installation Script for Shadow IPv6 Auditor
# Ensures required Python packages are installed with root privileges.

echo "--- Installing Dependencies for Shadow IPv6 Auditor ---"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python 3 could not be found. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "[INFO] pip3 not found. Attempting to install pip..."
    # Attempt to install pip using standard Linux package managers
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
    else
        echo "[ERROR] Cannot automatically install pip3. Please install it manually."
        exit 1
    fi
fi

# Install Scapy. This often requires root privileges to configure correctly.
echo "[*] Installing 'scapy' library using pip3. (Requires sudo)"
sudo pip3 install scapy

if [ $? -eq 0 ]; then
    echo "--------------------------------------------------------"
    echo "[SUCCESS] Installation complete."
    echo "[*] Setting execution permission for the auditor script."
    chmod +x shadow_ipv6_auditor.py
    
    echo "You can now run the auditor script using 'sudo' permissions:"
    echo "sudo python3 shadow_ipv6_auditor.py <interface> <ipv4_address>"
else
    echo "[ERROR] Scapy installation failed. Check the errors above."
fi