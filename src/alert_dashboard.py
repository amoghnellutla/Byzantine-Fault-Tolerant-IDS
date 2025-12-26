#!/usr/bin/env python3
"""
Suricata Alert Dashboard - Presentation Ready
Beautiful, organized visualization of security alerts
Author: Research Project - MSU
"""

import json
import time
from datetime import datetime
from collections import defaultdict, Counter
import os
import sys

# Suricata paths
SURICATA_FAST_LOG = "/usr/local/var/log/suricata/fast.log"
SURICATA_EVE_JSON = "/usr/local/var/log/suricata/eve.json"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Emoji indicators
SEVERITY_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🔵",
    "INFO": "⚪"
}

CATEGORY_EMOJI = {
    "SCAN": "🔍",
    "DOS": "💥",
    "EXPLOIT": "⚔️",
    "MALWARE": "🦠",
    "POLICY": "⚠️",
    "CNC": "🎮",
    "WEB": "🌐",
    "OTHER": "❓"
}


class AlertDashboard:
    """Real-time alert dashboard with presentation-quality formatting"""
    
    def __init__(self):
        self.alerts = []
        self.stats = {
            'total': 0,
            'by_severity': defaultdict(int),
            'by_category': defaultdict(int),
            'by_protocol': defaultdict(int),
            'top_signatures': Counter(),
            'top_sources': Counter(),
            'top_destinations': Counter(),
            'timeline': []
        }
        self.start_time = time.time()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print dashboard header"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*100}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'BYZANTINE IDS - SURICATA ALERT DASHBOARD':^100}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'Real-Time Security Monitoring':^100}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*100}{Colors.ENDC}\n")
        
        # Runtime info
        uptime = int(time.time() - self.start_time)
        uptime_str = f"{uptime//3600}h {(uptime%3600)//60}m {uptime%60}s"
        print(f"{Colors.OKCYAN}Dashboard Uptime: {uptime_str}  |  ", end='')
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
    
    def print_summary_stats(self):
        """Print high-level summary statistics"""
        print(f"{Colors.BOLD}{Colors.OKBLUE}{'SUMMARY STATISTICS':^100}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'─'*100}{Colors.ENDC}\n")
        
        # Total alerts
        print(f"{'Total Alerts Detected:':<40} {Colors.BOLD}{self.stats['total']:>10,}{Colors.ENDC}")
        print()
    
    def print_severity_breakdown(self):
        """Print alerts by severity level"""
        print(f"{Colors.BOLD}{Colors.WARNING}{'ALERTS BY SEVERITY LEVEL':^100}{Colors.ENDC}")
        print(f"{Colors.WARNING}{'─'*100}{Colors.ENDC}\n")
        
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
        
        for severity in severity_order:
            count = self.stats['by_severity'][severity]
            if count > 0:
                emoji = SEVERITY_EMOJI[severity]
                percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
                bar_length = int(percentage / 2)  # Scale to 50 chars max
                bar = '█' * bar_length
                
                print(f"{emoji} {severity:<12} │ {count:>6,} alerts │ {percentage:>5.1f}% │ {bar}")
        
        print()
    
    def print_category_breakdown(self):
        """Print alerts by attack category"""
        print(f"{Colors.BOLD}{Colors.FAIL}{'ALERTS BY ATTACK CATEGORY':^100}{Colors.ENDC}")
        print(f"{Colors.FAIL}{'─'*100}{Colors.ENDC}\n")
        
        # Sort by count
        sorted_categories = sorted(self.stats['by_category'].items(), 
                                   key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories[:10]:  # Top 10
            emoji = CATEGORY_EMOJI.get(category, "❓")
            percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            
            print(f"{emoji} {category:<12} │ {count:>6,} alerts │ {percentage:>5.1f}% │ {bar}")
        
        print()
    
    def print_top_signatures(self):
        """Print most frequent attack signatures"""
        print(f"{Colors.BOLD}{Colors.OKCYAN}{'TOP 10 ATTACK SIGNATURES':^100}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'─'*100}{Colors.ENDC}\n")
        
        for i, (signature, count) in enumerate(self.stats['top_signatures'].most_common(10), 1):
            # Truncate long signatures
            sig_display = signature[:80] + "..." if len(signature) > 80 else signature
            print(f"{i:>2}. [{count:>5,} alerts] {sig_display}")
        
        print()
    
    def print_network_stats(self):
        """Print network-related statistics"""
        print(f"{Colors.BOLD}{Colors.OKGREEN}{'NETWORK STATISTICS':^100}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{'─'*100}{Colors.ENDC}\n")
        
        # Top source IPs
        print(f"{'Top Source IPs (Attackers):':<50}")
        for i, (ip, count) in enumerate(self.stats['top_sources'].most_common(5), 1):
            print(f"  {i}. {ip:<20} → {count:>5,} alerts")
        print()
        
        # Top destination IPs
        print(f"{'Top Destination IPs (Targets):':<50}")
        for i, (ip, count) in enumerate(self.stats['top_destinations'].most_common(5), 1):
            print(f"  {i}. {ip:<20} → {count:>5,} alerts")
        print()
        
        # Protocol breakdown
        print(f"{'Protocol Distribution:':<50}")
        for proto, count in sorted(self.stats['by_protocol'].items(), 
                                   key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
            print(f"  {proto:<10} → {count:>6,} alerts ({percentage:>5.1f}%)")
        
        print()
    
    def print_recent_timeline(self):
        """Print recent alert timeline"""
        print(f"{Colors.BOLD}{Colors.HEADER}{'RECENT ALERT TIMELINE (Last 15 alerts)':^100}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'─'*100}{Colors.ENDC}\n")
        
        recent = self.stats['timeline'][-15:]
        
        for alert in recent:
            timestamp = alert['timestamp']
            severity = alert['severity']
            category = alert['category']
            signature = alert['signature'][:60]
            src = f"{alert['src_ip']}:{alert['src_port']}"
            dst = f"{alert['dst_ip']}:{alert['dst_port']}"
            
            emoji_sev = SEVERITY_EMOJI.get(severity, "⚪")
            emoji_cat = CATEGORY_EMOJI.get(category, "❓")
            
            print(f"{timestamp} │ {emoji_sev} {emoji_cat} │ {src:<22} → {dst:<22} │ {signature}")
        
        print()
    
    def update_stats(self, alert):
        """Update statistics with new alert"""
        self.stats['total'] += 1
        self.stats['by_severity'][alert['severity']] += 1
        self.stats['by_category'][alert['category']] += 1
        self.stats['by_protocol'][alert['protocol']] += 1
        self.stats['top_signatures'][alert['signature']] += 1
        self.stats['top_sources'][alert['src_ip']] += 1
        self.stats['top_destinations'][alert['dst_ip']] += 1
        
        # Add to timeline
        self.stats['timeline'].append({
            'timestamp': alert['timestamp'],
            'severity': alert['severity'],
            'category': alert['category'],
            'signature': alert['signature'],
            'src_ip': alert['src_ip'],
            'src_port': alert['src_port'],
            'dst_ip': alert['dst_ip'],
            'dst_port': alert['dst_port']
        })
    
    def render(self):
        """Render the complete dashboard"""
        self.clear_screen()
        self.print_header()
        
        if self.stats['total'] == 0:
            print(f"\n{Colors.WARNING}⏳ Waiting for alerts... Monitoring Suricata logs...{Colors.ENDC}\n")
            print(f"Monitoring:\n")
            print(f"  • {SURICATA_FAST_LOG}")
            print(f"  • {SURICATA_EVE_JSON}\n")
            return
        
        self.print_summary_stats()
        self.print_severity_breakdown()
        self.print_category_breakdown()
        self.print_top_signatures()
        self.print_network_stats()
        self.print_recent_timeline()
        
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*100}{Colors.ENDC}\n")


def load_alerts_from_logs():
    """Load and parse alerts from Suricata logs"""
    # This is a simplified version - integrate with your actual alert parser
    # For demo purposes, this simulates some sample data
    
    alerts = []
    
    # Try to read from eve.json
    try:
        if os.path.exists(SURICATA_EVE_JSON):
            with open(SURICATA_EVE_JSON, 'r') as f:
                # Read last 1000 lines
                lines = f.readlines()[-1000:]
                
                for line in lines:
                    try:
                        data = json.loads(line)
                        if data.get('event_type') == 'alert':
                            alert_data = data.get('alert', {})
                            alerts.append({
                                'timestamp': data.get('timestamp', ''),
                                'severity': data.get('alert', {}).get('severity', 3),
                                'category': data.get('alert', {}).get('category', 'OTHER'),
                                'signature': alert_data.get('signature', 'Unknown'),
                                'protocol': data.get('proto', 'N/A'),
                                'src_ip': data.get('src_ip', '0.0.0.0'),
                                'src_port': data.get('src_port', 0),
                                'dst_ip': data.get('dest_ip', '0.0.0.0'),
                                'dst_port': data.get('dest_port', 0)
                            })
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading logs: {e}")
    
    return alerts


def main():
    """Main dashboard loop"""
    dashboard = AlertDashboard()
    
    print(f"\n{Colors.OKGREEN}Loading Suricata alerts...{Colors.ENDC}\n")
    
    while True:
        try:
            # Load alerts
            alerts = load_alerts_from_logs()
            
            # Update dashboard
            dashboard.stats = {
                'total': 0,
                'by_severity': defaultdict(int),
                'by_category': defaultdict(int),
                'by_protocol': defaultdict(int),
                'top_signatures': Counter(),
                'top_sources': Counter(),
                'top_destinations': Counter(),
                'timeline': []
            }
            
            for alert in alerts:
                dashboard.update_stats(alert)
            
            # Render dashboard
            dashboard.render()
            
            # Refresh every 5 seconds
            time.sleep(5)
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Dashboard stopped.{Colors.ENDC}\n")
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}\n")
            time.sleep(5)


if __name__ == "__main__":
    main()
