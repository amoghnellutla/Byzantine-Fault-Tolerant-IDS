#!/usr/bin/env python3
"""
Byzantine Fault-Tolerant IDS - Coordinator
Aggregates votes from detector nodes and reaches Byzantine consensus
"""

from flask import Flask, request, jsonify
from rich.console import Console
from rich.table import Table
from collections import defaultdict
import time
import threading

app = Flask(__name__)
console = Console()

# Vote storage: {alert_message: {node_id: timestamp}}
votes = defaultdict(dict)
VOTE_WINDOW = 20  # seconds
THRESHOLD = 2     # 2 out of 3 nodes must agree
processed_alerts = set()

def check_consensus(alert_key):
    """Check if consensus threshold is met for given alert"""
    now = time.time()
    active_votes = {
        node: ts for node, ts in votes[alert_key].items()
        if now - ts <= VOTE_WINDOW
    }
    
    if len(active_votes) >= THRESHOLD:
        return True, list(active_votes.keys())
    return False, []

@app.route('/alert', methods=['POST'])
def receive_alert():
    """Receive and process alert vote from detector node"""
    data = request.json
    node = data.get('node', 'unknown')
    message = data.get('message', 'Unknown')
    
    # Show vote received
    console.print(f"[yellow]Vote received → Node: {node}, Msg: {message}[/yellow]")
    
    # Record vote
    alert_key = message
    votes[alert_key][node] = time.time()
    
    # Check for consensus
    consensus, nodes = check_consensus(alert_key)
    
    if consensus and alert_key not in processed_alerts:
        processed_alerts.add(alert_key)
        
        # Display consensus table
        table = Table(
            title="\n[bold green]✓ CONSENSUS REACHED[/bold green]",
            show_header=True,
            header_style="bold white on blue",
            border_style="green"
        )
        
        table.add_column("ATTACK DETECTED", style="bold cyan", width=45)
        table.add_column("NODES VOTING", style="bold yellow", width=25, justify="center")
        table.add_column("VOTE", style="bold green", width=8, justify="center")
        
        nodes_str = ", ".join(sorted(nodes))
        table.add_row(message, nodes_str, f"{len(nodes)}/{THRESHOLD}")
        
        console.print(table)
        console.print()
        
        # Clear votes for this alert
        votes.pop(alert_key, None)
    
    return jsonify({"status": "ok", "consensus": consensus})

def cleanup_processed():
    """Background thread to clear processed alerts periodically"""
    while True:
        time.sleep(10)
        processed_alerts.clear()

if __name__ == '__main__':
    console.print("\n[bold cyan]═" * 35)
    console.print("[bold magenta]   BYZANTINE FAULT-TOLERANT IDS   ")
    console.print("[bold cyan]═" * 35)
    console.print(f"[yellow]Threshold:[/yellow] {THRESHOLD}/3 nodes must agree")
    console.print(f"[yellow]Status:[/yellow] Waiting for alerts...\n")
    
    # Start cleanup thread
    threading.Thread(target=cleanup_processed, daemon=True).start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
