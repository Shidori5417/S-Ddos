# FsocietyDDoS - Linux Installation & Usage Guide

## 🐧 Linux Compatibility

This project has been fully optimized for Linux operating systems. All Windows-specific dependencies have been removed and replaced with Linux-compatible alternatives.

## 📋 System Requirements

### Supported Linux Distributions
- **Ubuntu** 18.04+ / **Debian** 10+
- **CentOS** 7+ / **RHEL** 7+ / **Fedora** 30+
- **Arch Linux** / **Manjaro**
- Other Linux distributions (manual package installation may be required)

### Hardware Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Ethernet or Wi-Fi connection

### Software Requirements
- **Python**: 3.7 or higher
- **Root privileges**: Required for raw socket operations
- **Internet connection**: For dependency installation

## 🚀 Quick Installation

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-repo/FsocietyDDoS.git
cd FsocietyDDoS

# Run the automated Linux setup
sudo python3 setup_linux.py
```

The setup script will:
- ✅ Check system requirements
- ✅ Install system packages
- ✅ Install Python dependencies
- ✅ Configure network capabilities
- ✅ Setup Tor service
- ✅ Create configuration files
- ✅ Setup systemd service (optional)

### Manual Installation

If you prefer manual installation:

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-dev python3-pip build-essential libssl-dev libffi-dev libpcap-dev net-tools iptables tor
```

**CentOS/RHEL/Fedora:**
```bash
# For CentOS/RHEL
sudo yum install -y python3-devel python3-pip gcc gcc-c++ make openssl-devel libffi-devel libpcap-devel net-tools iptables tor

# For Fedora
sudo dnf install -y python3-devel python3-pip gcc gcc-c++ make openssl-devel libffi-devel libpcap-devel net-tools iptables tor
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip base-devel openssl libffi libpcap net-tools iptables tor
```

#### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

#### 3. Configure Network Capabilities

```bash
# Allow raw socket operations without root
sudo setcap cap_net_raw+ep $(which python3)
```

#### 4. Start Tor Service

```bash
sudo systemctl enable tor
sudo systemctl start tor
```

## 🔧 Configuration

### Linux-Specific Configuration

The setup creates a `config/linux_config.json` file with Linux-optimized settings:

```json
{
  "system": {
    "platform": "linux",
    "use_raw_sockets": true,
    "network_interface": "auto",
    "enable_capabilities": true
  },
  "security": {
    "drop_privileges": true,
    "use_tor": true,
    "enable_iptables_rules": false
  },
  "logging": {
    "syslog_enabled": true,
    "log_rotation": true,
    "max_log_size": "100MB"
  }
}
```

### Network Interface Configuration

To specify a network interface:

```bash
# List available interfaces
ip link show

# Set interface in config
python3 fsociety_ddos.py --interface eth0
```

## 🎯 Usage

### Basic Usage

```bash
# Show help
python3 fsociety_ddos.py --help

# Basic attack
python3 fsociety_ddos.py --target 192.168.1.100 --method tcp_flood --threads 100

# Advanced attack with monitoring
python3 fsociety_ddos.py --target example.com --method http_flood --threads 200 --monitor
```

### Service Mode

Run as a systemd service:

```bash
# Enable service
sudo systemctl enable fsociety-ddos

# Start service
sudo systemctl start fsociety-ddos

# Check status
sudo systemctl status fsociety-ddos

# View logs
sudo journalctl -u fsociety-ddos -f
```

### Advanced Features

#### 1. Tor Integration
```bash
# Use Tor for anonymity
python3 fsociety_ddos.py --target example.com --use-tor --method http_flood
```

#### 2. Performance Monitoring
```bash
# Enable real-time monitoring
python3 fsociety_ddos.py --target example.com --monitor --optimize
```

#### 3. Multi-Interface Support
```bash
# Use multiple network interfaces
python3 fsociety_ddos.py --target example.com --interfaces eth0,wlan0
```

## 🛡️ Security Features

### Linux-Optimized Security

- **Process Isolation**: Automatic privilege dropping after initialization
- **Network Capabilities**: Uses Linux capabilities instead of root privileges
- **Tor Integration**: Built-in Tor support for anonymity
- **Sandbox Detection**: Linux-specific virtualization and sandbox detection
- **Resource Monitoring**: Real-time system resource monitoring

### Firewall Configuration

Configure iptables for enhanced security:

```bash
# Allow outgoing connections
sudo iptables -A OUTPUT -p tcp --dport 80,443 -j ACCEPT
sudo iptables -A OUTPUT -p udp --dport 53 -j ACCEPT

# Block incoming connections (optional)
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -j DROP
```

## 📊 Monitoring & Logging

### System Monitoring

The tool includes comprehensive Linux system monitoring:

- **CPU Usage**: Per-core monitoring with automatic optimization
- **Memory Usage**: RAM and swap monitoring with leak detection
- **Network I/O**: Real-time bandwidth and connection tracking
- **Process Monitoring**: Attack process tracking and management

### Log Files

Default log locations:
- **Application logs**: `./logs/fsociety.log`
- **System logs**: `/var/log/syslog` (if syslog enabled)
- **Monitoring logs**: `./logs/monitoring.log`

### Performance Optimization

Automatic optimizations for Linux:
- Process priority adjustment using `nice` values
- Memory optimization with garbage collection
- Network buffer tuning
- CPU affinity optimization

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied Errors
```bash
# Solution: Set network capabilities
sudo setcap cap_net_raw+ep $(which python3)

# Or run with sudo (not recommended)
sudo python3 fsociety_ddos.py
```

#### Tor Connection Issues
```bash
# Check Tor status
sudo systemctl status tor

# Restart Tor service
sudo systemctl restart tor

# Check Tor configuration
sudo nano /etc/tor/torrc
```

#### Package Installation Errors
```bash
# Update package lists
sudo apt update  # Ubuntu/Debian
sudo yum update  # CentOS/RHEL

# Install missing development tools
sudo apt install build-essential  # Ubuntu/Debian
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
```

### Performance Issues

#### High CPU Usage
```bash
# Enable automatic optimization
python3 fsociety_ddos.py --optimize --cpu-limit 80

# Monitor system resources
htop
```

#### Memory Issues
```bash
# Enable memory optimization
python3 fsociety_ddos.py --optimize-memory --memory-limit 4G

# Check memory usage
free -h
```

#### Network Issues
```bash
# Check network interfaces
ip link show

# Monitor network traffic
sudo nethogs
sudo iftop
```

## 📈 Performance Tuning

### System-Level Optimizations

#### 1. Network Stack Tuning
```bash
# Increase network buffers
echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 87380 134217728' | sudo tee -a /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

#### 2. File Descriptor Limits
```bash
# Increase file descriptor limits
echo '* soft nofile 65536' | sudo tee -a /etc/security/limits.conf
echo '* hard nofile 65536' | sudo tee -a /etc/security/limits.conf
```

#### 3. CPU Performance
```bash
# Set CPU governor to performance
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### Application-Level Optimizations

#### 1. Thread Configuration
```bash
# Optimize thread count based on CPU cores
python3 fsociety_ddos.py --threads $(nproc)
```

#### 2. Memory Management
```bash
# Enable memory optimization
python3 fsociety_ddos.py --optimize-memory --gc-threshold 1000
```

## 🔒 Legal & Ethical Usage

### ⚠️ Important Legal Notice

This tool is designed for:
- **Educational purposes**
- **Authorized penetration testing**
- **Network security research**
- **Load testing your own infrastructure**

### Responsible Usage Guidelines

1. **Only test systems you own or have explicit permission to test**
2. **Comply with local laws and regulations**
3. **Use appropriate rate limiting to avoid service disruption**
4. **Document and report findings responsibly**
5. **Respect network resources and infrastructure**

### Legal Compliance

Before using this tool:
- ✅ Obtain written authorization
- ✅ Review applicable laws in your jurisdiction
- ✅ Follow responsible disclosure practices
- ✅ Implement appropriate safeguards
- ✅ Monitor and log all activities

## 🤝 Contributing

We welcome contributions to improve Linux compatibility:

1. **Fork the repository**
2. **Create a feature branch**
3. **Test on multiple Linux distributions**
4. **Submit a pull request**

### Development Setup

```bash
# Clone for development
git clone https://github.com/your-repo/FsocietyDDoS.git
cd FsocietyDDoS

# Install development dependencies
pip3 install -r requirements-dev.txt

# Run tests
python3 -m pytest tests/

# Run linting
python3 -m flake8 .
```

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join community discussions
- **Security**: Report security issues privately

### System Information

When reporting issues, include:
```bash
# System information
uname -a
python3 --version
pip3 list | grep -E "(psutil|scapy|requests)"

# Network configuration
ip addr show
```

---

**Remember**: Use this tool responsibly and legally. Always obtain proper authorization before testing any systems you do not own.