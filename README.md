# Master Reality SNI Scanner

## Professional Reality Protocol SNI Testing Tool

### 📌 Overview

**Master Reality SNI Scanner** is a professional-grade, cross-platform tool designed for comprehensive testing of SNI (Server Name Indication) compatibility with the Reality protocol. Built with a modern client-server architecture, it enables security researchers, network administrators, and penetration testers to systematically evaluate SNI configurations across diverse network environments.

The tool addresses the critical challenge of identifying which SNI domains work reliably with Reality-based proxy configurations, allowing users to discover optimal settings for their specific network conditions.

---

### 🚀 Key Features

#### Server Component (`server-sniScanner.py`)
- **Batch Processing**: Efficiently handles large SNI lists by processing them in configurable batches (default: 50 SNIs per batch)
- **Dynamic Configuration**: Automatically generates and applies Reality server configurations for each batch
- **UUID Security**: Generates cryptographically secure random UUIDs for each session
- **Multi-Transport Support**: Full compatibility with 7 transport protocols
- **Port Management**: Automatic port detection and conflict resolution
- **RESTful API**: Clean HTTP API for seamless client-server communication

#### Client Component (`client-sniScanner.py`)
- **Parallel Testing**: Multi-threaded testing with configurable worker count (1-20 workers)
- **Four SNI Input Methods**:
  - Manual entry (one-by-one)
  - File import (batch loading from text files)
  - Auto-scan (discovers nearby SNI candidates)
  - Default presets (common working SNIs)
- **Real-time Results**: Live feedback with latency metrics and success/failure status
- **Formatted Output**: Beautiful ASCII tables for improved readability
- **Comprehensive Logging**: Detailed results saved with timestamps

#### Auto Installer (`dependencies-autoInstaller.py`)
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Intelligent Detection**: Automatically detects installed dependencies
- **One-Command Setup**: Installs Python packages and Xray-core
- **Status Reporting**: Shows clear installation status table

---

### 🛠️ Supported Transport Protocols

| Protocol | Description | Use Case |
|----------|-------------|----------|
| **TCP** | Standard TCP protocol | Maximum compatibility |
| **WebSocket (WS)** | WebSocket tunneling | CDN-friendly connections |
| **gRPC** | High-performance RPC | Low-latency requirements |
| **HTTP/2 (h2)** | HTTP/2 framing | Web traffic simulation |
| **XHTTP** | Advanced HTTP multiplexing | **Recommended for optimal performance** |
| **QUIC** | UDP-based protocol | Mobile networks, reduced latency |
| **SplitHTTP** | Fragmented HTTP requests | Anti-detection, CDN environments |

---

### 💻 Cross-Platform Compatibility

- **Linux** (Ubuntu, Debian, CentOS, RHEL, Arch)
- **macOS** (Intel and Apple Silicon)
- **Windows** (10, 11, Server editions)

---

### 📦 System Requirements

#### Server Requirements
- Python 3.6+
- Xray-core (v1.8.0+)
- Root/Sudo privileges (for Xray management)
- OpenSSL
- 1GB+ RAM (recommended)
- 10GB+ disk space (for logs)

#### Client Requirements
- Python 3.6+
- Xray-core (v1.8.0+)
- 512MB+ RAM
- Internet connection to target server

---

### 🔧 Installation

#### Quick Install
```bash
# Clone repository
git clone https://github.com/AminDaProgrammer/Master_Reality_SNI_Scanner.git
cd Master_Reality_SNI_Scanner

# Auto-install dependencies
python3 dependencies-autoInstaller.py

# Start server (on VPS)
sudo python3 server-sniScanner.py

# Start client (on testing machine)
python3 client-sniScanner.py --server <SERVER_IP>
```

#### Manual Installation
```bash
# Install Python dependencies
pip install requests cryptography

# Install Xray-core
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

---

### 🎯 Use Cases

| Use Case | Description |
|----------|-------------|
| **SNI Discovery** | Find working SNI domains for Reality configurations |
| **Network Testing** | Evaluate SNI performance across different networks |
| **Security Auditing** | Verify SNI integrity and compatibility |
| **Optimization** | Identify fastest SNI for specific locations |
| **Research** | Analyze SNI filtering patterns in various regions |

---

### 📊 Output Format

Results are saved in the `results/` directory with human-readable filenames:

```
Master_Reality_SNI_Scanner_2025_01_15_14_30_25.txt
```

#### File Contents
- **Summary Statistics**: Total tested, working, failed, success rate
- **Working SNIs Table**: Ranked list with latency metrics
- **Failed SNIs Table**: List of non-functional domains
- **Configuration Links**: Ready-to-use VLESS configuration strings

---

### 🔒 Security Considerations

- **Random UUID Generation**: Each session uses cryptographically secure UUIDs
- **No Hardcoded Credentials**: All configurations generated dynamically
- **Minimal Attack Surface**: API exposed only during active testing
- **Cleanup Routine**: Xray processes terminated after testing
- **No Persistent Data**: All logs and configs are temporary

---

### 📁 Project Structure

```
Master_Reality_SNI_Scanner/
├── server-sniScanner.py          # Server module - Reality config management
├── client-sniScanner.py          # Client module - SNI testing & reporting
├── dependencies-autoInstaller.py # Auto installer - Cross-platform dependencies
├── results/                      # Test results directory (auto-created)
│   └── Master_Reality_SNI_Scanner_*.txt
└── README.md                     # Project documentation
```

---

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  SNI Input: Manual | File | Auto-scan | Default         │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Transport Selection: TCP | WS | gRPC | h2 | XHTTP...  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Parallel Testing: Worker Pool (1-20 threads)          │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Results: Real-time table + File export                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP API (Port: 8080)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Batch Processing: 50 SNIs per batch                    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Reality Config Builder: UUID, Private/Public Keys      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Xray Manager: Start/Stop/Restart Service               │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Transport Config: TCP | WS | gRPC | h2 | XHTTP...    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

### 📈 Performance Benchmarks

| Metric | Value |
|--------|-------|
| **SNIs per Batch** | 50 (configurable) |
| **Parallel Workers** | 5-10 (configurable) |
| **Test Duration (50 SNIs)** | ~30-45 seconds |
| **Test Duration (500 SNIs)** | ~5-8 minutes |
| **Memory Usage** | ~150-300MB |
| **CPU Usage** | ~25-50% (with 5 workers) |

---

### 🛡️ Error Handling

- **Graceful Degradation**: Continues testing even if individual SNIs fail
- **Automatic Recovery**: Restores previous config on server failure
- **Timeout Management**: Configurable timeouts prevent hanging
- **Resource Cleanup**: Automatic termination of Xray processes
- **User Interrupt**: Ctrl+C gracefully shuts down all services

---

### 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

### 📄 License

**MIT License** - Free for personal and commercial use.

```
MIT License

Copyright (c) 2025 Master Reality SNI Scanner Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### ⚡ Quick Commands

```bash
# Install dependencies
python3 dependencies-autoInstaller.py

# Start server (Linux/macOS)
sudo python3 server-sniScanner.py

# Start server (Windows - as Administrator)
python server-sniScanner.py

# Start client
python3 client-sniScanner.py

# Start client with specific server
python3 client-sniScanner.py --server 192.168.1.100
```

---

### 🔗 Related Projects

- [Xray-core](https://github.com/XTLS/Xray-core) - Core proxy framework
- [VLESS Protocol](https://github.com/XTLS/Xray-examples) - Protocol documentation
- [3x-ui](https://github.com/MHSanaei/3x-ui) - Xray panel (inspiration)

---

**Master Reality SNI Scanner** - Empowering security professionals with reliable SNI testing for Reality protocol deployments.
