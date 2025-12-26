#!/usr/bin/env python3
"""
Byzantine Fault-Tolerant IDS Detector with Suricata Integration
Enhanced version with dual log monitoring (fast.log + eve.json)
Author: Research Project - MSU
"""

import json
import time
import socket
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

# Configuration
COORDINATOR_HOST = "192.168.1.100"  # Update with your coordinator IP
COORDINATOR_PORT = 5000
DETECTOR_ID = "rp6"  # Change per node: rp6, rp7, rp8

# Suricata paths
SURICATA_FAST_LOG = "/usr/local/var/log/suricata/fast.log"
SURICATA_EVE_JSON = "/usr/local/var/log/suricata/eve.json"

# Alert severity mapping
SEVERITY_MAP = {
    1: "CRITICAL",
    2: "HIGH", 
    3: "MEDIUM",
    4: "LOW",
    5: "INFO"
}

# Attack category classification
ATTACK_CATEGORIES = {
    "SCAN": ["nmap", "scan", "probe", "reconnaissance"],
    "DOS": ["dos", "flood", "ddos", "amplification"],
    "EXPLOIT": ["exploit", "overflow", "injection", "shellcode"],
    "MALWARE": ["malware", "trojan", "backdoor", "ransomware", "virus"],
    "POLICY": ["policy", "suspicious", "anomaly"],
    "CNC": ["cnc", "c2", "command", "botnet"],
    "WEB": ["sql", "xss", "web", "http"]
}


class AlertAggregator:
    """Aggregates and formats alerts for presentation"""
    
    def __init__(self):
        self.alerts = []
        self.stats = defaultdict(int)
        self.attack_timeline = []
        
    def add_alert(self, alert_data):
        """Add alert and update statistics"""
        self.alerts.append(alert_data)
        
        # Update statistics
        self.stats['total'] += 1
        self.stats[alert_data['severity']] += 1
        self.stats[alert_data['category']] += 1
        
        # Timeline entry
        self.attack_timeline.append({
            'timestamp': alert_data['timestamp'],
            'category': alert_data['category'],
            'signature': alert_data['signature'][:50]
        })
        
    def get_summary(self):
        """Get formatted summary for presentation"""
        return {
            'total_alerts': self.stats['total'],
            'by_severity': {k: self.stats[k] for k in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] if self.stats[k] > 0},
            'by_category': {k: self.stats[k] for k in ATTACK_CATEGORIES.keys() if self.stats[k] > 0},
            'recent_timeline': self.attack_timeline[-10:]
        }


class SuricataAlertParser:
    """Parse both fast.log and eve.json formats"""
    
    @staticmethod
    def parse_fast_log(line):
        """
        Parse fast.log format:
        MM/DD/YYYY-HH:MM:SS.mmmmmm  [**] [gid:sid:rev] signature [**] [Classification: type] [Priority: N] {proto} src:port -> dst:port
        """
        try:
            # Extract timestamp
            ts_match = re.match(r'(\d{2}/\d{2}/\d{4}-\d{2}:\d{2}:\d{2}\.\d+)', line)
            if not ts_match:
                return None
            timestamp = ts_match.group(1)
            
            # Extract signature
            sig_match = re.search(r'\[\*\*\] \[(\d+):(\d+):(\d+)\] (.*?) \[\*\*\]', line)
            if not sig_match:
                return None
            gid, sid, rev, signature = sig_match.groups()
            
            # Extract classification
            class_match = re.search(r'\[Classification: (.*?)\]', line)
            classification = class_match.group(1) if class_match else "Unknown"
            
            # Extract priority
            prio_match = re.search(r'\[Priority: (\d+)\]', line)
            priority = int(prio_match.group(1)) if prio_match else 5
            
            # Extract network info
            net_match = re.search(r'{(.*?)} ([\d\.]+):(\d+) -> ([\d\.]+):(\d+)', line)
            if net_match:
                proto, src_ip, src_port, dst_ip, dst_port = net_match.groups()
            else:
                proto = src_ip = src_port = dst_ip = dst_port = "N/A"
            
            return {
                'timestamp': timestamp,
                'signature': signature,
                'gid': gid,
                'sid': sid,
                'rev': rev,
                'classification': classification,
                'priority': priority,
                'severity': SEVERITY_MAP.get(priority, "INFO"),
                'protocol': proto,
                'src_ip': src_ip,
                'src_port': src_port,
                'dst_ip': dst_ip,
                'dst_port': dst_port,
                'source': 'fast.log'
            }
        except Exception as e:
            print(f"[ERROR] Failed to parse fast.log line: {e}")
            return None
    
    @staticmethod
    def parse_eve_json(line):
        """
        Parse eve.json format (full JSON with all metadata)
        """
        try:
            data = json.loads(line)
            
            # Only process alert events
            if data.get('event_type') != 'alert':
                return None
            
            alert = data.get('alert', {})
            
            return {
                'timestamp': data.get('timestamp', ''),
                'signature': alert.get('signature', 'Unknown'),
                'gid': alert.get('gid', 0),
                'sid': alert.get('signature_id', 0),
                'rev': alert.get('rev', 0),
                'classification': alert.get('category', 'Unknown'),
                'priority': alert.get('severity', 5),
                'severity': SEVERITY_MAP.get(alert.get('severity', 5), "INFO"),
                'protocol': data.get('proto', 'N/A'),
                'src_ip': data.get('src_ip', 'N/A'),
                'src_port': data.get('src_port', 'N/A'),
                'dst_ip': data.get('dest_ip', 'N/A'),
                'dst_port': data.get('dest_port', 'N/A'),
                'flow_id': data.get('flow_id', 'N/A'),
                'payload': data.get('payload', ''),
                'packet_info': data.get('packet_info', {}),
                'http': data.get('http', {}),
                'dns': data.get('dns', {}),
                'tls': data.get('tls', {}),
                'source': 'eve.json'
            }
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"[ERROR] Failed to parse eve.json line: {e}")
            return None
    
    @staticmethod
    def categorize_attack(signature, classification):
        """Determine attack category from signature and classification"""
        text = (signature + " " + classification).lower()
        
        for category, keywords in ATTACK_CATEGORIES.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "OTHER"


class SuricataMonitor:
    """Monitor Suricata logs and send alerts to Byzantine coordinator"""
    
    def __init__(self, detector_id):
        self.detector_id = detector_id
        self.parser = SuricataAlertParser()
        self.aggregator = AlertAggregator()
        self.running = False
        self.processed_alerts = set()  # Avoid duplicates
        
    def tail_file(self, filepath):
        """Tail a file and yield new lines (like tail -f)"""
        try:
            with open(filepath, 'r') as f:
                # Start from end of file
                f.seek(0, 2)
                
                while self.running:
                    line = f.readline()
                    if line:
                        yield line.strip()
                    else:
                        time.sleep(0.1)
        except FileNotFoundError:
            print(f"[WARNING] Log file not found: {filepath}")
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Error reading {filepath}: {e}")
            time.sleep(5)
    
    def monitor_fast_log(self):
        """Monitor fast.log for alerts"""
        print(f"[{self.detector_id}] Starting fast.log monitor...")
        
        for line in self.tail_file(SURICATA_FAST_LOG):
            if not line or line.startswith('#'):
                continue
            
            alert = self.parser.parse_fast_log(line)
            if alert:
                self.process_alert(alert)
    
    def monitor_eve_json(self):
        """Monitor eve.json for alerts"""
        print(f"[{self.detector_id}] Starting eve.json monitor...")
        
        for line in self.tail_file(SURICATA_EVE_JSON):
            if not line:
                continue
            
            alert = self.parser.parse_eve_json(line)
            if alert:
                self.process_alert(alert)
    
    def process_alert(self, alert):
        """Process and forward alert to coordinator"""
        if not alert:
            return
        
        # Create unique alert ID to avoid duplicates
        alert_id = hashlib.md5(
            f"{alert['timestamp']}{alert['sid']}{alert['src_ip']}{alert['dst_ip']}".encode()
        ).hexdigest()
        
        if alert_id in self.processed_alerts:
            return
        
        self.processed_alerts.add(alert_id)
        
        # Add category
        alert['category'] = self.parser.categorize_attack(
            alert['signature'], 
            alert['classification']
        )
        
        # Add to aggregator for statistics
        self.aggregator.add_alert(alert)
        
        # Format for presentation
        self.display_alert(alert)
        
        # Send to Byzantine coordinator
        self.send_to_coordinator(alert)
    
    def display_alert(self, alert):
        """Display alert in organized, presentation-ready format"""
        print("\n" + "="*80)
        print(f"🚨 SECURITY ALERT - {alert['severity']}")
        print("="*80)
        print(f"Detector Node    : {self.detector_id}")
        print(f"Timestamp        : {alert['timestamp']}")
        print(f"Category         : {alert['category']}")
        print(f"Signature        : {alert['signature']}")
        print(f"Classification   : {alert['classification']}")
        print(f"Severity Level   : {alert['severity']} (Priority {alert['priority']})")
        print(f"Rule ID          : {alert['gid']}:{alert['sid']}:{alert['rev']}")
        print("-"*80)
        print(f"Protocol         : {alert['protocol']}")
        print(f"Source           : {alert['src_ip']}:{alert['src_port']}")
        print(f"Destination      : {alert['dst_ip']}:{alert['dst_port']}")
        print(f"Data Source      : {alert['source']}")
        
        # Additional info from eve.json
        if alert.get('flow_id'):
            print(f"Flow ID          : {alert['flow_id']}")
        if alert.get('http'):
            print(f"HTTP Info        : {alert['http']}")
        if alert.get('dns'):
            print(f"DNS Info         : {alert['dns']}")
        
        print("="*80 + "\n")
    
    def send_to_coordinator(self, alert):
        """Send alert to Byzantine coordinator for consensus voting"""
        try:
            # Prepare Byzantine alert message
            message = {
                'type': 'SECURITY_ALERT',
                'detector_id': self.detector_id,
                'alert': alert,
                'timestamp': time.time()
            }
            
            # Send to coordinator
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((COORDINATOR_HOST, COORDINATOR_PORT))
            sock.sendall(json.dumps(message).encode() + b'\n')
            
            # Receive response
            response = sock.recv(4096).decode()
            print(f"[{self.detector_id}] Coordinator response: {response}")
            
            sock.close()
            
        except Exception as e:
            print(f"[{self.detector_id}] Failed to send to coordinator: {e}")
    
    def print_statistics(self):
        """Print statistics periodically"""
        while self.running:
            time.sleep(60)  # Print every 60 seconds
            
            summary = self.aggregator.get_summary()
            
            print("\n" + "="*80)
            print(f"📊 STATISTICS - Detector {self.detector_id}")
            print("="*80)
            print(f"Total Alerts     : {summary['total_alerts']}")
            print(f"By Severity      : {summary['by_severity']}")
            print(f"By Category      : {summary['by_category']}")
            print("="*80 + "\n")
    
    def start(self):
        """Start monitoring both log files"""
        self.running = True
        
        # Start fast.log monitor thread
        fast_thread = threading.Thread(target=self.monitor_fast_log, daemon=True)
        fast_thread.start()
        
        # Start eve.json monitor thread
        eve_thread = threading.Thread(target=self.monitor_eve_json, daemon=True)
        eve_thread.start()
        
        # Start statistics thread
        stats_thread = threading.Thread(target=self.print_statistics, daemon=True)
        stats_thread.start()
        
        print(f"[{self.detector_id}] Suricata Byzantine detector started")
        print(f"[{self.detector_id}] Monitoring: {SURICATA_FAST_LOG}")
        print(f"[{self.detector_id}] Monitoring: {SURICATA_EVE_JSON}")
        print(f"[{self.detector_id}] Coordinator: {COORDINATOR_HOST}:{COORDINATOR_PORT}")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n[{self.detector_id}] Shutting down...")
            self.running = False


def main():
    """Main entry point"""
    print("="*80)
    print("Byzantine Fault-Tolerant IDS with Suricata Integration")
    print("Dual Log Monitoring: fast.log + eve.json")
    print("="*80)
    
    # Create and start monitor
    monitor = SuricataMonitor(DETECTOR_ID)
    monitor.start()


if __name__ == "__main__":
    main()
