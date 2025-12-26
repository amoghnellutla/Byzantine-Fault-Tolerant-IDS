#!/usr/bin/env python3
"""
Byzantine Fault-Tolerant IDS - Honest Detector Node
Monitors Suricata alerts and casts honest votes to coordinator
"""

import os
import time
import re
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

# Configuration
FAST_LOG = "/usr/local/var/log/suricata/fast.log"
COORD_URL = "http://192.168.1.236:5000/alert"
NODE_ID = "rp6"  # Change to "rp8" for other honest nodes
LAST_ALERT = {}
DEDUP_SECONDS = 3

def send_vote(msg):
    """Send vote to Byzantine coordinator"""
    try:
        response = requests.post(
            COORD_URL,
            json={"node": NODE_ID, "message": msg},
            timeout=2
        )
        console.print("[dim green]✓ Vote sent to coordinator[/dim green]")
    except Exception as e:
        console.print(f"[dim red]✗ Failed to send vote: {e}[/dim red]")

def parse_line(line):
    """Extract alert message from Suricata fast.log format"""
    match = re.search(r'\[\*\*\]\s+\[[^\]]+\]\s+(.*?)\s+\[\*\*\]', line)
    return match.group(1).strip() if match else "Unknown"

# Startup
console.print(f"[bold green]{NODE_ID} Detector Started[/bold green]")
console.print(f"[dim]Sending votes to: {COORD_URL}[/dim]\n")

if not os.path.exists(FAST_LOG):
    console.print(f"[red]ERROR: {FAST_LOG} not found![/red]")
    exit(1)

# Main detection loop
with open(FAST_LOG, 'r') as f:
    f.seek(0, os.SEEK_END)  # Start at end of file
    
    while True:
        line = f.readline()
        
        if not line:
            time.sleep(0.2)
            continue
        
        if "CUSTOM ATTACK" in line:
            msg = parse_line(line)
            
            # Deduplication check
            now = time.time()
            if msg in LAST_ALERT and (now - LAST_ALERT[msg] < DEDUP_SECONDS):
                continue
            LAST_ALERT[msg] = now
            
            # Display locally
            console.print(Panel(
                msg,
                title=f"[bold cyan]{NODE_ID} ALERT[/bold cyan]",
                border_style="cyan"
            ))
            
            # Send vote to coordinator
            send_vote(msg)
            console.print()
