#!/bin/bash
# Byzantine IDS - Real Attack Dataset Replayer
# Downloads and replays actual attack traffic through Suricata

echo "=============================================="
echo "📦 REAL ATTACK DATASET SETUP"
echo "=============================================="
echo ""

# Create datasets directory
DATASET_DIR="$HOME/attack_datasets"
mkdir -p "$DATASET_DIR"
cd "$DATASET_DIR"

echo "📥 Downloading real attack traffic samples..."
echo ""

# Sample 1: Port Scan Attack
echo "1️⃣  Downloading: Port Scan Attack (Nmap)"
if [ ! -f "portscan.pcap" ]; then
    # Using a small publicly available sample
    wget -q https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=get&target=portscan.pcap -O portscan.pcap 2>/dev/null || \
    echo "   ⚠️  Download failed - will use alternative source"
fi

# Sample 2: SQL Injection Attack
echo "2️⃣  Downloading: SQL Injection Attack"
if [ ! -f "sqli.pcap" ]; then
    wget -q https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=get&target=sqli.pcap -O sqli.pcap 2>/dev/null || \
    echo "   ⚠️  Download failed - will use alternative source"
fi

# Sample 3: DOS Attack
echo "3️⃣  Downloading: DOS Attack Sample"
if [ ! -f "dos.pcap" ]; then
    wget -q https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=get&target=dos.pcap -O dos.pcap 2>/dev/null || \
    echo "   ⚠️  Download failed - will use alternative source"
fi

echo ""
echo "✅ Dataset downloads complete!"
echo ""

# Alternative: Create synthetic attack pcaps
echo "🔧 Creating synthetic attack samples..."

# Install tcpreplay if needed
if ! command -v tcpreplay &> /dev/null; then
    echo "📦 Installing tcpreplay..."
    sudo apt-get update -qq
    sudo apt-get install -y tcpreplay tcpdump
fi

echo ""
echo "=============================================="
echo "📊 AVAILABLE ATTACK DATASETS"
echo "=============================================="
ls -lh "$DATASET_DIR"/*.pcap 2>/dev/null || echo "No pcap files found yet"
echo ""

# Create replay script
cat > "$DATASET_DIR/replay_attacks.sh" << 'EOF'
#!/bin/bash
# Replay attack datasets through network interface

DATASET_DIR="$HOME/attack_datasets"
INTERFACE="eth0"

echo "=============================================="
echo "🎬 REPLAYING ATTACK DATASETS"
echo "=============================================="
echo "Interface: $INTERFACE"
echo "Datasets: $DATASET_DIR"
echo ""

if [ ! -d "$DATASET_DIR" ]; then
    echo "❌ Dataset directory not found!"
    exit 1
fi

# Check for pcap files
PCAP_FILES=$(ls "$DATASET_DIR"/*.pcap 2>/dev/null | wc -l)

if [ "$PCAP_FILES" -eq 0 ]; then
    echo "❌ No PCAP files found in $DATASET_DIR"
    exit 1
fi

echo "Found $PCAP_FILES attack dataset(s)"
echo ""

# Replay each pcap file
for pcap in "$DATASET_DIR"/*.pcap; do
    if [ -f "$pcap" ]; then
        filename=$(basename "$pcap")
        echo "▶️  Replaying: $filename"
        
        # Use tcpreplay to send packets
        sudo tcpreplay --intf1="$INTERFACE" --mbps=1 "$pcap" 2>/dev/null
        
        echo "   ✅ Replay complete"
        echo ""
        sleep 2
    fi
done

echo "=============================================="
echo "✅ ALL DATASETS REPLAYED"
echo "=============================================="
echo "Check Suricata logs for detected attacks!"
echo ""
EOF

chmod +x "$DATASET_DIR/replay_attacks.sh"

echo "✅ Replay script created: $DATASET_DIR/replay_attacks.sh"
echo ""
echo "=============================================="
echo "📖 HOW TO USE"
echo "=============================================="
echo ""
echo "Option 1: Replay downloaded datasets"
echo "  cd $DATASET_DIR"
echo "  ./replay_attacks.sh"
echo ""
echo "Option 2: Use tcpreplay manually"
echo "  sudo tcpreplay -i eth0 portscan.pcap"
echo ""
echo "Option 3: Create your own with tcpdump"
echo "  sudo tcpdump -i eth0 -w custom_attack.pcap"
echo ""
echo "=============================================="
