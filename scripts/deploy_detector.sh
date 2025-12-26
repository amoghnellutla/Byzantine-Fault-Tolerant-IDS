#!/bin/bash
# Byzantine IDS - Suricata Detector Deployment Script
# This script automates the deployment on each detector node

echo "=============================================="
echo "Byzantine IDS - Suricata Detector Deployment"
echo "=============================================="
echo ""

# Configuration
read -p "Enter Detector ID (rp6, rp7, or rp8): " DETECTOR_ID
read -p "Enter Coordinator IP address: " COORDINATOR_IP
read -p "Enter Coordinator Port [5000]: " COORDINATOR_PORT
COORDINATOR_PORT=${COORDINATOR_PORT:-5000}

echo ""
echo "Configuration:"
echo "  Detector ID: $DETECTOR_ID"
echo "  Coordinator: $COORDINATOR_IP:$COORDINATOR_PORT"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "Step 1: Checking prerequisites..."

# Check if Suricata is installed
if ! command -v suricata &> /dev/null; then
    echo "ERROR: Suricata is not installed!"
    echo "Please install Suricata 7.0.1 first."
    exit 1
fi

# Check Suricata version
SURICATA_VERSION=$(suricata --version | grep "Suricata version" | awk '{print $3}')
echo "  ✓ Suricata version: $SURICATA_VERSION"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    exit 1
fi
echo "  ✓ Python 3 installed"

# Check if log directories exist
if [ ! -d "/usr/local/var/log/suricata" ]; then
    echo "ERROR: Suricata log directory not found!"
    exit 1
fi
echo "  ✓ Suricata log directory exists"

echo ""
echo "Step 2: Updating detector configuration..."

# Update detector configuration
sed -i "s/DETECTOR_ID = \".*\"/DETECTOR_ID = \"$DETECTOR_ID\"/" suricata_detector.py
sed -i "s/COORDINATOR_HOST = \".*\"/COORDINATOR_HOST = \"$COORDINATOR_IP\"/" suricata_detector.py
sed -i "s/COORDINATOR_PORT = .*/COORDINATOR_PORT = $COORDINATOR_PORT/" suricata_detector.py

echo "  ✓ Configuration updated"

echo ""
echo "Step 3: Creating systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/byzantine-detector.service > /dev/null <<EOF
[Unit]
Description=Byzantine IDS Suricata Detector
After=network.target suricata.service
Requires=suricata.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/suricata_detector.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "  ✓ Systemd service created"

echo ""
echo "Step 4: Enabling and starting service..."

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable byzantine-detector.service

# Start service
sudo systemctl start byzantine-detector.service

echo "  ✓ Service started"

echo ""
echo "Step 5: Verifying installation..."

# Wait a moment for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet byzantine-detector.service; then
    echo "  ✓ Byzantine detector service is running"
else
    echo "  ✗ Service failed to start!"
    echo ""
    echo "View logs with: sudo journalctl -u byzantine-detector.service -f"
    exit 1
fi

echo ""
echo "=============================================="
echo "Deployment Complete!"
echo "=============================================="
echo ""
echo "Service Management Commands:"
echo "  View logs:    sudo journalctl -u byzantine-detector.service -f"
echo "  Stop service: sudo systemctl stop byzantine-detector.service"
echo "  Restart:      sudo systemctl restart byzantine-detector.service"
echo "  Status:       sudo systemctl status byzantine-detector.service"
echo ""
echo "Suricata Commands:"
echo "  Start:        sudo systemctl start suricata"
echo "  Stop:         sudo systemctl stop suricata"
echo "  Status:       sudo systemctl status suricata"
echo ""
echo "View real-time alerts with:"
echo "  sudo tail -f /usr/local/var/log/suricata/fast.log"
echo ""
echo "View dashboard:"
echo "  python3 alert_dashboard.py"
echo ""
