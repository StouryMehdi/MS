#!/usr/bin/env python3

import platform
import subprocess
import socket
import re
import json
from datetime import datetime

class CrossPlatformNetworkScanner:
    def __init__(self):
        self.system = platform.system().lower()
        print(f"🔍 Detected OS: {platform.system()} {platform.release()}")
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
            return local_ip
        except:
            return "127.0.0.1"
    
    def get_network_info_linux(self):
        """Get network info for Linux"""
        devices = []
        
        try:
            # Method 1: Using ip command
            result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line and not line.startswith(' '):
                    # New interface
                    match = re.search(r'^\d+:\s+(\w+):', line)
                    if match:
                        current_interface = match.group(1)
                        interfaces.append({'name': current_interface, 'ip': [], 'mac': ''})
                elif current_interface and 'link/ether' in line:
                    # MAC address
                    mac_match = re.search(r'link/ether\s+([0-9a-f:]+)', line, re.IGNORECASE)
                    if mac_match:
                        for interface in interfaces:
                            if interface['name'] == current_interface:
                                interface['mac'] = mac_match.group(1)
                elif current_interface and 'inet ' in line:
                    # IP address
                    ip_match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)/', line)
                    if ip_match:
                        for interface in interfaces:
                            if interface['name'] == current_interface:
                                interface['ip'].append(ip_match.group(1))
            
            return interfaces
            
        except Exception as e:
            print(f"Error getting Linux network info: {e}")
            return []
    
    def get_network_info_windows(self):
        """Get network info for Windows"""
        devices = []
        
        try:
            # Method 1: Using ipconfig
            result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, shell=True)
            
            interfaces = []
            current_interface = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # Interface name
                if line and not line.startswith(' ') and 'adapter' in line.lower():
                    current_interface = line.replace('adapter', '').replace(':', '').strip()
                    interfaces.append({'name': current_interface, 'ip': [], 'mac': ''})
                
                # Physical Address (MAC)
                elif current_interface and 'physical address' in line.lower():
                    mac_match = re.search(r'([0-9A-Fa-f-]{17})', line)
                    if mac_match:
                        for interface in interfaces:
                            if interface['name'] == current_interface:
                                interface['mac'] = mac_match.group(1).replace('-', ':')
                
                # IPv4 Address
                elif current_interface and 'ipv4 address' in line.lower():
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        for interface in interfaces:
                            if interface['name'] == current_interface:
                                interface['ip'].append(ip_match.group(1))
            
            return interfaces
            
        except Exception as e:
            print(f"Error getting Windows network info: {e}")
            return []
    
    def scan_arp_table(self):
        """Scan ARP table for IP-MAC mappings"""
        arp_table = []
        
        try:
            if self.system == "linux":
                # Linux ARP table
                result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if line and 'at' in line:
                        # Parse: hostname (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0
                        ip_match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', line)
                        mac_match = re.search(r'at\s+([0-9a-f:]+)', line, re.IGNORECASE)
                        if ip_match and mac_match:
                            arp_table.append({
                                'ip': ip_match.group(1),
                                'mac': mac_match.group(1),
                                'type': 'LAN Device'
                            })
            
            elif self.system == "windows":
                # Windows ARP table
                result = subprocess.run(["arp", "-a"], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if line and re.match(r'^\d+\.\d+\.\d+\.\d+', line):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0]
                            mac = parts[1]
                            if mac != 'ff-ff-ff-ff-ff-ff' and mac != '00-00-00-00-00-00':
                                arp_table.append({
                                    'ip': ip,
                                    'mac': mac.replace('-', ':'),
                                    'type': 'LAN Device'
                                })
        
        except Exception as e:
            print(f"Error scanning ARP table: {e}")
        
        return arp_table
    
    def get_network_devices(self):
        """Get all network devices with IP and MAC addresses"""
        print("\n🌐 Scanning Network Devices...")
        print("=" * 60)
        
        # Get local network interfaces
        if self.system == "linux":
            interfaces = self.get_network_info_linux()
        else:
            interfaces = self.get_network_info_windows()
        
        # Get ARP table for other devices
        arp_devices = self.scan_arp_table()
        
        # Combine results
        all_devices = []
        
        # Add local interfaces
        for interface in interfaces:
            if interface['ip'] or interface['mac']:
                for ip in interface['ip']:
                    all_devices.append({
                        'ip': ip,
                        'mac': interface['mac'],
                        'name': interface['name'],
                        'type': 'Local Interface'
                    })
        
        # Add ARP table devices (avoid duplicates)
        for arp_device in arp_devices:
            if not any(device['ip'] == arp_device['ip'] for device in all_devices):
                all_devices.append(arp_device)
        
        return all_devices
    
    def display_network_info(self):
        """Display comprehensive network information"""
        print(f"\n🖥️  Cross-Platform Network Scanner")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        local_ip = self.get_local_ip()
        print(f"📍 Local IP Address: {local_ip}")
        print(f"💻 Hostname: {socket.gethostname()}")
        print(f"🖥️  OS: {platform.system()} {platform.release()}")
        print("-" * 70)
        
        # Get network devices
        devices = self.get_network_devices()
        
        if not devices:
            print("❌ No network devices found")
            return
        
        print(f"\n📱 Found {len(devices)} Network Device(s):")
        print("-" * 70)
        print(f"{'IP Address':<20} {'MAC Address':<20} {'Type/Name':<25}")
        print("-" * 70)
        
        for device in devices:
            ip = device.get('ip', 'N/A')
            mac = device.get('mac', 'N/A')
            name_type = device.get('name', device.get('type', 'Unknown'))
            
            print(f"{ip:<20} {mac:<20} {name_type:<25}")
    
    def save_to_file(self, filename=None):
        """Save network scan results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"network_scan_{timestamp}.txt"
        
        devices = self.get_network_devices()
        
        with open(filename, 'w') as f:
            f.write("Network Scan Results\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"OS: {platform.system()} {platform.release()}\n")
            f.write(f"Hostname: {socket.gethostname()}\n")
            f.write(f"Local IP: {self.get_local_ip()}\n\n")
            
            f.write("Network Devices:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'IP Address':<20} {'MAC Address':<20} {'Type/Name':<25}\n")
            f.write("-" * 50 + "\n")
            
            for device in devices:
                ip = device.get('ip', 'N/A')
                mac = device.get('mac', 'N/A')
                name_type = device.get('name', device.get('type', 'Unknown'))
                f.write(f"{ip:<20} {mac:<20} {name_type:<25}\n")
        
        print(f"💾 Results saved to: {filename}")

def main():
    """Main function"""
    scanner = CrossPlatformNetworkScanner()
    
    try:
        while True:
            print("\n" + "=" * 70)
            print("🌐 Cross-Platform Network Scanner")
            print("=" * 70)
            print("1. Scan Network Devices")
            print("2. Save Results to File")
            print("3. Continuous Monitoring")
            print("4. Exit")
            print("-" * 70)
            
            choice = input("Choose option (1-4): ").strip()
            
            if choice == "1":
                scanner.display_network_info()
                input("\nPress Enter to continue...")
            
            elif choice == "2":
                filename = input("Enter filename (or press Enter for auto-name): ").strip()
                if not filename:
                    scanner.save_to_file()
                else:
                    scanner.save_to_file(filename)
                input("\nPress Enter to continue...")
            
            elif choice == "3":
                print("\n🔄 Starting Continuous Monitoring (Ctrl+C to stop)...")
                try:
                    while True:
                        scanner.display_network_info()
                        print("\n⏳ Refreshing in 10 seconds...")
                        import time
                        time.sleep(10)
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped")
            
            elif choice == "4":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    except KeyboardInterrupt:
        print("\n👋 Program terminated by user")

if __name__ == "__main__":
    main()