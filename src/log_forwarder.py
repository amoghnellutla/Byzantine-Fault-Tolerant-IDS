#!/usr/bin/env python3
"""
Byzantine Fault-Tolerant IDS - Log Forwarder
Forwards Suricata logs from rp6 to rp8 detector nodes via UDP
"""

import socket
import time
import os

LOG_FILE = "/usr/local/var/log/suricata/fast.log"
RP8_IP = "192.168.1.239"
PORTS = [9999, 9998]  # Physical and virtual rp8 detectors

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print(f"[LOG FORWARDER] Forwarding {LOG_FILE} to {RP8_IP} ports {PORTS}")

if not os.path.exists(LOG_FILE):
    print(f"[ERROR] {LOG_FILE} not found!")
    exit(1)

# Tail-following behavior
with open(LOG_FILE, 'r') as f:
    f.seek(0, os.SEEK_END)  # Start at end of file
    
    while True:
        line = f.readline()
        
        if line:
            # Forward to both rp8 ports
            for port in PORTS:
                sock.sendto(line.encode('utf-8'), (RP8_IP, port))
        else:
            time.sleep(0.1)  # Brief pause if no new data
