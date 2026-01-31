# Author: Jack Lidster
# Date: 2026-01-27
# Description: Scans the computer for any non-browser processes that are scanning this computer's files 
# and sending them to an external server. If any are found, it will terminate the process and alert the user.

import psutil
import socket
import time
import os
from datetime import datetime

# Known safe browsers (add more as needed)
KNOWN_BROWSERS = {
    'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 'brave.exe',
    'safari.exe', 'iexplore.exe', 'vivaldi.exe', 'chromium.exe',
    'chrome', 'firefox', 'msedge', 'opera', 'brave', 'safari', 'vivaldi'
}

# Known safe system processes
SAFE_PROCESSES = {
    'svchost.exe', 'system', 'wininit.exe', 'services.exe', 'lsass.exe',
    'csrss.exe', 'smss.exe', 'explorer.exe', 'taskhostw.exe', 'runtimebroker.exe',
    'searchindexer.exe', 'spoolsv.exe', 'dwm.exe', 'sihost.exe', 'ctfmon.exe',
    'code.exe', 'python.exe', 'pythonw.exe', 'windowsterminal.exe', 'cmd.exe',
    'powershell.exe', 'conhost.exe', 'winlogon.exe', 'fontdrvhost.exe',
    # Apple programs
    'itunes.exe', 'applemobiledeviceservice.exe', 'iphonetunnelservice.exe',
    'appleiphonecalculatornotificationservice.exe', 'apdproxy.exe',
    'mobilesync.exe', 'mdnsresponder.exe', 'softwareupdate.exe',
    'apsdaemon.exe', 'distnoted.exe', 'iclouddrive.exe', 'icloud.exe',
    'icloudservices.exe', 'icloudphotos.exe', 'applephotostreams.exe',
    'coreaudiod.exe', 'airplayxpchelper.exe', 'applemusic.exe', 'appletv.exe'
}

# Suspicious file access patterns (directories that shouldn't be scanned by unknown processes)
SENSITIVE_DIRECTORIES = [
    os.path.expanduser('~\\Documents'),
    os.path.expanduser('~\\Desktop'),
    os.path.expanduser('~\\Downloads'),
    os.path.expanduser('~\\Pictures'),
    os.path.expanduser('~\\AppData'),
]

def is_external_ip(ip):
    """Check if an IP address is external (not local/private)."""
    try:
        if ip.startswith('127.') or ip.startswith('0.'):
            return False
        if ip.startswith('192.168.') or ip.startswith('10.'):
            return False
        if ip.startswith('172.'):
            second_octet = int(ip.split('.')[1])
            if 16 <= second_octet <= 31:
                return False
        if ip == '::1' or ip.startswith('fe80:') or ip.startswith('fd'):
            return False
        return True
    except:
        return False

def get_process_connections():
    """Get all processes with active network connections."""
    suspicious_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            proc_exe = proc.info['exe'] or ''
            
            # Skip browsers and known safe processes
            if proc_name in KNOWN_BROWSERS or proc_name in SAFE_PROCESSES:
                continue
            
            # Get network connections for this process
            connections = proc.net_connections(kind='inet')
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    if is_external_ip(remote_ip):
                        # Check if process is accessing sensitive files
                        open_files = []
                        try:
                            open_files = [f.path for f in proc.open_files()]
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass
                        
                        # Check if accessing sensitive directories
                        accessing_sensitive = any(
                            any(sens_dir.lower() in f.lower() for sens_dir in SENSITIVE_DIRECTORIES)
                            for f in open_files
                        )
                        
                        suspicious_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc_name,
                            'exe': proc_exe,
                            'remote_ip': remote_ip,
                            'remote_port': remote_port,
                            'open_files': open_files[:5],  # Limit to 5 files
                            'accessing_sensitive': accessing_sensitive
                        })
                        break  # One entry per process
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return suspicious_processes

def alert_user(process_info):
    """Alert the user about a suspicious process."""
    print("\n" + "=" * 60)
    print("⚠️  SUSPICIOUS PROCESS DETECTED!")
    print("=" * 60)
    print(f"Process Name: {process_info['name']}")
    print(f"PID: {process_info['pid']}")
    print(f"Executable: {process_info['exe']}")
    print(f"Connected to: {process_info['remote_ip']}:{process_info['remote_port']}")
    
    if process_info['open_files']:
        print(f"Open Files: ")
        for f in process_info['open_files']:
            print(f"  - {f}")
    
    if process_info['accessing_sensitive']:
        print("🔴 WARNING: This process is accessing sensitive directories!")
    
    print("=" * 60)

def terminate_process(pid, process_name):
    """Terminate a suspicious process after user confirmation."""
    try:
        response = input(f"\nDo you want to terminate '{process_name}' (PID: {pid})? (y/n): ").strip().lower()
        if response == 'y':
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            print(f"✅ Process '{process_name}' (PID: {pid}) has been terminated.")
            return True
        else:
            print(f"Process '{process_name}' was NOT terminated.")
            return False
    except psutil.NoSuchProcess:
        print(f"Process already terminated.")
        return True
    except psutil.AccessDenied:
        print(f"❌ Access denied. Try running as Administrator.")
        return False
    except Exception as e:
        print(f"❌ Error terminating process: {e}")
        return False

def scan_once():
    """Perform a single scan for suspicious processes."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scanning for suspicious processes...")
    
    suspicious = get_process_connections()
    
    if not suspicious:
        print("✅ No suspicious processes detected.")
        return
    
    for proc_info in suspicious:
        alert_user(proc_info)
        terminate_process(proc_info['pid'], proc_info['name'])

def continuous_monitor(interval=30):
    """Continuously monitor for suspicious processes."""
    print("=" * 60)
    print("🔒 SECURITY MONITOR STARTED")
    print(f"   Scanning every {interval} seconds...")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            scan_once()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n🛑 Security monitor stopped by user.")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("       SUSPICIOUS PROCESS SCANNER")
    print("=" * 60)
    print("\nOptions:")
    print("  1. Single scan")
    print("  2. Continuous monitoring")
    print("  3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        scan_once()
    elif choice == '2':
        interval = input("Enter scan interval in seconds (default 30): ").strip()
        interval = int(interval) if interval.isdigit() else 30
        continuous_monitor(interval)
    else:
        print("Exiting...")
