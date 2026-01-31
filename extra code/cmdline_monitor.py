# Author: Jack Lidster
# Date: 2026-01-27
# Description: Monitors what apps or files open the command line and reports back
# what it is, what it's doing, and when it was installed.

import psutil
import os
import time
import hashlib
import subprocess
import json
import struct
from datetime import datetime

# Optional: for web lookups
try:
    import urllib.request
    import urllib.parse
    import ssl
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Optional: for web lookups
try:
    import urllib.request
    import urllib.parse
    import ssl
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

# Command line processes to monitor
CMDLINE_PROCESSES = {
    'cmd.exe', 'powershell.exe', 'pwsh.exe', 'windowsterminal.exe',
    'conhost.exe', 'wt.exe', 'bash.exe', 'wsl.exe'
}

# Suspicious file locations (commonly used by malware)
SUSPICIOUS_LOCATIONS = [
    os.path.expanduser('~\\AppData\\Local\\Temp'),
    os.path.expanduser('~\\AppData\\Roaming\\Temp'),
    'C:\\Windows\\Temp',
    'C:\\Temp',
    os.path.expanduser('~\\Downloads'),
    'C:\\ProgramData',
]

# Suspicious file extensions often used by malware
SUSPICIOUS_EXTENSIONS = {
    '.scr', '.pif', '.bat', '.cmd', '.vbs', '.vbe', '.js', '.jse',
    '.ws', '.wsf', '.wsc', '.wsh', '.ps1', '.ps1xml', '.ps2', '.ps2xml',
    '.psc1', '.psc2', '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml',
    '.msh2xml', '.scf', '.lnk', '.inf', '.reg', '.hta'
}

# Known malicious process names (common malware names)
KNOWN_MALICIOUS_NAMES = {
    'cryptolocker', 'wannacry', 'petya', 'notpetya', 'locky', 'cerber',
    'teslacrypt', 'gandcrab', 'ryuk', 'sodinokibi', 'revil', 'darkside',
    'conti', 'lockbit', 'blackcat', 'maze', 'egregor', 'doppelpaymer',
    'mimikatz', 'cobaltstrike', 'metasploit', 'meterpreter'
}

def get_file_hash(file_path):
    """Calculate MD5 and SHA256 hash of a file."""
    try:
        if file_path and os.path.exists(file_path):
            md5_hash = hashlib.md5()
            sha256_hash = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    md5_hash.update(chunk)
                    sha256_hash.update(chunk)
            
            return {
                'md5': md5_hash.hexdigest(),
                'sha256': sha256_hash.hexdigest()
            }
    except (PermissionError, FileNotFoundError, OSError):
        pass
    return None

def check_digital_signature(file_path):
    """Check if a file has a valid digital signature (Windows only)."""
    try:
        if file_path and os.path.exists(file_path):
            # Use PowerShell to check digital signature
            result = subprocess.run(
                ['powershell', '-Command', f'(Get-AuthenticodeSignature "{file_path}").Status'],
                capture_output=True, text=True, timeout=10
            )
            status = result.stdout.strip()
            return {
                'signed': status == 'Valid',
                'status': status
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return {'signed': False, 'status': 'Unknown'}

def check_if_malicious(file_path, process_name=""):
    """
    Check if a file might be malicious based on multiple indicators.
    Returns a dict with risk assessment.
    """
    result = {
        'file_path': file_path,
        'risk_level': 'LOW',  # LOW, MEDIUM, HIGH, CRITICAL
        'risk_score': 0,
        'warnings': [],
        'is_suspicious': False,
        'hash': None,
        'signature': None
    }
    
    if not file_path or not os.path.exists(file_path):
        result['warnings'].append("File path invalid or file does not exist")
        return result
    
    file_name = os.path.basename(file_path).lower()
    file_ext = os.path.splitext(file_path)[1].lower()
    file_dir = os.path.dirname(file_path).lower()
    
    # Check 1: Suspicious location
    for sus_loc in SUSPICIOUS_LOCATIONS:
        if sus_loc.lower() in file_dir:
            result['risk_score'] += 15
            result['warnings'].append(f"⚠️ Located in suspicious directory: {sus_loc}")
            break
    
    # Check 2: Suspicious extension
    if file_ext in SUSPICIOUS_EXTENSIONS:
        result['risk_score'] += 25
        result['warnings'].append(f"⚠️ Suspicious file extension: {file_ext}")
    
    # Check 3: Known malicious names
    for mal_name in KNOWN_MALICIOUS_NAMES:
        if mal_name in file_name or mal_name in process_name.lower():
            result['risk_score'] += 50
            result['warnings'].append(f"🔴 Matches known malware name: {mal_name}")
    
    # Check 4: Hidden file attribute
    try:
        import stat
        file_stat = os.stat(file_path)
        if file_stat.st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN:
            result['risk_score'] += 10
            result['warnings'].append("⚠️ File is hidden")
    except:
        pass
    
    # Check 5: Recently created (within last hour) and running from temp
    try:
        create_time = os.path.getctime(file_path)
        age_hours = (time.time() - create_time) / 3600
        if age_hours < 1 and any(loc.lower() in file_dir for loc in SUSPICIOUS_LOCATIONS):
            result['risk_score'] += 20
            result['warnings'].append(f"⚠️ Recently created ({age_hours:.1f} hours ago) in suspicious location")
    except:
        pass
    
    # Check 6: Digital signature
    sig_check = check_digital_signature(file_path)
    result['signature'] = sig_check
    if not sig_check['signed']:
        if sig_check['status'] == 'NotSigned':
            result['risk_score'] += 15
            result['warnings'].append("⚠️ File is not digitally signed")
        elif sig_check['status'] in ['HashMismatch', 'Invalid']:
            result['risk_score'] += 40
            result['warnings'].append("🔴 Digital signature is INVALID or TAMPERED")
    
    # Check 7: Get file hash for potential lookup
    result['hash'] = get_file_hash(file_path)
    
    # Check 8: Suspicious naming patterns
    suspicious_patterns = ['temp', 'tmp', 'update', 'patch', 'crack', 'keygen', 'activator']
    for pattern in suspicious_patterns:
        if pattern in file_name and file_ext in ['.exe', '.dll', '.scr']:
            result['risk_score'] += 15
            result['warnings'].append(f"⚠️ Suspicious naming pattern: '{pattern}' in executable")
            break
    
    # Check 9: Double extension (e.g., document.pdf.exe)
    name_without_ext = os.path.splitext(file_name)[0]
    if '.' in name_without_ext and file_ext in ['.exe', '.scr', '.pif', '.bat', '.cmd']:
        result['risk_score'] += 30
        result['warnings'].append("🔴 Double extension detected (common malware trick)")
    
    # Check 10: Very long filename (sometimes used to hide extension)
    if len(file_name) > 100:
        result['risk_score'] += 10
        result['warnings'].append("⚠️ Unusually long filename")
    
    # Determine risk level
    if result['risk_score'] >= 50:
        result['risk_level'] = 'CRITICAL'
        result['is_suspicious'] = True
    elif result['risk_score'] >= 35:
        result['risk_level'] = 'HIGH'
        result['is_suspicious'] = True
    elif result['risk_score'] >= 20:
        result['risk_level'] = 'MEDIUM'
        result['is_suspicious'] = True
    else:
        result['risk_level'] = 'LOW'
    
    return result

def display_malware_check(check_result):
    """Display the malware check results."""
    risk_colors = {
        'LOW': '🟢',
        'MEDIUM': '🟡',
        'HIGH': '🟠',
        'CRITICAL': '🔴'
    }
    
    print(f"\n  {'─' * 50}")
    print(f"  MALWARE CHECK RESULT")
    print(f"  {'─' * 50}")
    print(f"  File: {check_result['file_path']}")
    print(f"  Risk Level: {risk_colors.get(check_result['risk_level'], '⚪')} {check_result['risk_level']} (Score: {check_result['risk_score']})")
    
    if check_result['hash']:
        print(f"  MD5: {check_result['hash']['md5']}")
        print(f"  SHA256: {check_result['hash']['sha256'][:32]}...")
    
    if check_result['signature']:
        sig_icon = '✅' if check_result['signature']['signed'] else '❌'
        print(f"  Digital Signature: {sig_icon} {check_result['signature']['status']}")
    
    if check_result['warnings']:
        print(f"\n  Warnings ({len(check_result['warnings'])}):")
        for warning in check_result['warnings']:
            print(f"    {warning}")
    else:
        print(f"\n  ✅ No suspicious indicators found")
    
    print(f"  {'─' * 50}")
    
    # If risk score is above 20, perform deep scan
    if check_result['risk_score'] > 20:
        deep_scan_file(check_result['file_path'], check_result['hash'])

def get_pe_info(file_path):
    """Extract information from PE (Portable Executable) files."""
    pe_info = {
        'is_pe': False,
        'architecture': None,
        'subsystem': None,
        'compile_time': None,
        'imports': [],
        'sections': [],
        'is_packed': False,
        'suspicious_imports': []
    }
    
    try:
        with open(file_path, 'rb') as f:
            # Check DOS header
            dos_header = f.read(2)
            if dos_header != b'MZ':
                return pe_info
            
            pe_info['is_pe'] = True
            
            # Get PE header offset
            f.seek(60)
            pe_offset = struct.unpack('<I', f.read(4))[0]
            
            # Read PE signature
            f.seek(pe_offset)
            pe_sig = f.read(4)
            if pe_sig != b'PE\x00\x00':
                return pe_info
            
            # Read COFF header
            machine = struct.unpack('<H', f.read(2))[0]
            pe_info['architecture'] = '64-bit' if machine == 0x8664 else '32-bit' if machine == 0x14c else 'Unknown'
            
            num_sections = struct.unpack('<H', f.read(2))[0]
            timestamp = struct.unpack('<I', f.read(4))[0]
            pe_info['compile_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp > 0 else 'Unknown'
            
    except Exception as e:
        pass
    
    return pe_info

def get_file_metadata(file_path):
    """Get detailed file metadata using PowerShell."""
    metadata = {
        'description': None,
        'company': None,
        'product': None,
        'version': None,
        'original_name': None,
        'copyright': None
    }
    
    try:
        ps_command = f'''
        $file = Get-Item "{file_path}"
        $shell = New-Object -ComObject Shell.Application
        $folder = $shell.Namespace($file.DirectoryName)
        $item = $folder.ParseName($file.Name)
        
        $versionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo("{file_path}")
        
        @{{
            Description = $versionInfo.FileDescription
            Company = $versionInfo.CompanyName
            Product = $versionInfo.ProductName
            Version = $versionInfo.FileVersion
            OriginalName = $versionInfo.OriginalFilename
            Copyright = $versionInfo.LegalCopyright
        }} | ConvertTo-Json
        '''
        
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=15
        )
        
        if result.stdout.strip():
            data = json.loads(result.stdout.strip())
            metadata['description'] = data.get('Description')
            metadata['company'] = data.get('Company')
            metadata['product'] = data.get('Product')
            metadata['version'] = data.get('Version')
            metadata['original_name'] = data.get('OriginalName')
            metadata['copyright'] = data.get('Copyright')
            
    except Exception:
        pass
    
    return metadata

def lookup_hash_online(file_hash, hash_type='sha256'):
    """Look up file hash on online malware databases."""
    results = {
        'found': False,
        'malicious': False,
        'source': None,
        'details': None,
        'error': None
    }
    
    if not WEB_AVAILABLE:
        results['error'] = "Web lookup not available"
        return results
    
    # Create SSL context that doesn't verify (for corporate networks)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Try multiple free hash lookup services
    services = [
        {
            'name': 'MalwareBazaar',
            'url': f'https://mb-api.abuse.ch/api/v1/',
            'method': 'POST',
            'data': {'query': 'get_info', 'hash': file_hash},
            'parse': lambda r: parse_malwarebazaar(r)
        },
        {
            'name': 'Maltiverse',
            'url': f'https://api.maltiverse.com/sample/{file_hash}',
            'method': 'GET',
            'data': None,
            'parse': lambda r: parse_maltiverse(r)
        }
    ]
    
    for service in services:
        try:
            if service['method'] == 'POST':
                data = urllib.parse.urlencode(service['data']).encode()
                req = urllib.request.Request(service['url'], data=data)
            else:
                req = urllib.request.Request(service['url'])
            
            req.add_header('User-Agent', 'SecurityScanner/1.0')
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                response_data = json.loads(response.read().decode())
                parsed = service['parse'](response_data)
                
                if parsed['found']:
                    results = parsed
                    results['source'] = service['name']
                    return results
                    
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue  # Not found, try next service
            results['error'] = f"{service['name']}: HTTP {e.code}"
        except urllib.error.URLError as e:
            results['error'] = f"{service['name']}: Connection failed"
        except json.JSONDecodeError:
            results['error'] = f"{service['name']}: Invalid response"
        except Exception as e:
            results['error'] = f"{service['name']}: {str(e)}"
    
    return results

def parse_malwarebazaar(data):
    """Parse MalwareBazaar API response."""
    result = {'found': False, 'malicious': False, 'details': None}
    
    if data.get('query_status') == 'ok' and data.get('data'):
        sample = data['data'][0]
        result['found'] = True
        result['malicious'] = True
        result['details'] = {
            'file_type': sample.get('file_type'),
            'signature': sample.get('signature'),
            'tags': sample.get('tags', []),
            'first_seen': sample.get('first_seen'),
            'intelligence': sample.get('intelligence', {})
        }
    
    return result

def parse_maltiverse(data):
    """Parse Maltiverse API response."""
    result = {'found': False, 'malicious': False, 'details': None}
    
    if data and data.get('sha256'):
        result['found'] = True
        classification = data.get('classification', 'unknown')
        result['malicious'] = classification in ['malicious', 'suspicious']
        result['details'] = {
            'classification': classification,
            'type': data.get('type'),
            'tags': data.get('tag', []),
            'filename': data.get('filename'),
            'creation_time': data.get('creation_time')
        }
    
    return result

def deep_scan_file(file_path, file_hash):
    """Perform a deep scan of a suspicious file."""
    print(f"\n  {'=' * 70}")
    print(f"  🔬 DEEP SCAN - Analyzing suspicious file...")
    print(f"  {'=' * 70}")
    print(f"  File: {file_path}")
    
    # Get PE information
    pe_info = get_pe_info(file_path)
    if pe_info['is_pe']:
        print(f"\n  📦 EXECUTABLE INFORMATION:")
        print(f"     Architecture: {pe_info['architecture']}")
        print(f"     Compile Time: {pe_info['compile_time']}")
    
    # Get file metadata
    metadata = get_file_metadata(file_path)
    if any(metadata.values()):
        print(f"\n  📋 FILE METADATA:")
        if metadata['description']:
            print(f"     Description: {metadata['description']}")
        if metadata['company']:
            print(f"     Company: {metadata['company']}")
        if metadata['product']:
            print(f"     Product: {metadata['product']}")
        if metadata['version']:
            print(f"     Version: {metadata['version']}")
        if metadata['original_name']:
            print(f"     Original Name: {metadata['original_name']}")
        if metadata['copyright']:
            print(f"     Copyright: {metadata['copyright']}")
    
    # Check online databases
    print(f"\n  🌐 ONLINE THREAT INTELLIGENCE LOOKUP:")
    
    if file_hash:
        sha256 = file_hash.get('sha256')
        if sha256:
            print(f"     Checking hash: {sha256[:16]}...")
            
            online_result = lookup_hash_online(sha256)
            
            if online_result.get('error'):
                print(f"     ⚠️ Lookup error: {online_result['error']}")
            elif online_result.get('found'):
                if online_result.get('malicious'):
                    print(f"     🔴 MALWARE DETECTED!")
                    print(f"     Source: {online_result['source']}")
                    
                    if online_result['details']:
                        details = online_result['details']
                        if details.get('signature'):
                            print(f"     Malware Family: {details['signature']}")
                        if details.get('file_type'):
                            print(f"     File Type: {details['file_type']}")
                        if details.get('tags'):
                            print(f"     Tags: {', '.join(details['tags'][:5])}")
                        if details.get('first_seen'):
                            print(f"     First Seen: {details['first_seen']}")
                        if details.get('classification'):
                            print(f"     Classification: {details['classification']}")
                else:
                    print(f"     🟡 File found in database but not classified as malicious")
                    print(f"     Source: {online_result['source']}")
            else:
                print(f"     ✅ Hash not found in malware databases (may still be unknown malware)")
        else:
            print(f"     ⚠️ Could not calculate file hash")
    else:
        print(f"     ⚠️ No hash available for lookup")
    
    # Additional checks
    print(f"\n  🔍 ADDITIONAL ANALYSIS:")
    
    # Check file size
    try:
        file_size = os.path.getsize(file_path)
        size_kb = file_size / 1024
        size_mb = size_kb / 1024
        if size_mb >= 1:
            print(f"     File Size: {size_mb:.2f} MB")
        else:
            print(f"     File Size: {size_kb:.2f} KB")
        
        # Very small executables can be suspicious
        if file_path.lower().endswith('.exe') and file_size < 10240:  # Less than 10KB
            print(f"     ⚠️ Unusually small executable")
    except:
        pass
    
    # Check for AutoRun entries
    print(f"\n     Checking for persistence mechanisms...")
    check_persistence(file_path)
    
    print(f"\n  {'=' * 70}")

def check_persistence(file_path):
    """Check if the file has any persistence mechanisms (auto-start)."""
    file_name = os.path.basename(file_path).lower()
    
    # Common autorun registry locations
    autorun_checks = [
        ('HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 'User Run'),
        ('HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 'System Run'),
        ('HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce', 'User RunOnce'),
    ]
    
    found_persistence = False
    
    for reg_path, description in autorun_checks:
        try:
            result = subprocess.run(
                ['powershell', '-Command', f'Get-ItemProperty -Path "{reg_path}" -ErrorAction SilentlyContinue | Format-List'],
                capture_output=True, text=True, timeout=5
            )
            
            if file_name in result.stdout.lower() or file_path.lower() in result.stdout.lower():
                print(f"     🔴 Found in {description} registry!")
                found_persistence = True
                
        except:
            pass
    
    # Check scheduled tasks
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-ScheduledTask | Where-Object {$_.State -ne "Disabled"} | Select-Object TaskName, TaskPath | ConvertTo-Json'],
            capture_output=True, text=True, timeout=10
        )
        
        if file_name in result.stdout.lower():
            print(f"     🔴 Found in Scheduled Tasks!")
            found_persistence = True
            
    except:
        pass
    
    if not found_persistence:
        print(f"     ✅ No persistence mechanisms detected")

def get_file_creation_time(file_path):
    """Get when a file was created/installed."""
    try:
        if file_path and os.path.exists(file_path):
            timestamp = os.path.getctime(file_path)
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return "Unknown"

def get_process_cmdline(proc):
    """Get the command line arguments of a process."""
    try:
        cmdline = proc.cmdline()
        if cmdline:
            return ' '.join(cmdline)
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return "Access Denied"

def get_parent_info(proc):
    """Get information about the parent process."""
    try:
        parent = proc.parent()
        if parent:
            return {
                'name': parent.name(),
                'pid': parent.pid,
                'exe': parent.exe() if parent.exe() else "Unknown",
                'cmdline': get_process_cmdline(parent)
            }
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return None

def scan_cmdline_openers():
    """Scan for all processes that have opened command line processes."""
    cmdline_instances = []
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
        try:
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            
            # Check if this is a command line process
            if proc_name in CMDLINE_PROCESSES:
                proc_exe = proc.info['exe'] or ''
                create_time = datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                
                # Get parent process info (what opened the command line)
                parent_info = get_parent_info(proc)
                
                # Get the command being run
                cmdline = get_process_cmdline(proc)
                
                cmdline_instances.append({
                    'cmdline_process': proc_name,
                    'cmdline_pid': proc.info['pid'],
                    'cmdline_started': create_time,
                    'command_running': cmdline,
                    'parent': parent_info,
                    'parent_installed': get_file_creation_time(parent_info['exe']) if parent_info else "Unknown",
                    'malware_check': check_if_malicious(parent_info['exe'], parent_info['name']) if parent_info else None
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return cmdline_instances

def display_results(instances):
    """Display the results in a formatted table."""
    print("\n" + "=" * 100)
    print("  COMMAND LINE MONITOR - Apps/Files Opening Command Line")
    print("=" * 100)
    print(f"  Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total Command Line Instances Found: {len(instances)}")
    print("=" * 100)
    
    if not instances:
        print("\n  No command line processes currently running.")
        return
    
    for i, instance in enumerate(instances, 1):
        print(f"\n{'─' * 100}")
        print(f"  [{i}] COMMAND LINE INSTANCE")
        print(f"{'─' * 100}")
        print(f"  Terminal Type     : {instance['cmdline_process'].upper()}")
        print(f"  Terminal PID      : {instance['cmdline_pid']}")
        print(f"  Started At        : {instance['cmdline_started']}")
        print(f"  Command Running   : {instance['command_running'][:80]}..." if len(instance['command_running']) > 80 else f"  Command Running   : {instance['command_running']}")
        
        if instance['parent']:
            print(f"\n  OPENED BY:")
            print(f"  ├── Application   : {instance['parent']['name']}")
            print(f"  ├── Parent PID    : {instance['parent']['pid']}")
            print(f"  ├── Executable    : {instance['parent']['exe']}")
            print(f"  ├── Installed On  : {instance['parent_installed']}")
            print(f"  └── Parent Command: {instance['parent']['cmdline'][:70]}..." if len(instance['parent']['cmdline']) > 70 else f"  └── Parent Command: {instance['parent']['cmdline']}")
            
            # Display malware check results
            if instance.get('malware_check'):
                display_malware_check(instance['malware_check'])
        else:
            print(f"\n  OPENED BY: System/Unknown (no parent process found)")
    
    print(f"\n{'=' * 100}")

def continuous_monitor(interval=10):
    """Continuously monitor for new command line instances."""
    print("=" * 100)
    print("  🔍 CONTINUOUS COMMAND LINE MONITOR")
    print(f"     Scanning every {interval} seconds...")
    print("     Press Ctrl+C to stop")
    print("=" * 100)
    
    seen_pids = set()
    
    try:
        while True:
            instances = scan_cmdline_openers()
            
            # Check for new instances
            new_instances = [i for i in instances if i['cmdline_pid'] not in seen_pids]
            
            if new_instances:
                print(f"\n⚡ NEW COMMAND LINE ACTIVITY DETECTED at {datetime.now().strftime('%H:%M:%S')}")
                display_results(new_instances)
                
                # Add to seen
                for inst in new_instances:
                    seen_pids.add(inst['cmdline_pid'])
            
            # Clean up closed processes
            current_pids = {i['cmdline_pid'] for i in instances}
            closed_pids = seen_pids - current_pids
            if closed_pids:
                print(f"\n🔴 Command line processes closed: {closed_pids}")
                seen_pids -= closed_pids
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor stopped by user.")

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("       COMMAND LINE OPENER TRACKER")
    print("       Tracks what apps/files open the command line")
    print("=" * 100)
    print("\nOptions:")
    print("  1. Single scan - List all current command line instances")
    print("  2. Continuous monitoring - Watch for new command line activity")
    print("  3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        instances = scan_cmdline_openers()
        display_results(instances)
    elif choice == '2':
        interval = input("Enter scan interval in seconds (default 10): ").strip()
        interval = int(interval) if interval.isdigit() else 10
        continuous_monitor(interval)
    else:
        print("Exiting...")
