#!/usr/bin/env python3
"""
Byzantine IDS Attack Simulator
Generates guaranteed malicious traffic for Suricata detection
Perfect for demos and testing
"""

import socket
import random
import time
import sys
from datetime import datetime

class AttackSimulator:
    """Generate various attack patterns that Suricata will detect"""
    
    def __init__(self, target_ip, target_port=80):
        self.target_ip = target_ip
        self.target_port = target_port
        self.attacks_run = 0
        
    def print_banner(self):
        """Print attack simulator banner"""
        print("\n" + "="*70)
        print("🎯 BYZANTINE IDS - ATTACK SIMULATOR")
        print("="*70)
        print(f"Target IP: {self.target_ip}")
        print(f"Target Port: {self.target_port}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def attack_1_port_scan_simulation(self):
        """Simulate port scanning (triggers ET SCAN signatures)"""
        print("\n🔍 ATTACK 1: Port Scan Simulation")
        print("-" * 50)
        
        ports = [21, 22, 23, 25, 80, 443, 3306, 8080, 8443, 3389]
        
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((self.target_ip, port))
                sock.close()
                print(f"  → Probing port {port}")
            except:
                pass
            time.sleep(0.1)
        
        print("✅ Port scan simulation complete")
        print("   Expected: ET SCAN Nmap TCP / ET SCAN Port Sweep")
        self.attacks_run += 1
    
    def attack_2_syn_flood_simulation(self):
        """Simulate SYN flood (triggers ET DOS signatures)"""
        print("\n💥 ATTACK 2: SYN Flood Simulation (Controlled)")
        print("-" * 50)
        
        print("  → Sending rapid connection attempts...")
        
        for i in range(50):  # Limited to 50 for safety
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect((self.target_ip, self.target_port))
                sock.close()
            except:
                pass
        
        print("✅ SYN flood simulation complete")
        print("   Expected: ET DOS Possible SYN Flood")
        self.attacks_run += 1
    
    def attack_3_malicious_http_requests(self):
        """Send HTTP requests with malicious payloads"""
        print("\n🌐 ATTACK 3: Malicious HTTP Requests")
        print("-" * 50)
        
        payloads = [
            "GET /?id=1' OR '1'='1 HTTP/1.1\r\nHost: {}\r\n\r\n",  # SQL injection
            "GET /?search=<script>alert(1)</script> HTTP/1.1\r\nHost: {}\r\n\r\n",  # XSS
            "GET /../../../../etc/passwd HTTP/1.1\r\nHost: {}\r\n\r\n",  # Path traversal
            "GET / HTTP/1.1\r\nUser-Agent: Nmap Scripting Engine\r\nHost: {}\r\n\r\n",  # Nmap UA
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_ip, self.target_port))
                sock.send(payload.format(self.target_ip).encode())
                sock.close()
                print(f"  → Sent malicious HTTP request {i}")
                time.sleep(0.5)
            except Exception as e:
                print(f"  → HTTP request {i} (connection refused - normal)")
        
        print("✅ Malicious HTTP requests complete")
        print("   Expected: ET WEB SQL Injection / ET WEB XSS / ET SCAN Nmap")
        self.attacks_run += 1
    
    def attack_4_ssh_brute_force_simulation(self):
        """Simulate SSH brute force attempts"""
        print("\n🔐 ATTACK 4: SSH Brute Force Simulation")
        print("-" * 50)
        
        print("  → Attempting rapid SSH connections...")
        
        for i in range(10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.target_ip, 22))
                # Send SSH banner
                sock.send(b"SSH-2.0-OpenSSH_7.4\r\n")
                sock.close()
                print(f"  → SSH attempt {i+1}/10")
                time.sleep(0.3)
            except:
                pass
        
        print("✅ SSH brute force simulation complete")
        print("   Expected: ET SCAN SSH / ET POLICY SSH")
        self.attacks_run += 1
    
    def attack_5_suspicious_dns_queries(self):
        """Generate suspicious DNS-like traffic"""
        print("\n📡 ATTACK 5: Suspicious Network Traffic")
        print("-" * 50)
        
        print("  → Generating suspicious traffic patterns...")
        
        # Multiple rapid connections to different ports
        suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999]
        
        for port in suspicious_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((self.target_ip, port))
                sock.close()
            except:
                pass
            time.sleep(0.2)
        
        print("✅ Suspicious traffic generation complete")
        print("   Expected: ET POLICY Suspicious Port / ET SCAN")
        self.attacks_run += 1
    
    def attack_6_malformed_packets(self):
        """Send malformed packets"""
        print("\n⚠️  ATTACK 6: Malformed Packet Generation")
        print("-" * 50)
        
        print("  → Sending packets with unusual characteristics...")
        
        # Send packets with weird flags/data
        for i in range(5):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((self.target_ip, self.target_port))
                # Send garbage data
                sock.send(b"\x00" * 100 + b"MALFORMED" * 10)
                sock.close()
                time.sleep(0.2)
            except:
                pass
        
        print("✅ Malformed packet generation complete")
        print("   Expected: SURICATA STREAM / Protocol anomalies")
        self.attacks_run += 1
    
    def run_all_attacks(self):
        """Execute all attack simulations"""
        self.print_banner()
        
        print("🚀 Starting comprehensive attack simulation...")
        print("⏱️  This will take approximately 1-2 minutes\n")
        
        time.sleep(2)
        
        try:
            self.attack_1_port_scan_simulation()
            time.sleep(2)
            
            self.attack_2_syn_flood_simulation()
            time.sleep(2)
            
            self.attack_3_malicious_http_requests()
            time.sleep(2)
            
            self.attack_4_ssh_brute_force_simulation()
            time.sleep(2)
            
            self.attack_5_suspicious_dns_queries()
            time.sleep(2)
            
            self.attack_6_malformed_packets()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Attack simulation interrupted by user")
            sys.exit(1)
        
        # Final summary
        print("\n" + "="*70)
        print("✅ ATTACK SIMULATION COMPLETE")
        print("="*70)
        print(f"Total attacks executed: {self.attacks_run}")
        print(f"Target: {self.target_ip}")
        print(f"Time completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Check your Suricata detector for alerts!")
        print("   Expected categories: SCAN, DOS, WEB, POLICY")
        print("   Expected severity: MEDIUM to CRITICAL")
        print("="*70 + "\n")

def main():
    """Main entry point"""
    
    if len(sys.argv) != 2:
        print("\n❌ Usage: python3 attack_simulator.py <TARGET_IP>")
        print("\nExample:")
        print("  python3 attack_simulator.py 192.168.1.237")
        print("\nThis will simulate 6 different attack types against the target.")
        print("Make sure Suricata is running on the target before starting!\n")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    
    # Validate IP format (basic check)
    parts = target_ip.split('.')
    if len(parts) != 4:
        print("❌ Invalid IP address format")
        sys.exit(1)
    
    print("\n⚠️  WARNING: This script generates malicious network traffic!")
    print("Only use against systems you own or have permission to test.")
    print("\nTarget:", target_ip)
    response = input("\nProceed with attack simulation? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Attack simulation cancelled")
        sys.exit(0)
    
    # Create simulator and run
    simulator = AttackSimulator(target_ip)
    simulator.run_all_attacks()

if __name__ == "__main__":
    main()
