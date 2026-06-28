#!/usr/bin/env python3
"""
Master SNI Scanner v2.1.0 - SERVER MODE
Professional Reality SNI Testing Tool
"""

import os
import sys
import json
import subprocess
import time
import signal
import shutil
import uuid
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler

# ============================================================================
# SECTION 1: COLOR SETUP - Terminal color configuration
# ============================================================================

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'


def print_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")


def print_success(msg): print(f"{GREEN}[✓]{RESET} {msg}")


def print_error(msg): print(f"{RED}[✗]{RESET} {msg}")


def print_warning(msg): print(f"{YELLOW}[!]{RESET} {msg}")


# ============================================================================
# SECTION 2: GLOBAL VARIABLES
# ============================================================================

server_instance = None


# ============================================================================
# SECTION 3: PORT MANAGEMENT - Check and free ports
# ============================================================================

def check_port_available(port):
    """Check if a port is available for use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(('0.0.0.0', port))
        return result != 0


def free_port(port):
    """Free a port by killing the process using it"""
    try:
        result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(f"kill -9 {pid}", shell=True, capture_output=True)
                time.sleep(0.5)
        return True
    except Exception:
        return False


def get_available_port(default_port, try_range=10):
    """Find an available port, trying a range if default is taken"""
    port = default_port
    for i in range(try_range):
        if check_port_available(port):
            return port
        else:
            port = default_port + i + 1
    return None


# ============================================================================
# SECTION 4: REQUIREMENTS & SYSTEM - Install dependencies and get system info
# ============================================================================

def install_requirements():
    """Auto-install required Python packages and Xray-core"""
    print_info("Installing requirements...")
    subprocess.run(f'{sys.executable} -m pip install requests -q', shell=True, capture_output=True)

    xray_path = '/usr/local/bin/xray'
    if not os.path.exists(xray_path):
        print_info("Installing Xray-core...")
        subprocess.run(
            'bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install',
            shell=True)
        time.sleep(3)

    print_success("Requirements check complete")


def get_server_ip():
    """Get the server's public IP address"""
    try:
        import urllib.request
        response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
        return response.read().decode('utf-8').strip()
    except:
        return None


# ============================================================================
# SECTION 5: KEY MANAGEMENT - Generate keys and UUID
# ============================================================================

def generate_keys():
    """Generate x25519 keypair using xray x25519 command"""
    xray_path = '/usr/local/bin/xray'
    if not os.path.exists(xray_path):
        return None, None

    try:
        result = subprocess.run([xray_path, 'x25519'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return None, None

        output = result.stdout
        private_key = None
        public_key = None

        for line in output.split('\n'):
            line = line.strip()
            if 'Private key:' in line:
                private_key = line.split('Private key:')[1].strip()
            elif 'Public key:' in line:
                public_key = line.split('Public key:')[1].strip()
            if 'PrivateKey:' in line and not private_key:
                private_key = line.split('PrivateKey:')[1].strip()
            if 'Password (PublicKey):' in line and not public_key:
                public_key = line.split('Password (PublicKey):')[1].strip()

        if private_key and public_key:
            return private_key, public_key
        return None, None
    except Exception:
        return None, None


def generate_random_uuid():
    """Generate a cryptographically secure random UUID v4"""
    return str(uuid.uuid4())


# ============================================================================
# SECTION 6: CONFIGURATION BUILDER - Create Xray server configs
# ============================================================================

def create_server_config(port, private_key, sni_batch, transport_name, server_uuid):
    """Create Xray server configuration with specified transport"""
    transport_configs = {
        'tcp': {'network': 'tcp'},
        'websocket': {'network': 'ws', 'wsSettings': {'path': '/ws'}},
        'grpc': {'network': 'grpc', 'grpcSettings': {'serviceName': 'gun'}},
        'http2': {'network': 'h2', 'httpSettings': {'path': '/'}},
        'xhttp': {'network': 'xhttp', 'xhttpSettings': {'path': '/', 'mode': 'auto'}},
        'quic': {'network': 'quic'},
        'splithttp': {'network': 'splithttp', 'splithttpSettings': {'path': '/split'}}
    }

    transport = transport_configs.get(transport_name, transport_configs['tcp'])

    if not sni_batch or len(sni_batch) == 0:
        sni_batch = ["yahoo.com"]

    target_sni = sni_batch[0]

    reality_settings = {
        "show": False,
        "target": f"{target_sni}:443",
        "xver": 0,
        "serverNames": sni_batch,
        "privateKey": private_key,
        "shortIds": ["6d6f6e6f6c697468", ""]
    }

    inbound = {
        "port": port,
        "protocol": "vless",
        "tag": "reality-in",
        "settings": {
            "clients": [{"id": server_uuid}],
            "decryption": "none"
        },
        "streamSettings": {
            "network": transport['network'],
            "security": "reality",
            "realitySettings": reality_settings
        },
        "sniffing": {"enabled": True, "destOverride": ["http", "tls"]}
    }

    for key, value in transport.items():
        if key != 'network':
            inbound['streamSettings'][key] = value

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [inbound],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }


# ============================================================================
# SECTION 7: XRAY MANAGEMENT - Apply configs and manage Xray service
# ============================================================================

def apply_xray_config(config):
    """Apply configuration to Xray and restart the service"""
    config_path = '/usr/local/etc/xray/config.json'
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        subprocess.run('systemctl stop xray', shell=True, capture_output=True)
        subprocess.run('pkill -9 xray', shell=True, capture_output=True)
        time.sleep(1)
        subprocess.run('systemctl start xray', shell=True, capture_output=True)
        time.sleep(2)

        result = subprocess.run('systemctl is-active xray', shell=True, capture_output=True, text=True)
        return result.stdout.strip() == 'active'
    except Exception as e:
        print_error(f"Config error: {e}")
        return False


def create_minimal_config():
    """Create a minimal valid config to ensure Xray can start"""
    minimal_config = {
        "log": {"loglevel": "warning"},
        "inbounds": [],
        "outbounds": [{"protocol": "freedom", "tag": "direct"}]
    }

    config_path = '/usr/local/etc/xray/config.json'
    os.makedirs('/usr/local/etc/xray', exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(minimal_config, f, indent=2)

    subprocess.run('systemctl stop xray', shell=True, capture_output=True)
    subprocess.run('pkill -9 xray', shell=True, capture_output=True)
    time.sleep(1)
    subprocess.run('systemctl start xray', shell=True, capture_output=True)
    time.sleep(2)


# ============================================================================
# SECTION 8: HTTP API HANDLER - Handle client requests
# ============================================================================

class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for client API requests"""

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        """Handle GET requests - health check endpoint"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'version': '2.0.0'}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests - API endpoints for config and batch management"""
        global server_instance

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return

            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            # Endpoint: Receive SNI list from client and split into batches
            if self.path == '/api/send_config':
                sni_list = data.get('sni_list', [])
                transport = data.get('transport', 'tcp')
                batch_size = data.get('batch_size', 50)

                if not sni_list:
                    self.send_response(400)
                    self.end_headers()
                    return

                print_success(f"Received {len(sni_list)} SNI(s)")
                print_info(f"Transport: {transport}")
                print_info(f"Batch size: {batch_size}")

                batches = [sni_list[i:i + batch_size] for i in range(0, len(sni_list), batch_size)]
                print_info(f"Split into {len(batches)} batches")

                response_data = {
                    'status': 'ok',
                    'port': server_instance.port,
                    'public_key': server_instance.public_key,
                    'server_uuid': server_instance.server_uuid,
                    'short_id': '6d6f6e6f6c697468',
                    'server_ip': server_instance.server_ip,
                    'transport': transport,
                    'batches': batches,
                    'total_batches': len(batches),
                    'version': '2.0.0',
                    'api_port': server_instance.api_port
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())

            # Endpoint: Apply a specific batch to Xray
            elif self.path == '/api/apply_batch':
                sni_batch = data.get('sni_batch', [])
                transport = data.get('transport', 'tcp')
                batch_index = data.get('batch_index', 0)
                total_batches = data.get('total_batches', 1)

                if not sni_batch:
                    self.send_response(400)
                    self.end_headers()
                    return

                print_info(f"Applying batch {batch_index + 1}/{total_batches} ({len(sni_batch)} SNIs)")

                config = create_server_config(
                    server_instance.port,
                    server_instance.private_key,
                    sni_batch,
                    transport,
                    server_instance.server_uuid
                )

                if apply_xray_config(config):
                    self.send_response(200)
                    self.end_headers()
                else:
                    self.send_response(500)
                    self.end_headers()

            else:
                self.send_response(404)
                self.end_headers()

        except Exception as e:
            print_error(f"Request error: {e}")
            self.send_response(500)
            self.end_headers()


# ============================================================================
# SECTION 9: SERVER CLASS - Store server configuration
# ============================================================================

class Server:
    """Server configuration container"""

    def __init__(self, port, api_port, private_key, public_key, server_ip, server_uuid):
        self.port = port
        self.api_port = api_port
        self.private_key = private_key
        self.public_key = public_key
        self.server_ip = server_ip
        self.server_uuid = server_uuid


# ============================================================================
# SECTION 10: SIGNAL HANDLER & MAIN - Main execution flow
# ============================================================================

def signal_handler(signum, frame):
    """Handle Ctrl+C interrupt gracefully"""
    print_info("\nShutting down server...")
    sys.exit(0)


def main():
    """Main server execution flow"""
    global server_instance

    print(f"""
{MAGENTA}
╔══════════════════════════════════════════════════════════════════╗
║     Master SNI Scanner v2.1.0 - SERVER MODE                     ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")

    if os.geteuid() != 0:
        print_error("Run with: sudo python3 server-sniScanner.py")
        return

    install_requirements()

    print(f"\n{YELLOW}=== Configuration ==={RESET}")

    # Get Reality port
    port_input = input(f"{CYAN}Reality port (default 443): {RESET}").strip()
    desired_port = int(port_input) if port_input.isdigit() else 443

    if not check_port_available(desired_port):
        print_warning(f"Port {desired_port} is in use, trying to free...")
        free_port(desired_port)
        time.sleep(1)

    port = get_available_port(desired_port)
    if not port:
        print_error(f"No available port near {desired_port}")
        return
    if port != desired_port:
        print_warning(f"Using port {port} instead of {desired_port}")

    # Get API port
    api_input = input(f"{CYAN}API port (default 8080): {RESET}").strip()
    desired_api_port = int(api_input) if api_input.isdigit() else 8080

    if not check_port_available(desired_api_port):
        print_warning(f"API port {desired_api_port} is in use, trying to free...")
        free_port(desired_api_port)
        time.sleep(1)

    api_port = get_available_port(desired_api_port)
    if not api_port:
        print_error(f"No available API port near {desired_api_port}")
        return
    if api_port != desired_api_port:
        print_warning(f"Using API port {api_port} instead of {desired_api_port}")

    # Generate keys
    print_info("Generating keys...")
    private_key, public_key = generate_keys()

    if not private_key or not public_key:
        print_warning("Could not generate keys automatically")
        private_key = input(f"{CYAN}Private Key: {RESET}").strip()
        public_key = input(f"{CYAN}Public Key: {RESET}").strip()

    if not private_key or not public_key:
        print_error("No valid keys")
        return

    print_success(f"Private Key: {private_key[:20]}...")
    print_success(f"Public Key: {public_key[:40]}...")

    # Generate UUID
    server_uuid = generate_random_uuid()
    print_success(f"Server UUID: {server_uuid}")

    # Get server IP
    server_ip = get_server_ip()
    if not server_ip:
        server_ip = input(f"{CYAN}Server IP: {RESET}").strip()

    print_success(f"Server IP: {server_ip}")

    # Initialize Xray with minimal config
    create_minimal_config()

    # Create server instance
    server_instance = Server(port, api_port, private_key, public_key, server_ip, server_uuid)
    signal.signal(signal.SIGINT, signal_handler)

    # Start HTTP server
    http_server = HTTPServer(('0.0.0.0', api_port), CustomHTTPRequestHandler)

    print(f"\n{GREEN}{'=' * 60}{RESET}")
    print(f"{GREEN}SERVER READY{RESET}")
    print(f"{GREEN}{'=' * 60}{RESET}")
    print(f"  Reality: {CYAN}{server_ip}:{port}{RESET}")
    print(f"  API Port: {CYAN}{api_port}{RESET}")
    print(f"  UUID: {CYAN}{server_uuid}{RESET}")
    print(f"\n{BLUE}Client command:{RESET}")
    print(f"{YELLOW}python3 client-sniScanner.py --server {server_ip} --api-port {api_port}{RESET}")

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()