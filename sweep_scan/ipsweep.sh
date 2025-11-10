#!/bin/bash

# --- STEP 1: IP Sweep (from your previous script) ---

if [ "$1" == "" ]; then
    echo "You forgot an IP address prefix!"
    echo "Syntax: ./scan_and_map.sh 192.168.1"
    exit 1
fi

echo "--- 🔍 STEP 1: Starting IP Sweep on $1.1-254 ---"
# Run the sweep and save the found IP addresses to iplist.txt
for ip in $(seq 1 254); do
    ping -c 1 $1.$ip | grep "64 bytes" | cut -d " " -f 4 | tr -d ":"
done > iplist.txt
echo "--- ✅ Found IPs saved to iplist.txt ---"

echo ""

# --- STEP 2: Nmap Port Scan (your new command) ---

if [ ! -s iplist.txt ]; then
    echo "--- ❌ STEP 2: iplist.txt is empty. No hosts found to scan. ---"
    exit 1
fi

echo "--- 🔎 STEP 2: Starting Nmap scan for port 80 on listed hosts ---"
echo "--- Results will be displayed as they complete. ---"

# Loop through each IP in the file and run an Nmap scan
for ip in $(cat iplist.txt); do 
    nmap -p 80 -T4 $ip & 
done

# Wait for all background Nmap processes to finish before exiting the script
wait

echo "--- ✅ Nmap scanning complete. ---"