#!/usr/bin/env python3
"""
Byzantine Fault-Tolerant IDS - Byzantine (Faulty) Detector Node
Simulates compromised detector that lies 30% of the time
"""

import socket
import time
import re
import requests
import random
from rich.console import Console
from rich.panel import Panel

console = Console()

# Configuration
COORD_URL = "http://192.168.1.236:5000/alert"
NODE_ID = "rp8-virtual"
LAST_ALERT = {}
DEDUP_SECONDS = 3
PORT = 9998  # Listen on different port than physical rp8
LIE_PROBABILITY = 0.30  # 30% chance of lying

def send_vote(msg):
    """Send vote to Byzantine coordinator"""
    try:
        requests.post(
            COORD_URL,
            json={"node": NODE_ID, "message": msg},
            timeout=2
        )
        console.print("[green]✓ Vote sent to coordinator[/green]")
    except:
        console.print("[red]✗ FAILED to send vote[/red]")

def parse_line(line):
    """Extract alert message from Suricata fast.log format"""
    match = re.search(r'\[\*\*\]\s+\[[^\]]+\]\s+(.*?)\s+\[\*\*\]', line)
    return match.group(1).strip() if match else "Unknown"

# Startup
console.print(f"[bold red]{NODE_ID} Started (Byzantine Mode)[/bold red]")
console.print(f"[bold red]This node will lie {int(LIE_PROBABILITY*100)}% of the time[/bold red]\n")

# UDP socket for receiving forwarded logs
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

# Main Byzantine loop
while True:
    data, addr = sock.recvfrom(4096)
    line = data.decode("utf-8").strip()
    
    if "CUSTOM ATTACK" not in line:
        continue
    
    msg = parse_line(line)
    
    # Deduplication check
    now = time.time()
    if msg in LAST_ALERT and now - LAST_ALERT[msg] < DEDUP_SECONDS:
        continue
    LAST_ALERT[msg] = now
    
    # Byzantine decision: Lie or be honest?
    if random.random() < LIE_PROBABILITY:
        # BYZANTINE BEHAVIOR: Lie about the alert
        fake = "FAKE_" + msg
        console.print(Panel(
            f"[red]Lying![/red]\nReal={msg}\nFake={fake}",
            title=f"{NODE_ID} (Byzantine)",
            border_style="red",
        ))
        send_vote(fake)
        console.print()
    else:
        # HONEST BEHAVIOR: Report accurate alert
        console.print(Panel(
            msg,
            title=f"{NODE_ID} ALERT",
            border_style="cyan",
        ))
        send_vote(msg)
        console.print()
