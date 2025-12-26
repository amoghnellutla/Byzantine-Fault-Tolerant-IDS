#!/usr/bin/env python3
"""
Byzantine IDS - Integration Validation Script
Tests all components of the Suricata-Byzantine integration
"""

import os
import sys
import json
import socket
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")

def print_test(test_name):
    print(f"{Colors.BOLD}Testing: {test_name}{Colors.ENDC}")

def print_success(message):
    print(f"  {Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"  {Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"  {Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def test_suricata_installation():
    """Test if Suricata is installed and version is correct"""
    print_test("Suricata Installation")
    
    try:
        result = subprocess.run(['suricata', '--version'], 
                              capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            version = result.stdout.strip()
            if '7.0' in version:
                print_success(f"Suricata 7.0.x detected: {version}")
                return True
            else:
                print_warning(f"Non-optimal version: {version}")
                print_warning("Recommended: Suricata 7.0.1")
                return True
        else:
            print_error("Suricata command failed")
            return False
            
    except FileNotFoundError:
        print_error("Suricata not found in PATH")
        print_error("Install with: sudo apt install suricata")
        return False
    except Exception as e:
        print_error(f"Error checking Suricata: {e}")
        return False

def test_suricata_service():
    """Test if Suricata service is running"""
    print_test("Suricata Service Status")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'suricata'],
                              capture_output=True, text=True)
        
        if result.stdout.strip() == 'active':
            print_success("Suricata service is running")
            return True
        else:
            print_warning("Suricata service is not running")
            print_warning("Start with: sudo systemctl start suricata")
            return False
            
    except Exception as e:
        print_warning(f"Could not check service status: {e}")
        return False

def test_log_files():
    """Test if Suricata log files exist and are accessible"""
    print_test("Suricata Log Files")
    
    log_paths = [
        "/usr/local/var/log/suricata/fast.log",
        "/usr/local/var/log/suricata/eve.json",
        "/var/log/suricata/fast.log",
        "/var/log/suricata/eve.json"
    ]
    
    found = False
    for path in log_paths:
        if os.path.exists(path):
            stat = os.stat(path)
            size = stat.st_size
            print_success(f"Found: {path} ({size} bytes)")
            found = True
    
    if not found:
        print_error("No Suricata log files found")
        print_error("Expected locations:")
        for path in log_paths[:2]:
            print(f"    {path}")
        return False
    
    return True

def test_suricata_rules():
    """Test if rules are loaded"""
    print_test("Suricata Rules")
    
    try:
        result = subprocess.run(['sudo', 'suricata', '-T', 
                               '-c', '/usr/local/etc/suricata/suricata.yaml'],
                              capture_output=True, text=True, timeout=30)
        
        output = result.stdout + result.stderr
        
        if 'successfully loaded' in output.lower():
            print_success("Suricata configuration is valid")
            
            # Try to count rules
            if 'loaded' in output.lower():
                for line in output.split('\n'):
                    if 'rule' in line.lower() and 'loaded' in line.lower():
                        print_success(f"  {line.strip()}")
            
            return True
        else:
            print_error("Configuration test failed")
            print_error("Run manually: sudo suricata -T")
            return False
            
    except Exception as e:
        print_warning(f"Could not test configuration: {e}")
        return False

def test_detector_script():
    """Test if detector script exists and is valid"""
    print_test("Detector Script")
    
    script_paths = [
        "./suricata_detector.py",
        "/home/pi/suricata_detector.py",
        "./byzantine_detector.py"
    ]
    
    found = False
    for path in script_paths:
        if os.path.exists(path):
            print_success(f"Found: {path}")
            
            # Check if it's executable
            if os.access(path, os.X_OK):
                print_success("Script is executable")
            else:
                print_warning("Script is not executable")
                print_warning(f"Run: chmod +x {path}")
            
            # Try to parse it
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    if 'DETECTOR_ID' in content:
                        print_success("Configuration variables found")
                    if 'SuricataMonitor' in content:
                        print_success("Main monitor class found")
                    if 'parse_fast_log' in content:
                        print_success("fast.log parser found")
                    if 'parse_eve_json' in content:
                        print_success("eve.json parser found")
            except Exception as e:
                print_error(f"Could not read script: {e}")
            
            found = True
            break
    
    if not found:
        print_error("Detector script not found")
        print_error("Expected locations:")
        for path in script_paths:
            print(f"    {path}")
        return False
    
    return True

def test_dashboard_script():
    """Test if dashboard script exists"""
    print_test("Dashboard Script")
    
    script_paths = [
        "./alert_dashboard.py",
        "/home/pi/alert_dashboard.py"
    ]
    
    found = False
    for path in script_paths:
        if os.path.exists(path):
            print_success(f"Found: {path}")
            found = True
            break
    
    if not found:
        print_warning("Dashboard script not found (optional)")
    
    return True

def test_python_version():
    """Test Python version"""
    print_test("Python Environment")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version_str} (compatible)")
        return True
    else:
        print_error(f"Python {version_str} (too old)")
        print_error("Requires Python 3.7+")
        return False

def test_network_connectivity():
    """Test network configuration"""
    print_test("Network Connectivity")
    
    # Get hostname
    try:
        hostname = socket.gethostname()
        print_success(f"Hostname: {hostname}")
    except:
        print_warning("Could not determine hostname")
    
    # Get IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        print_success(f"IP Address: {ip}")
    except:
        print_warning("Could not determine IP address")
    
    return True

def test_detector_service():
    """Test if detector service is installed"""
    print_test("Byzantine Detector Service")
    
    try:
        result = subprocess.run(['systemctl', 'is-enabled', 'byzantine-detector'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("Service is installed and enabled")
            
            # Check if running
            result = subprocess.run(['systemctl', 'is-active', 'byzantine-detector'],
                                  capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                print_success("Service is currently running")
            else:
                print_warning("Service is not running")
                print_warning("Start with: sudo systemctl start byzantine-detector")
            
            return True
        else:
            print_warning("Service not installed")
            print_warning("Run deployment script: ./deploy_detector.sh")
            return False
            
    except Exception as e:
        print_warning(f"Could not check service: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results if r['status'])
    total = len(results)
    
    for result in results:
        if result['status']:
            print(f"{Colors.GREEN}✓{Colors.ENDC} {result['name']}")
        else:
            print(f"{Colors.RED}✗{Colors.ENDC} {result['name']}")
    
    print()
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! System is ready.{Colors.ENDC}\n")
        return True
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some tests failed. Review output above.{Colors.ENDC}\n")
        return False

def main():
    """Run all validation tests"""
    print_header("BYZANTINE IDS - INTEGRATION VALIDATION")
    
    tests = [
        ("Python Environment", test_python_version),
        ("Suricata Installation", test_suricata_installation),
        ("Suricata Service", test_suricata_service),
        ("Suricata Log Files", test_log_files),
        ("Suricata Rules", test_suricata_rules),
        ("Detector Script", test_detector_script),
        ("Dashboard Script", test_dashboard_script),
        ("Network Connectivity", test_network_connectivity),
        ("Detector Service", test_detector_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            status = test_func()
            results.append({'name': test_name, 'status': status})
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append({'name': test_name, 'status': False})
        print()
    
    success = print_summary(results)
    
    if success:
        print("Next steps:")
        print("1. Start Suricata: sudo systemctl start suricata")
        print("2. Start detector: sudo systemctl start byzantine-detector")
        print("3. View alerts: sudo tail -f /usr/local/var/log/suricata/fast.log")
        print("4. Launch dashboard: python3 alert_dashboard.py")
        print()
        sys.exit(0)
    else:
        print("Please fix the failed tests before proceeding.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
