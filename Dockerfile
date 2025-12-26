FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpcap-dev \
    tcpdump \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Suricata
RUN apt-get update && apt-get install -y \
    suricata \
    suricata-update \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Copy Suricata rules
RUN mkdir -p /etc/suricata/rules
COPY config/custom.rules /etc/suricata/rules/

# Update Suricata rules
RUN suricata-update

# Create necessary directories
RUN mkdir -p /var/log/suricata /var/log/bft-ids

# Expose ports
EXPOSE 5000 5001 5002 5003 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SURICATA_CONFIG=/etc/suricata/suricata.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/status || exit 1

# Default command
CMD ["python3", "src/coordinator.py"]
