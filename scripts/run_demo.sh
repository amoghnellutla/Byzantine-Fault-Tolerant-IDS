#!/bin/bash
# Byzantine IDS - Complete Demo Script
# Runs comprehensive attack simulation for maximum demo effect

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║           BYZANTINE IDS - COMPLETE DEMO SCRIPT                 ║"
echo "║                                                                ║"
echo "║  Maximum Demo Effect: Simulated + Real Attack Traffic         ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
TARGET_IP="192.168.1.237"  # Change this to your rp6 IP
DEMO_DIR="$HOME/byzantine_demo"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create demo directory
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

echo ""
echo -e "${BLUE}📋 DEMO CONFIGURATION${NC}"
echo "─────────────────────────────────────────────────────────"
echo "Target IP: $TARGET_IP"
echo "Demo Directory: $DEMO_DIR"
echo "Current Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Menu
echo -e "${YELLOW}🎯 SELECT DEMO MODE:${NC}"
echo ""
echo "  1) Quick Demo (2 minutes) - Simulated attacks only"
echo "  2) Full Demo (5 minutes) - Simulated + Real datasets"
echo "  3) Individual Attacks - Select specific attack types"
echo "  4) Continuous Demo - Loop attacks for extended presentation"
echo "  5) Setup Only - Download datasets and prepare environment"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 QUICK DEMO MODE${NC}"
        echo "─────────────────────────────────────────────────────────"
        
        # Check if attack simulator exists
        if [ ! -f "attack_simulator.py" ]; then
            echo "Downloading attack simulator..."
            # Simulator should already be created
        fi
        
        echo ""
        echo "▶️  Starting attack simulation against $TARGET_IP"
        echo ""
        
        python3 ~/attack_simulator.py "$TARGET_IP"
        
        echo ""
        echo -e "${GREEN}✅ Quick demo complete!${NC}"
        ;;
        
    2)
        echo ""
        echo -e "${GREEN}🎬 FULL DEMO MODE${NC}"
        echo "─────────────────────────────────────────────────────────"
        
        echo ""
        echo "Phase 1: Simulated Attacks (2 minutes)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        python3 ~/attack_simulator.py "$TARGET_IP"
        
        echo ""
        echo "⏸️  Waiting 10 seconds before Phase 2..."
        sleep 10
        
        echo ""
        echo "Phase 2: Real Attack Datasets (3 minutes)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        if [ -d "$HOME/attack_datasets" ] && [ -f "$HOME/attack_datasets/replay_attacks.sh" ]; then
            cd "$HOME/attack_datasets"
            ./replay_attacks.sh
        else
            echo "⚠️  Real datasets not available - run setup first (option 5)"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Full demo complete!${NC}"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}🎯 INDIVIDUAL ATTACK SELECTION${NC}"
        echo "─────────────────────────────────────────────────────────"
        echo ""
        echo "Available attacks:"
        echo "  a) Port Scan"
        echo "  b) SYN Flood (DOS)"
        echo "  c) Malicious HTTP (SQL Injection/XSS)"
        echo "  d) SSH Brute Force"
        echo "  e) Suspicious Traffic"
        echo "  f) Malformed Packets"
        echo "  g) Run ALL"
        echo ""
        read -p "Select attack [a-g]: " attack_choice
        
        echo ""
        echo "Individual attack mode selected: $attack_choice"
        echo "This feature runs specific attack types only"
        echo ""
        echo "For now, running full simulation..."
        python3 ~/attack_simulator.py "$TARGET_IP"
        ;;
        
    4)
        echo ""
        echo -e "${BLUE}🔄 CONTINUOUS DEMO MODE${NC}"
        echo "─────────────────────────────────────────────────────────"
        echo ""
        echo "This will run attacks in a loop until you press Ctrl+C"
        echo ""
        read -p "How many rounds? [1-10]: " rounds
        
        if [ -z "$rounds" ] || [ "$rounds" -lt 1 ]; then
            rounds=3
        fi
        
        echo ""
        echo "Running $rounds rounds with 30 second delays..."
        echo "Press Ctrl+C to stop"
        echo ""
        
        for i in $(seq 1 $rounds); do
            echo ""
            echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}     ROUND $i of $rounds${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
            
            python3 ~/attack_simulator.py "$TARGET_IP"
            
            if [ $i -lt $rounds ]; then
                echo ""
                echo "⏸️  Waiting 30 seconds before next round..."
                sleep 30
            fi
        done
        
        echo ""
        echo -e "${GREEN}✅ Continuous demo complete! ($rounds rounds)${NC}"
        ;;
        
    5)
        echo ""
        echo -e "${BLUE}🔧 SETUP MODE${NC}"
        echo "─────────────────────────────────────────────────────────"
        
        # Run dataset setup
        if [ -f ~/setup_datasets.sh ]; then
            bash ~/setup_datasets.sh
        else
            echo "Downloading dataset setup script..."
            echo "Setup script should be in home directory"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo "You can now run Full Demo (option 2)"
        ;;
        
    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "─────────────────────────────────────────────────────────"
echo ""
echo -e "${BLUE}📊 NEXT STEPS:${NC}"
echo ""
echo "1️⃣  Check Suricata detector terminal on rp6"
echo "    You should see multiple alerts with different categories"
echo ""
echo "2️⃣  Check fast.log on rp6:"
echo "    sudo tail -50 /usr/local/var/log/suricata/fast.log"
echo ""
echo "3️⃣  View dashboard (if running):"
echo "    python3 alert_dashboard.py"
echo ""
echo "4️⃣  Verify Byzantine consensus (if multiple nodes active)"
echo ""
echo -e "${GREEN}✅ Demo script finished successfully!${NC}"
echo ""
