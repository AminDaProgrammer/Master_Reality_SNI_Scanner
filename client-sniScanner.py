#!/usr/bin/env python3
"""
Master SNI Scanner v2.1.0 - CLIENT MODE
Professional Reality SNI Testing Tool
"""

import os
import sys
import json
import time
import subprocess
import argparse
import tempfile
import requests
import platform
import re
import socket
import signal
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# ============================================================================
# SECTION 1: COLOR SETUP - Terminal color configuration
# ============================================================================

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'


def setup_colors():
    """Configure colors for Windows and Linux terminal compatibility"""
    global GREEN, RED, YELLOW, BLUE, CYAN, MAGENTA, WHITE, BOLD, RESET

    if platform.system().lower() == 'windows':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass

        try:
            from colorama import init, Fore, Style
            init(autoreset=True)
            GREEN = Fore.GREEN
            RED = Fore.RED
            YELLOW = Fore.YELLOW
            BLUE = Fore.BLUE
            CYAN = Fore.CYAN
            MAGENTA = Fore.MAGENTA
            WHITE = Fore.WHITE
            BOLD = Style.BRIGHT
            RESET = Style.RESET_ALL
            return
        except ImportError:
            pass

    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


setup_colors()


# ============================================================================
# SECTION 2: UI HELPERS - Terminal display utilities
# ============================================================================

def print_banner():
    """Display the application banner at startup"""
    print(f"""{MAGENTA}{BOLD}
╔══════════════════════════════════════════════════════════════════╗
║     Master SNI Scanner v2.1.0 - CLIENT MODE                     ║
║     Professional Reality SNI Testing Tool                       ║
╚══════════════════════════════════════════════════════════════════╝{RESET}
""")


def print_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")


def print_success(msg): print(f"{GREEN}[✓]{RESET} {msg}")


def print_error(msg): print(f"{RED}[✗]{RESET} {msg}")


def print_warning(msg): print(f"{YELLOW}[!]{RESET} {msg}")


def print_table(headers, rows):
    """Print a formatted table"""
    if not rows:
        return

    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    col_widths = [w + 2 for w in col_widths]
    total_width = sum(col_widths) + len(headers) + 1

    print(f"{CYAN}{'─' * total_width}{RESET}")

    header_line = "│"
    for i, header in enumerate(headers):
        header_line += f" {str(header).ljust(col_widths[i] - 1)}│"
    print(f"{CYAN}{header_line}{RESET}")

    print(f"{CYAN}{'─' * total_width}{RESET}")

    for row in rows:
        row_line = "│"
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "-"
            row_line += f" {cell_str.ljust(col_widths[i] - 1)}│"
        print(f"{row_line}{RESET}")

    print(f"{CYAN}{'─' * total_width}{RESET}")


# ============================================================================
# SECTION 3: XRAY PROCESS MANAGEMENT - Control Xray processes
# ============================================================================

def kill_all_xray():
    """Kill all Xray processes"""
    if platform.system().lower() == 'windows':
        subprocess.run('taskkill /f /im xray.exe', shell=True, capture_output=True)
    else:
        subprocess.run('pkill -9 xray', shell=True, capture_output=True)


def get_xray_path():
    """Find Xray executable path"""
    if platform.system().lower() == 'windows':
        paths = [r'C:\Program Files\xray\xray.exe', r'C:\xray\xray.exe']
        for path in paths:
            if os.path.exists(path):
                return path
    else:
        paths = ['/usr/local/bin/xray', '/usr/bin/xray']
        for path in paths:
            if os.path.exists(path):
                return path

    import shutil
    return shutil.which('xray')


# ============================================================================
# SECTION 4: USER INTERACTION - Get configuration from user
# ============================================================================

def select_transport():
    """Prompt user to select a transport protocol"""
    print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{YELLOW}{BOLD}Step 1: Select Transport Protocol{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}1.{RESET} TCP")
    print(f"{CYAN}2.{RESET} WebSocket (ws)")
    print(f"{CYAN}3.{RESET} gRPC")
    print(f"{CYAN}4.{RESET} HTTP/2 (h2)")
    print(f"{CYAN}5.{RESET} XHTTP {WHITE}(Recommended){RESET}")
    print(f"{CYAN}6.{RESET} QUIC")
    print(f"{CYAN}7.{RESET} SplitHTTP")

    choice = input(f"\n{YELLOW}Select [1-7] (default 5): {RESET}").strip() or '5'

    transports = {
        '1': 'tcp', '2': 'websocket', '3': 'grpc',
        '4': 'http2', '5': 'xhttp', '6': 'quic', '7': 'splithttp'
    }

    selected = transports.get(choice, 'xhttp')
    print_success(f"Transport: {selected}")
    return selected


def select_workers():
    """Prompt user to select the number of parallel workers"""
    print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{YELLOW}{BOLD}Step 2: Select Number of Parallel Workers{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}Recommended: 5-10 for most connections{RESET}")
    print(f"{CYAN}Higher = faster but more resource intensive{RESET}\n")

    choice = input(f"{CYAN}Number of workers (default 5): {RESET}").strip()
    workers = int(choice) if choice.isdigit() else 5
    print_success(f"Using {workers} parallel workers")
    return workers


def select_batch_size():
    """Prompt user to select the batch size for SNI testing"""
    print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{YELLOW}{BOLD}Step 3: Select Batch Size{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}Each batch = number of SNIs per server config{RESET}")
    print(f"{CYAN}Recommended: 50 (balance between speed and stability){RESET}\n")

    choice = input(f"{CYAN}Batch size (default 50): {RESET}").strip()
    batch_size = int(choice) if choice.isdigit() else 50
    print_success(f"Batch size: {batch_size}")
    return batch_size


def scan_nearby_snis(server_ip, threads=20):
    """Auto-scan for SNI candidates"""
    print_info("Auto-scanning for nearby SNIs...")
    print_warning("This may take 1-2 minutes...")

    try:
        ip_parts = server_ip.split('.')
        base_network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
    except:
        return ["www.yahoo.com", "google.com", "cloudflare.com"]

    print_info(f"Scanning network: {base_network}.0/24")

    def check_port(ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 443))
            sock.close()
            return ip if result == 0 else None
        except:
            return None

    ips_to_check = [f"{base_network}.{i}" for i in range(1, 51)]
    open_ips = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_port, ip): ip for ip in ips_to_check}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ips.append(result)

    if not open_ips:
        return ["www.yahoo.com", "google.com", "cloudflare.com"]

    snis = []
    for ip in open_ips[:20]:
        try:
            cmd = f"echo | timeout 3 openssl s_client -connect {ip}:443 -servername {ip} 2>/dev/null | openssl x509 -noout -text 2>/dev/null | grep -oP 'DNS:[^,]+' | cut -d: -f2 | head -1"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            if result.stdout.strip():
                sni = result.stdout.strip().lower()
                if re.match(r'^[a-z0-9][a-z0-9\.-]+\.[a-z]{2,}$', sni) and not sni.startswith('*.'):
                    if sni not in snis and len(snis) < 30:
                        snis.append(sni)
                        print(f"{CYAN}[SNI]{RESET} Found: {sni}")
        except:
            continue

    return snis if snis else ["www.yahoo.com", "google.com", "cloudflare.com"]


def get_sni_from_file():
    """Load SNIs from a text file"""
    file_path = input(f"{CYAN}Enter file path: {RESET}").strip()

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return None

    snis = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            sni = line.strip().lower()
            if sni and '.' in sni and len(sni) > 3 and not sni.startswith('#'):
                if sni not in snis:
                    snis.append(sni)

    if snis:
        print_success(f"Loaded {len(snis)} SNIs from file")
    else:
        print_error("No valid SNIs found in file")
    return snis


def get_sni_manual():
    """Get SNIs manually from user input"""
    print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{YELLOW}{BOLD}Enter SNI Domains Manually{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}Enter one per line. Empty line to finish.{RESET}\n")

    sni_list = []
    while True:
        sni = input(f"{CYAN}SNI>{RESET} ").strip().lower()
        if not sni:
            if len(sni_list) == 0:
                print_warning("Please enter at least one SNI")
                continue
            break
        if re.match(r'^[a-z0-9][a-z0-9\.-]+\.[a-z]{2,}$', sni) and len(sni) > 3:
            if sni not in sni_list:
                sni_list.append(sni)
                print_success(f"Added: {sni}")
            else:
                print_warning(f"Already added: {sni}")
        else:
            print_error(f"Invalid SNI format: {sni}")

    return sni_list


# ============================================================================
# SECTION 5: SNI LIST MANAGEMENT - Get SNI list based on selected method
# ============================================================================

def get_sni_list(server_ip, sni_method):
    """Get SNI list based on selected method"""
    if sni_method == '1':
        return get_sni_manual()
    elif sni_method == '2':
        snis = get_sni_from_file()
        if snis:
            # Ask user if they want to shuffle
            shuffle_choice = input(f"{CYAN}Shuffle SNI list? (y/n): {RESET}").strip().lower()
            if shuffle_choice == 'y':
                random.shuffle(snis)
                print_success(f"SNI list shuffled ({len(snis)} items)")
            return snis
        else:
            print_warning("No valid SNIs found in file. Falling back to manual input.")
            return get_sni_manual()
    elif sni_method == '3':
        return scan_nearby_snis(server_ip)
    else:
        default = ["www.yahoo.com", "google.com", "cloudflare.com", "m.tiktok.com", "microsoft.com", "github.com"]
        print_success(f"Using default list ({len(default)} SNIs)")
        for sni in default:
            print(f"  • {sni}")
        return default


def show_sni_method_menu():
    """Display SNI method menu and get user choice"""
    print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{YELLOW}{BOLD}Step 4: Select SNI Input Method{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
    print(f"{CYAN}1.{RESET} Manual Input (Type SNIs one by one)")
    print(f"{CYAN}2.{RESET} Load from File (Text file with SNIs)")
    print(f"{CYAN}3.{RESET} Auto Scan (Find nearby SNIs automatically)")
    print(f"{CYAN}4.{RESET} Default List (Common SNIs)")
    print()

    choice = input(f"{YELLOW}Select [1-4] (default 4): {RESET}").strip() or '4'
    return choice


def install_requirements():
    """Check and install requirements"""
    print_info("Checking requirements...")

    for package in ['requests', 'cryptography']:
        try:
            __import__(package)
        except ImportError:
            print_info(f"Installing {package}...")
            subprocess.run(f'{sys.executable} -m pip install {package} -q', shell=True, capture_output=True)

    xray_path = get_xray_path()
    if not xray_path:
        print_warning("Xray not found. Please install Xray-core first")
        if platform.system().lower() == 'windows':
            print("  Download: https://github.com/XTLS/Xray-core/releases")
        else:
            print(
                "  Run: bash -c \"$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)\" @ install")
        input(f"\n{YELLOW}Press Enter after installing Xray...{RESET}")
    else:
        print_success(f"Xray found at: {xray_path}")

    print_success("Requirements check complete")


# ============================================================================
# SECTION 6: XRAY CLIENT CONFIGURATION - Build client configs
# ============================================================================

def create_xray_config(server_ip, port, public_key, sni, short_id, server_uuid, transport):
    """Create Xray client configuration with server UUID"""

    user = {"id": server_uuid, "encryption": "none"}

    outbound = {
        "protocol": "vless",
        "tag": "proxy",
        "settings": {"vnext": [{"address": server_ip, "port": port, "users": [user]}]},
        "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {"serverName": sni, "fingerprint": "chrome", "publicKey": public_key,
                                "shortId": short_id}
        }
    }

    if transport == 'websocket':
        outbound['streamSettings']['network'] = 'ws'
        outbound['streamSettings']['wsSettings'] = {'path': '/ws'}
    elif transport == 'grpc':
        outbound['streamSettings']['network'] = 'grpc'
        outbound['streamSettings']['grpcSettings'] = {'serviceName': 'gun'}
    elif transport == 'http2':
        outbound['streamSettings']['network'] = 'h2'
        outbound['streamSettings']['httpSettings'] = {'path': '/'}
    elif transport == 'xhttp':
        outbound['streamSettings']['network'] = 'xhttp'
        outbound['streamSettings']['xhttpSettings'] = {'path': '/', 'mode': 'auto'}
    elif transport == 'quic':
        outbound['streamSettings']['network'] = 'quic'
    elif transport == 'splithttp':
        outbound['streamSettings']['network'] = 'splithttp'
        outbound['streamSettings']['splithttpSettings'] = {'path': '/split'}

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{"port": 1080, "protocol": "socks", "settings": {"udp": True, "auth": "noauth"}}],
        "outbounds": [outbound, {"protocol": "freedom", "tag": "direct"}]
    }


# ============================================================================
# SECTION 7: CONNECTION TESTING - Test SNI connections
# ============================================================================

def run_single_xray_and_test(config_path, timeout=8):
    """Run a single Xray instance and test connection"""
    xray_path = get_xray_path()
    if not xray_path:
        return False, None

    kill_all_xray()
    time.sleep(0.5)

    if platform.system().lower() == 'windows':
        process = subprocess.Popen(
            [xray_path, 'run', '-c', config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    else:
        process = subprocess.Popen(
            [xray_path, 'run', '-c', config_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )

    time.sleep(1.5)

    proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}

    try:
        start_time = time.time()
        response = requests.get('https://www.cloudflare.com/cdn-cgi/trace', proxies=proxies, timeout=timeout)
        latency = int((time.time() - start_time) * 1000)
        process.terminate()
        return response.status_code == 200, latency
    except:
        process.terminate()
        return False, None


def test_single_sni(server_ip, port, public_key, sni, short_id, server_uuid, transport):
    """Test a single SNI"""
    config_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = create_xray_config(server_ip, port, public_key, sni, short_id, server_uuid, transport)
            json.dump(config, f, indent=2)
            config_path = f.name

        success, latency = run_single_xray_and_test(config_path)

        if config_path and os.path.exists(config_path):
            os.unlink(config_path)

        if success:
            link = f"vless://{server_uuid}@{server_ip}:{port}?security=reality&encryption=none&pbk={public_key}&sni={sni}&sid={short_id}&type={transport}&fp=chrome#Reality_{sni}"
            return {'sni': sni, 'success': True, 'latency': latency, 'link': link}
        return {'sni': sni, 'success': False, 'latency': None, 'link': None}
    except Exception:
        if config_path and os.path.exists(config_path):
            try:
                os.unlink(config_path)
            except:
                pass
        return {'sni': sni, 'success': False, 'latency': None, 'link': None}


def test_batch_parallel(sni_batch, server_ip, port, public_key, short_id, server_uuid, transport, max_workers):
    """Test a batch of SNIs in parallel"""
    global _test_results_global
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(test_single_sni, server_ip, port, public_key, sni, short_id, server_uuid, transport): sni
            for sni in sni_batch}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            # Store each result immediately for partial display on interrupt
            _test_results_global.append(result)

            if result['success']:
                print_success(f"  ✓ {result['sni']} ({result['latency']}ms)")
            else:
                print_warning(f"  ✗ {result['sni']}")

    return results


# ============================================================================
# SECTION 8: SERVER COMMUNICATION - Send/Receive data from server
# ============================================================================

def send_config_to_server(server_ip, sni_list, transport, batch_size, api_port=8080):
    """Send SNI list and config to server"""
    try:
        response = requests.post(
            f'http://{server_ip}:{api_port}/api/send_config',
            json={'sni_list': sni_list, 'transport': transport, 'batch_size': batch_size},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Server returned {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        return None


def apply_server_batch(server_ip, sni_batch, transport, batch_index, total_batches, api_port=8080):
    """Tell server to apply a specific batch"""
    try:
        response = requests.post(
            f'http://{server_ip}:{api_port}/api/apply_batch',
            json={'sni_batch': sni_batch, 'transport': transport, 'batch_index': batch_index,
                  'total_batches': total_batches},
            timeout=30
        )
        return response.status_code == 200
    except:
        return False


# ============================================================================
# SECTION 9: RESULTS HANDLING - Save and display results
# ============================================================================

def save_results_table(all_results, server_ip, port, transport):
    """Save all results to results folder"""
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    filename = results_dir / f"Master_SNI_Scanner_{timestamp}.txt"

    working = [r for r in all_results if r['success']]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"MASTER SNI SCANNER v2.1.0 - TEST RESULTS\n")
        f.write(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Server: {server_ip}:{port}\n")
        f.write(f"Transport: {transport.upper()}\n")
        f.write(f"Total SNIs Tested: {len(all_results)}\n")
        f.write(f"Working SNIs: {len(working)}\n")
        f.write("=" * 100 + "\n\n")

        if working:
            f.write("WORKING SNIs:\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'#':<5} {'SNI Domain':<40} {'Latency (ms)':<15} {'Status':<10}\n")
            f.write("-" * 100 + "\n")
            # Feature 3: Sort by latency (low to high)
            working_sorted = sorted(working, key=lambda x: x['latency'])
            for i, w in enumerate(working_sorted, 1):
                f.write(f"{i:<5} {w['sni']:<40} {w['latency']:<15} WORKING\n")
            f.write("-" * 100 + "\n\n")

            f.write("WORKING CONFIGURATION LINKS:\n")
            f.write("=" * 100 + "\n\n")
            for w in working_sorted:
                f.write(f"SNI: {w['sni']}\n")
                f.write(f"Link: {w['link']}\n")
                f.write("-" * 100 + "\n")

    print_success(f"Results saved to: {filename}")

    if working:
        working_file = results_dir / f"Master_SNI_Scanner_working_{timestamp}.txt"
        with open(working_file, 'w', encoding='utf-8') as f:
            for w in working:
                f.write(f"{w['link']}\n")
        print_success(f"Working links saved to: {working_file}")

    return filename


def print_results_table(results, server_ip, port, transport):
    """Print results in a formatted table sorted by latency"""
    working = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]

    print(f"\n{GREEN}{BOLD}{'=' * 80}{RESET}")
    print(f"{GREEN}{BOLD}TEST RESULTS SUMMARY{RESET}")
    print(f"{GREEN}{BOLD}{'=' * 80}{RESET}\n")

    stats_headers = ["Metric", "Value"]
    stats_rows = [
        ["Server", f"{server_ip}:{port}"],
        ["Transport", transport.upper()],
        ["Total SNIs Tested", str(len(results))],
        ["Working SNIs", f"{GREEN}{len(working)}{RESET}" if working else f"{RED}0{RESET}"],
        ["Success Rate", f"{len(working) / len(results) * 100:.1f}%"]
    ]
    print_table(stats_headers, stats_rows)

    if working:
        print(f"\n{GREEN}{BOLD}WORKING SNIs (sorted by latency):{RESET}\n")
        working_headers = ["#", "SNI Domain", "Latency (ms)", "Status"]
        working_rows = []
        # Feature 3: Sort by latency (low to high)
        working_sorted = sorted(working, key=lambda x: x['latency'])
        for i, w in enumerate(working_sorted, 1):
            working_rows.append([i, w['sni'], w['latency'], f"{GREEN}✓ WORKING{RESET}"])
        print_table(working_headers, working_rows)
    else:
        # Feature 1: No working SNIs found - show formatted message
        print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
        print(f"{YELLOW}{BOLD}  No working SNIs found!{RESET}")
        print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
        print(f"{CYAN}  Suggestions:{RESET}")
        print(f"  • Try a different transport protocol")
        print(f"  • Try different SNI domains")
        print(f"  • Check server firewall")
        print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")

    if failed and len(failed) <= 20:
        print(f"\n{RED}{BOLD}FAILED SNIs:{RESET}\n")
        failed_headers = ["#", "SNI Domain", "Status"]
        failed_rows = []
        for i, f_item in enumerate(failed, 1):
            failed_rows.append([i, f_item['sni'], f"{RED}✗ FAILED{RESET}"])
        print_table(failed_headers, failed_rows)
    elif failed:
        print_warning(f"\n{len(failed)} SNIs failed (not shown individually)")


# ============================================================================
# SECTION 10: CONFIGURATION SUMMARY - Review and confirm settings
# ============================================================================

def show_config_summary(transport, workers, batch_size, sni_method, sni_count, server_ip):
    """Show configuration summary table and ask for confirmation"""
    print(f"\n{YELLOW}{BOLD}{'=' * 80}{RESET}")
    print(f"{YELLOW}{BOLD}CONFIGURATION SUMMARY - PLEASE REVIEW{RESET}")
    print(f"{YELLOW}{BOLD}{'=' * 80}{RESET}\n")

    method_names = {
        '1': 'Manual Input',
        '2': 'Load from File',
        '3': 'Auto Scan',
        '4': 'Default List'
    }
    method_readable = method_names.get(sni_method, sni_method)

    headers = ["Setting", "Value"]
    rows = [
        ["Server IP", server_ip],
        ["Transport Protocol", transport.upper()],
        ["Parallel Workers", str(workers)],
        ["Batch Size", str(batch_size)],
        ["SNI Input Method", method_readable],
        ["Total SNIs to Test", str(sni_count)]
    ]
    print_table(headers, rows)

    print(f"\n{YELLOW}{BOLD}{'=' * 80}{RESET}")
    print(f"{CYAN}Options:{RESET}")
    print(f"  {GREEN}c{RESET} - Confirm and continue")
    print(f"  {YELLOW}e{RESET} - Edit configuration")
    print(f"  {RED}q{RESET} - Quit")
    print(f"{YELLOW}{BOLD}{'=' * 80}{RESET}")

    while True:
        choice = input(f"\n{WHITE}Select option [c/e/q]: {RESET}").strip().lower()
        if choice == 'c':
            return True
        elif choice == 'e':
            return False
        elif choice == 'q':
            print_warning("Exiting...")
            sys.exit(0)
        else:
            print_warning("Invalid option. Please enter c, e, or q")


# ============================================================================
# SECTION 11: CLEANUP & SIGNAL HANDLER - Final cleanup and interrupt handling
# ============================================================================

# Global variables for partial results
_test_results_global = []
_test_completed = False
_server_ip_global = ""
_server_port_global = 0
_transport_global = ""


def cleanup():
    """Final cleanup"""
    print_info("Cleaning up Xray processes...")
    kill_all_xray()
    print_success("Cleanup complete")


def save_partial_results():
    """Save partial results to results folder - same format as complete scan"""
    global _test_results_global, _server_ip_global, _server_port_global, _transport_global

    if not _test_results_global:
        return

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = results_dir / f"Master_SNI_Scanner_{timestamp}.txt"

    working = [r for r in _test_results_global if r['success']]

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"MASTER SNI SCANNER v2.1.0 - TEST RESULTS (INTERRUPTED)\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Server: {_server_ip_global}:{_server_port_global}\n")
        f.write(f"Transport: {_transport_global.upper()}\n")
        f.write(f"Total SNIs Tested: {len(_test_results_global)}\n")
        f.write(f"Working SNIs: {len(working)}\n")
        f.write("=" * 100 + "\n\n")

        if working:
            f.write("WORKING SNIs:\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'#':<5} {'SNI Domain':<40} {'Latency (ms)':<15} {'Status':<10}\n")
            f.write("-" * 100 + "\n")
            working_sorted = sorted(working, key=lambda x: x['latency'])
            for i, w in enumerate(working_sorted, 1):
                f.write(f"{i:<5} {w['sni']:<40} {w['latency']:<15} WORKING\n")
            f.write("-" * 100 + "\n\n")

            f.write("WORKING CONFIGURATION LINKS:\n")
            f.write("=" * 100 + "\n\n")
            for w in working_sorted:
                f.write(f"SNI: {w['sni']}\n")
                f.write(f"Link: {w['link']}\n")
                f.write("-" * 100 + "\n")
        else:
            f.write("No working SNIs found.\n")

        # Also save working links separately
        if working:
            working_file = results_dir / f"Master_SNI_Scanner_working_{timestamp}.txt"
            with open(working_file, 'w', encoding='utf-8') as wf:
                for w in working:
                    wf.write(f"{w['link']}\n")
            print_success(f"Working links saved to: {working_file}")

    print_success(f"Results saved to: {filename}")


def signal_handler(signum, frame):
    """Handle Ctrl+C interrupt gracefully - show and save partial results before exit"""
    global _test_results_global, _test_completed

    print_info("\n\nInterrupted by user")

    # If test was not completed and we have partial results
    if not _test_completed and _test_results_global:
        print_info(f"Displaying partial results ({len(_test_results_global)} SNIs tested)...")
        print_results_table(_test_results_global, _server_ip_global, _server_port_global, _transport_global)
        save_partial_results()
    elif not _test_completed and not _test_results_global:
        print_info("No SNIs have been tested yet.")

    cleanup()
    sys.exit(0)


# ============================================================================
# SECTION 12: MAIN - Main execution flow
# ============================================================================

def main():
    """Main client execution flow"""
    global _test_results_global, _test_completed, _server_ip_global, _server_port_global, _transport_global

    print_banner()

    parser = argparse.ArgumentParser(description='Master SNI Scanner v2.1.0 - Client')
    parser.add_argument('--server', help='Server IP address')
    parser.add_argument('--api-port', type=int, default=None,
                        help='API port for server connection (default: 8080)')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    install_requirements()

    config_confirmed = False
    transport = None
    max_workers = None
    batch_size = None
    sni_method = None
    server_ip = None
    sni_list = None
    api_port = 8080
    first_run = True

    while not config_confirmed:
        # ============================================================
        # STEP 1: Get Server IP
        # ============================================================
        if args.server and first_run:
            server_ip = args.server
            print_success(f"Server IP: {server_ip} (from command line)")
        else:
            server_ip = input(f"\n{CYAN}Enter server IP address: {RESET}").strip()

        if not server_ip:
            print_error("Server IP required")
            return

        # ============================================================
        # STEP 2: Get API Port
        # ============================================================
        if args.api_port is not None and first_run:
            api_port = args.api_port
            print_success(f"API Port: {api_port} (from command line)")
        else:
            api_port_input = input(f"{CYAN}Enter API port (default 8080): {RESET}").strip()
            api_port = int(api_port_input) if api_port_input.isdigit() else 8080
            print_success(f"API Port: {api_port}")

        # After first run, always ask user for input (editing mode)
        first_run = False

        # ============================================================
        # STEP 3: Health Check - Connect to server
        # ============================================================
        print_info(f"Connecting to server {server_ip}:{api_port}...")
        try:
            response = requests.get(f'http://{server_ip}:{api_port}/health', timeout=10)
            if response.status_code != 200:
                print_error("Server health check failed")
                return
            print_success(f"Connected to server")
        except Exception as e:
            print_error(f"Cannot reach server at {server_ip}:{api_port} - {e}")
            return

        # ============================================================
        # STEP 4: Select Transport Protocol
        # ============================================================
        transport = select_transport()

        # ============================================================
        # STEP 5: Select Number of Parallel Workers
        # ============================================================
        max_workers = select_workers()

        # ============================================================
        # STEP 6: Select Batch Size
        # ============================================================
        batch_size = select_batch_size()

        # ============================================================
        # STEP 7: Select SNI Input Method
        # ============================================================
        sni_method = show_sni_method_menu()
        sni_list = get_sni_list(server_ip, sni_method)

        if not sni_list:
            print_error("No SNI selected")
            return

        # ============================================================
        # STEP 8: Show Summary and Confirm
        # ============================================================
        config_confirmed = show_config_summary(
            transport, max_workers, batch_size, sni_method, len(sni_list), server_ip
        )

        if not config_confirmed:
            print_info("\n" + "=" * 50)
            print_info("Editing configuration. Please re-enter your settings.")
            print_info("=" * 50 + "\n")
            first_run = False

    # Store global values for partial save
    _server_ip_global = server_ip
    _server_port_global = api_port
    _transport_global = transport

    # ============================================================
    # START TESTING
    # ============================================================
    print_info(f"\nTotal SNIs to test: {len(sni_list)}")
    print_info(f"Batch size: {batch_size}")
    print_info(f"Parallel workers: {max_workers}")
    print_info(f"API Port: {api_port}")

    print_info("\nSending configuration to server...")
    config = send_config_to_server(server_ip, sni_list, transport, batch_size, api_port)

    if not config:
        print_error("Failed to configure server")
        return

    print_success(f"Server configured")
    print_info(f"  Server: {config['server_ip']}:{config['port']}")
    print_info(f"  Transport: {config['transport']}")
    print_info(f"  UUID: {config['server_uuid'][:20]}...")
    print_info(f"  Total batches: {config['total_batches']}")

    all_results = []
    batches = config['batches']
    _test_results_global = []

    try:
        for batch_idx, batch in enumerate(batches):
            print(f"\n{YELLOW}{BOLD}{'=' * 60}{RESET}")
            print(f"{YELLOW}{BOLD}Processing Batch {batch_idx + 1}/{len(batches)}{RESET}")
            print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
            print_info(f"SNIs in this batch: {len(batch)}")

            print_info("Updating server config for this batch...")
            if not apply_server_batch(server_ip, batch, transport, batch_idx, len(batches), api_port):
                print_error(f"Failed to apply batch {batch_idx + 1}")
                continue

            print_success(f"Server ready for batch {batch_idx + 1}")
            print_info("Waiting for server to stabilize...")
            time.sleep(3)

            print_info(f"\nTesting {len(batch)} SNIs with {max_workers} parallel workers...\n")
            batch_results = test_batch_parallel(
                batch, config['server_ip'], config['port'], config['public_key'],
                config['short_id'], config['server_uuid'], transport, max_workers
            )

            all_results.extend(batch_results)

            working_in_batch = sum(1 for r in batch_results if r['success'])
            print_info(f"\nBatch {batch_idx + 1} complete: {working_in_batch}/{len(batch)} working")

    except KeyboardInterrupt:
        raise

    _test_completed = True

    # Print and save results
    print_results_table(all_results, config['server_ip'], config['port'], transport)
    save_results_table(all_results, config['server_ip'], config['port'], transport)

    cleanup()

    print(f"\n{GREEN}{BOLD}{'=' * 80}{RESET}")
    print(f"{GREEN}{BOLD}MASTER SNI SCANNER v2.1.0 - COMPLETED{RESET}")
    print(f"{GREEN}{BOLD}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    main()