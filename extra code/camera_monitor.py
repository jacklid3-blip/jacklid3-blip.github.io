# Author: Jack Lidster
# Date: 2026-01-27
# Description: Checks if the camera is currently being used and shows what apps
# have accessed the camera in the last 7 days.

import subprocess
import json
import os
import re
from datetime import datetime, timedelta

def get_friendly_app_name(app_path):
    """Convert registry path or package name to a friendly app name."""
    if not app_path:
        return "Unknown"
    
    app_path = str(app_path)
    
    # For desktop apps (file paths)
    if '\\' in app_path or '/' in app_path:
        # Extract just the executable name
        exe_name = os.path.basename(app_path.replace('#', '\\'))
        
        # Common app name mappings
        app_mappings = {
            'chrome.exe': 'Google Chrome',
            'firefox.exe': 'Mozilla Firefox',
            'msedge.exe': 'Microsoft Edge',
            'opera.exe': 'Opera',
            'brave.exe': 'Brave Browser',
            'discord.exe': 'Discord',
            'slack.exe': 'Slack',
            'teams.exe': 'Microsoft Teams',
            'zoom.exe': 'Zoom',
            'skype.exe': 'Skype',
            'obs64.exe': 'OBS Studio',
            'obs32.exe': 'OBS Studio',
            'streamlabs obs.exe': 'Streamlabs OBS',
            'code.exe': 'Visual Studio Code',
            'devenv.exe': 'Visual Studio',
            'webex.exe': 'Cisco Webex',
            'facetime.exe': 'FaceTime',
            'snap camera.exe': 'Snap Camera',
            'manycam.exe': 'ManyCam',
            'logitech capture.exe': 'Logitech Capture',
            'xsplit.exe': 'XSplit',
            'whatsapp.exe': 'WhatsApp',
            'telegram.exe': 'Telegram',
            'signal.exe': 'Signal',
            'viber.exe': 'Viber',
            'facecam.exe': 'FaceCam',
            'youcam.exe': 'YouCam',
            'bandicam.exe': 'Bandicam',
            'camtasia.exe': 'Camtasia',
            'screencast-o-matic.exe': 'Screencast-O-Matic',
        }
        
        return app_mappings.get(exe_name.lower(), exe_name)
    
    # For Store apps (package names)
    # Microsoft.WindowsCamera_8wekyb3d8bbwe -> Windows Camera
    store_mappings = {
        'microsoft.windowscamera': 'Windows Camera',
        'microsoft.skypeapp': 'Skype',
        'microsoft.teams': 'Microsoft Teams',
        'microsoft.windows.photos': 'Windows Photos',
        'microsoft.zunevideo': 'Movies & TV',
        'microsoft.people': 'People',
        'discordapp': 'Discord',
        'zoom': 'Zoom',
        '5319275a.whatsappdesktop': 'WhatsApp',
        'telegramdesktop': 'Telegram',
    }
    
    # Extract base package name
    package_base = app_path.split('_')[0].lower()
    
    for key, name in store_mappings.items():
        if key in package_base:
            return name
    
    # Return cleaned up package name if no mapping found
    return package_base.replace('microsoft.', '').replace('.', ' ').title()

def get_camera_currently_in_use():
    """Check if the camera is currently being used and by which app."""
    print("\n" + "=" * 70)
    print("  📷 CURRENT CAMERA STATUS")
    print("=" * 70)
    
    # Method 1: Check registry for apps currently using camera
    ps_command = '''
    $cameraInUse = @()
    
    function Convert-FileTime($fileTime) {
        if ($fileTime -gt 0) {
            try {
                return [DateTime]::FromFileTime($fileTime).ToString("yyyy-MM-dd HH:mm:ss")
            } catch {
                return $null
            }
        }
        return $null
    }
    
    # Check NonPackaged apps (traditional desktop apps)
    $nonPackagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackagedApps"
    if (Test-Path $nonPackagedPath) {
        Get-ChildItem $nonPackagedPath | ForEach-Object {
            $appPath = $_.PSChildName -replace '#', '\\'
            $lastUsedStop = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStop -ErrorAction SilentlyContinue).LastUsedTimeStop
            $lastUsedStart = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStart -ErrorAction SilentlyContinue).LastUsedTimeStart
            
            # If LastUsedTimeStop is 0 but LastUsedTimeStart has a value, camera is in use
            if ($lastUsedStart -gt 0 -and $lastUsedStop -eq 0) {
                $startTime = Convert-FileTime $lastUsedStart
                $cameraInUse += @{
                    App = $appPath
                    Type = "Desktop App"
                    InUse = $true
                    StartedAt = $startTime
                }
            }
        }
    }
    
    # Check Packaged apps (Microsoft Store apps)
    $packagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    Get-ChildItem $packagedPath -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -ne "NonPackagedApps" } | ForEach-Object {
        $appName = $_.PSChildName
        $lastUsedStop = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStop -ErrorAction SilentlyContinue).LastUsedTimeStop
        $lastUsedStart = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStart -ErrorAction SilentlyContinue).LastUsedTimeStart
        
        if ($lastUsedStart -gt 0 -and $lastUsedStop -eq 0) {
            $startTime = Convert-FileTime $lastUsedStart
            $cameraInUse += @{
                App = $appName
                Type = "Store App"
                InUse = $true
                StartedAt = $startTime
            }
        }
    }
    
    $cameraInUse | ConvertTo-Json -Depth 3
    '''
    
    apps_in_use = []
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=30
        )
        
        if result.stdout.strip() and result.stdout.strip() != 'null':
            data = json.loads(result.stdout.strip())
            if not isinstance(data, list):
                data = [data]
            apps_in_use.extend(data)
    except:
        pass
    
    # Method 2: Check running processes that commonly use camera
    ps_process_check = '''
    $cameraProcesses = @()
    
    # Get processes that might be using camera by checking for camera-related handles
    $cameraApps = @(
        'zoom', 'teams', 'skype', 'discord', 'obs64', 'obs32', 'streamlabs',
        'chrome', 'firefox', 'msedge', 'brave', 'opera', 'slack', 'webex',
        'facetime', 'whatsapp', 'telegram', 'signal', 'viber', 'manycam',
        'snap camera', 'logitech capture', 'xsplit', 'bandicam', 'camtasia',
        'youcam', 'windowscamera', 'camera'
    )
    
    Get-Process | Where-Object { 
        $procName = $_.ProcessName.ToLower()
        $cameraApps | Where-Object { $procName -like "*$_*" }
    } | ForEach-Object {
        try {
            $proc = $_
            $path = $proc.Path
            
            # Check if process has camera device handle (approximation)
            $cameraProcesses += @{
                Name = $proc.ProcessName
                PID = $proc.Id
                Path = $path
                StartTime = if ($proc.StartTime) { $proc.StartTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "Unknown" }
                Memory = [math]::Round($proc.WorkingSet64 / 1MB, 2)
            }
        } catch {}
    }
    
    $cameraProcesses | ConvertTo-Json -Depth 3
    '''
    
    running_camera_apps = []
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_process_check],
            capture_output=True, text=True, timeout=30
        )
        
        if result.stdout.strip() and result.stdout.strip() != 'null':
            data = json.loads(result.stdout.strip())
            if not isinstance(data, list):
                data = [data]
            running_camera_apps = data
    except:
        pass
    
    # Display results
    if apps_in_use:
        print("\n  🔴 CAMERA IS CURRENTLY IN USE!")
        print("-" * 70)
        for app in apps_in_use:
            app_path = app.get('App', 'Unknown')
            friendly_name = get_friendly_app_name(app_path)
            app_type = app.get('Type', 'Unknown')
            started_at = app.get('StartedAt', 'Unknown')
            
            print(f"\n  📹 {friendly_name}")
            print(f"     Type: {app_type}")
            print(f"     Started Using Camera: {started_at}")
            print(f"     Full Path/Package: {app_path}")
        
        # Show additional process info if available
        if running_camera_apps:
            print("\n  📊 Related Running Processes:")
            print("-" * 70)
            for proc in running_camera_apps:
                print(f"     • {proc.get('Name', 'Unknown')} (PID: {proc.get('PID', '?')})")
                print(f"       Path: {proc.get('Path', 'Unknown')}")
                print(f"       Started: {proc.get('StartTime', 'Unknown')}")
                print(f"       Memory: {proc.get('Memory', '?')} MB")
        
        return True
    else:
        print("\n  ✅ Camera is NOT currently in use")
        
        if running_camera_apps:
            print("\n  ℹ️ Camera-capable apps currently running (not using camera):")
            for proc in running_camera_apps[:5]:  # Show top 5
                print(f"     • {proc.get('Name', 'Unknown')} (PID: {proc.get('PID', '?')})")
        
        return False

def get_camera_history_last_7_days():
    """Get all apps that have used the camera in the last 7 days."""
    print("\n" + "=" * 70)
    print("  📅 CAMERA ACCESS HISTORY (Last 7 Days)")
    print("=" * 70)
    
    all_apps = []
    
    # Method 1: Check Registry for camera access
    ps_registry_command = '''
    $results = @()
    $sevenDaysAgo = (Get-Date).AddDays(-7)
    
    function Convert-FileTime($fileTime) {
        if ($fileTime -gt 0) {
            try {
                return [DateTime]::FromFileTime($fileTime)
            } catch {
                return $null
            }
        }
        return $null
    }
    
    function Get-AppDetails($appPath) {
        $details = @{
            Publisher = $null
            Description = $null
            Version = $null
        }
        
        if ($appPath -and (Test-Path $appPath -ErrorAction SilentlyContinue)) {
            try {
                $fileInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($appPath)
                $details.Publisher = $fileInfo.CompanyName
                $details.Description = $fileInfo.FileDescription
                $details.Version = $fileInfo.FileVersion
            } catch {}
        }
        
        return $details
    }
    
    # Check NonPackaged apps (traditional desktop apps)
    $nonPackagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackagedApps"
    if (Test-Path $nonPackagedPath) {
        Get-ChildItem $nonPackagedPath | ForEach-Object {
            $appPath = $_.PSChildName -replace '#', '\\'
            $lastUsedStop = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStop -ErrorAction SilentlyContinue).LastUsedTimeStop
            $lastUsedStart = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStart -ErrorAction SilentlyContinue).LastUsedTimeStart
            
            $stopTime = Convert-FileTime $lastUsedStop
            $startTime = Convert-FileTime $lastUsedStart
            
            $lastAccess = $stopTime
            if ($startTime -gt $stopTime) { $lastAccess = $startTime }
            
            if ($lastAccess -and $lastAccess -gt $sevenDaysAgo) {
                $currentlyInUse = ($lastUsedStart -gt 0 -and $lastUsedStop -eq 0)
                $appDetails = Get-AppDetails $appPath
                
                $duration = $null
                if ($startTime -and $stopTime -and $stopTime -gt $startTime) {
                    $duration = ($stopTime - $startTime).TotalMinutes
                }
                
                $results += @{
                    App = $appPath
                    Type = "Desktop App"
                    LastAccess = $lastAccess.ToString("yyyy-MM-dd HH:mm:ss")
                    CurrentlyInUse = $currentlyInUse
                    Publisher = $appDetails.Publisher
                    Description = $appDetails.Description
                    Version = $appDetails.Version
                    LastSessionMinutes = if ($duration) { [math]::Round($duration, 1) } else { $null }
                    Source = "Registry"
                }
            }
        }
    }
    
    # Check Packaged apps (Microsoft Store apps)
    $packagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    Get-ChildItem $packagedPath -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -ne "NonPackagedApps" } | ForEach-Object {
        $appName = $_.PSChildName
        $lastUsedStop = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStop -ErrorAction SilentlyContinue).LastUsedTimeStop
        $lastUsedStart = (Get-ItemProperty $_.PSPath -Name LastUsedTimeStart -ErrorAction SilentlyContinue).LastUsedTimeStart
        
        $stopTime = Convert-FileTime $lastUsedStop
        $startTime = Convert-FileTime $lastUsedStart
        
        $lastAccess = $stopTime
        if ($startTime -gt $stopTime) { $lastAccess = $startTime }
        
        if ($lastAccess -and $lastAccess -gt $sevenDaysAgo) {
            $currentlyInUse = ($lastUsedStart -gt 0 -and $lastUsedStop -eq 0)
            
            $displayName = $null
            try {
                $package = Get-AppxPackage | Where-Object { $_.PackageFamilyName -like "$appName*" } | Select-Object -First 1
                if ($package) {
                    $displayName = $package.Name
                }
            } catch {}
            
            $duration = $null
            if ($startTime -and $stopTime -and $stopTime -gt $startTime) {
                $duration = ($stopTime - $startTime).TotalMinutes
            }
            
            $results += @{
                App = $appName
                Type = "Store App"
                LastAccess = $lastAccess.ToString("yyyy-MM-dd HH:mm:ss")
                CurrentlyInUse = $currentlyInUse
                Publisher = "Microsoft Store"
                Description = $displayName
                Version = $null
                LastSessionMinutes = if ($duration) { [math]::Round($duration, 1) } else { $null }
                Source = "Registry"
            }
        }
    }
    
    $results | ConvertTo-Json -Depth 3
    '''
    
    # Method 2: Check Windows Event Logs for camera access
    ps_eventlog_command = '''
    $results = @()
    $sevenDaysAgo = (Get-Date).AddDays(-7)
    
    # Check for camera/webcam related events in multiple logs
    $logNames = @(
        "Microsoft-Windows-WebcamExperience/Analytic",
        "Microsoft-Windows-Privacy-Auditing/Operational",
        "Microsoft-Windows-Kernel-Audit-API-Calls/Operational"
    )
    
    # Try to get events from Application log mentioning camera
    try {
        Get-WinEvent -FilterHashtable @{
            LogName = 'Application'
            StartTime = $sevenDaysAgo
        } -ErrorAction SilentlyContinue | Where-Object {
            $_.Message -match 'camera|webcam|video capture'
        } | Select-Object -First 50 | ForEach-Object {
            # Extract process info from message
            $results += @{
                Time = $_.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
                Message = $_.Message.Substring(0, [Math]::Min(200, $_.Message.Length))
                Source = $_.ProviderName
            }
        }
    } catch {}
    
    # Check Security log for object access (requires admin)
    try {
        Get-WinEvent -FilterHashtable @{
            LogName = 'Security'
            Id = 4663, 4656  # Object access events
            StartTime = $sevenDaysAgo
        } -ErrorAction SilentlyContinue | Where-Object {
            $_.Message -match 'camera|webcam|video'
        } | Select-Object -First 20 | ForEach-Object {
            $results += @{
                Time = $_.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
                Message = $_.Message.Substring(0, [Math]::Min(200, $_.Message.Length))
                Source = "Security Log"
            }
        }
    } catch {}
    
    $results | ConvertTo-Json -Depth 3
    '''
    
    # Method 3: Check for browser-based camera access (Discord web, Google Meet, etc.)
    ps_browser_command = '''
    $browserApps = @()
    $sevenDaysAgo = (Get-Date).AddDays(-7)
    
    # Check Chrome camera permissions
    $chromePath = "$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Preferences"
    if (Test-Path $chromePath) {
        try {
            $prefs = Get-Content $chromePath -Raw | ConvertFrom-Json
            $mediaEngagement = $prefs.profile.content_settings.exceptions.media_engagement
            $cameraPermissions = $prefs.profile.content_settings.exceptions.media_stream_camera
            
            if ($cameraPermissions) {
                $cameraPermissions.PSObject.Properties | ForEach-Object {
                    $site = $_.Name -replace ',.*$', ''
                    $setting = $_.Value.setting
                    if ($setting -eq 1) {  # 1 = allowed
                        $browserApps += @{
                            App = $site
                            Browser = "Google Chrome"
                            Type = "Website"
                            Permission = "Allowed"
                        }
                    }
                }
            }
        } catch {}
    }
    
    # Check Edge camera permissions
    $edgePath = "$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default\\Preferences"
    if (Test-Path $edgePath) {
        try {
            $prefs = Get-Content $edgePath -Raw | ConvertFrom-Json
            $cameraPermissions = $prefs.profile.content_settings.exceptions.media_stream_camera
            
            if ($cameraPermissions) {
                $cameraPermissions.PSObject.Properties | ForEach-Object {
                    $site = $_.Name -replace ',.*$', ''
                    $setting = $_.Value.setting
                    if ($setting -eq 1) {
                        $browserApps += @{
                            App = $site
                            Browser = "Microsoft Edge"
                            Type = "Website"
                            Permission = "Allowed"
                        }
                    }
                }
            }
        } catch {}
    }
    
    # Check Firefox camera permissions
    $firefoxProfiles = "$env:APPDATA\\Mozilla\\Firefox\\Profiles"
    if (Test-Path $firefoxProfiles) {
        Get-ChildItem $firefoxProfiles -Directory | ForEach-Object {
            $permissionsDb = Join-Path $_.FullName "permissions.sqlite"
            # Note: Would need SQLite to properly read this
        }
    }
    
    $browserApps | ConvertTo-Json -Depth 3
    '''
    
    # Method 4: Check for Discord, Teams, Zoom specific access
    ps_apps_command = '''
    $appHistory = @()
    $sevenDaysAgo = (Get-Date).AddDays(-7)
    
    # Discord - check if it has been running and using camera
    $discordPath = "$env:LOCALAPPDATA\\Discord"
    if (Test-Path $discordPath) {
        $discordExe = Get-ChildItem "$discordPath\\app-*\\Discord.exe" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($discordExe) {
            # Check Discord logs for camera usage
            $discordLogs = Get-ChildItem "$discordPath\\*.log" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $sevenDaysAgo }
            
            $appHistory += @{
                App = "Discord"
                Path = $discordExe.FullName
                Type = "Desktop App"
                LastModified = $discordExe.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                HasRecentLogs = ($discordLogs.Count -gt 0)
                Source = "App Directory"
            }
        }
    }
    
    # Microsoft Teams
    $teamsPath = "$env:LOCALAPPDATA\\Microsoft\\Teams"
    if (Test-Path $teamsPath) {
        $teamsExe = "$teamsPath\\current\\Teams.exe"
        if (Test-Path $teamsExe) {
            $appHistory += @{
                App = "Microsoft Teams"
                Path = $teamsExe
                Type = "Desktop App"
                LastModified = (Get-Item $teamsExe).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                Source = "App Directory"
            }
        }
    }
    
    # New Teams
    $newTeamsPath = "$env:LOCALAPPDATA\\Packages\\MSTeams_8wekyb3d8bbwe"
    if (Test-Path $newTeamsPath) {
        $appHistory += @{
            App = "Microsoft Teams (New)"
            Path = $newTeamsPath
            Type = "Store App"
            Source = "App Directory"
        }
    }
    
    # Zoom
    $zoomPath = "$env:APPDATA\\Zoom"
    if (Test-Path $zoomPath) {
        $zoomLogs = Get-ChildItem "$zoomPath\\logs" -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $sevenDaysAgo }
        if ($zoomLogs) {
            $appHistory += @{
                App = "Zoom"
                Path = $zoomPath
                Type = "Desktop App"
                RecentActivity = $true
                LastLog = ($zoomLogs | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                Source = "App Logs"
            }
        }
    }
    
    # Google Chrome (for Google Meet)
    $chromePath = "$env:LOCALAPPDATA\\Google\\Chrome\\User Data"
    if (Test-Path $chromePath) {
        $appHistory += @{
            App = "Google Chrome (Meet, etc.)"
            Path = $chromePath
            Type = "Browser"
            Note = "Check browser permissions for websites"
            Source = "Browser"
        }
    }
    
    $appHistory | ConvertTo-Json -Depth 3
    '''
    
    try:
        # Run registry check
        result1 = subprocess.run(
            ['powershell', '-Command', ps_registry_command],
            capture_output=True, text=True, timeout=60
        )
        
        if result1.stdout.strip() and result1.stdout.strip() != 'null':
            data = json.loads(result1.stdout.strip())
            if not isinstance(data, list):
                data = [data]
            all_apps.extend(data)
    except:
        pass
    
    try:
        # Run browser check
        result2 = subprocess.run(
            ['powershell', '-Command', ps_browser_command],
            capture_output=True, text=True, timeout=30
        )
        
        browser_sites = []
        if result2.stdout.strip() and result2.stdout.strip() != 'null':
            data = json.loads(result2.stdout.strip())
            if not isinstance(data, list):
                data = [data]
            browser_sites = data
    except:
        browser_sites = []
    
    try:
        # Run app-specific check
        result3 = subprocess.run(
            ['powershell', '-Command', ps_apps_command],
            capture_output=True, text=True, timeout=30
        )
        
        specific_apps = []
        if result3.stdout.strip() and result3.stdout.strip() != 'null':
            data = json.loads(result3.stdout.strip())
            if not isinstance(data, list):
                data = [data]
            specific_apps = data
    except:
        specific_apps = []
    
    # Display results
    if all_apps:
        # Filter out generic Windows Camera if other specific apps are found
        specific_app_names = ['discord', 'teams', 'zoom', 'chrome', 'firefox', 'edge', 'skype', 'slack']
        has_specific_apps = any(
            any(name in str(app.get('App', '')).lower() for name in specific_app_names)
            for app in all_apps
        )
        
        # If we only have Windows Camera but browser sites show other apps, note this
        windows_camera_only = all(
            'windowscamera' in str(app.get('App', '')).lower() or 
            'microsoft.windows' in str(app.get('App', '')).lower()
            for app in all_apps
        )
        
        print(f"\n  Found {len(all_apps)} app(s) in registry:\n")
        print("-" * 70)
        
        for i, app in enumerate(all_apps, 1):
            app_path = app.get('App', 'Unknown')
            friendly_name = get_friendly_app_name(app_path)
            app_type = app.get('Type', 'Unknown')
            last_access = app.get('LastAccess', 'Unknown')
            in_use = app.get('CurrentlyInUse', False)
            publisher = app.get('Publisher') or 'Unknown'
            description = app.get('Description') or friendly_name
            version = app.get('Version')
            duration = app.get('LastSessionMinutes')
            source = app.get('Source', 'Registry')
            
            status_icon = "🔴 CURRENTLY IN USE" if in_use else ""
            
            # Add note if this is Windows Camera but likely used by another app
            proxy_note = ""
            if 'windowscamera' in str(app_path).lower() or 'microsoft.windowscamera' in str(app_path).lower():
                proxy_note = "\n      ⚠️ Note: This may be a proxy for another app (Discord, Meet, etc.)"
            
            print(f"\n  [{i}] {friendly_name} {status_icon}")
            print(f"      Description: {description}")
            print(f"      Publisher: {publisher}")
            if version:
                print(f"      Version: {version}")
            print(f"      Type: {app_type}")
            print(f"      Last Camera Access: {last_access}")
            if duration:
                if duration >= 60:
                    hours = int(duration // 60)
                    mins = int(duration % 60)
                    print(f"      Last Session Duration: {hours}h {mins}m")
                else:
                    print(f"      Last Session Duration: {duration:.1f} minutes")
            print(f"      Full Path/Package: {app_path}{proxy_note}")
    
    # Show browser sites with camera permission
    if browser_sites:
        print("\n" + "-" * 70)
        print("  🌐 WEBSITES WITH CAMERA PERMISSION (may have used camera):")
        print("-" * 70)
        
        for site in browser_sites:
            site_name = site.get('App', 'Unknown')
            browser = site.get('Browser', 'Unknown')
            
            # Identify common services
            service_name = site_name
            if 'discord' in site_name.lower():
                service_name = f"Discord ({site_name})"
            elif 'meet.google' in site_name.lower():
                service_name = f"Google Meet ({site_name})"
            elif 'teams.microsoft' in site_name.lower() or 'teams.live' in site_name.lower():
                service_name = f"Microsoft Teams ({site_name})"
            elif 'zoom' in site_name.lower():
                service_name = f"Zoom ({site_name})"
            elif 'skype' in site_name.lower():
                service_name = f"Skype ({site_name})"
            elif 'slack' in site_name.lower():
                service_name = f"Slack ({site_name})"
            elif 'webex' in site_name.lower():
                service_name = f"Cisco Webex ({site_name})"
            
            print(f"\n  • {service_name}")
            print(f"    Browser: {browser}")
            print(f"    Permission: ✅ Allowed")
    
    # Show specific apps detected
    if specific_apps:
        print("\n" + "-" * 70)
        print("  📱 CAMERA-CAPABLE APPS DETECTED ON SYSTEM:")
        print("-" * 70)
        
        for app in specific_apps:
            app_name = app.get('App', 'Unknown')
            app_type = app.get('Type', 'Unknown')
            last_log = app.get('LastLog')
            source = app.get('Source', '')
            note = app.get('Note', '')
            
            print(f"\n  • {app_name}")
            print(f"    Type: {app_type}")
            if last_log:
                print(f"    Recent Activity: {last_log}")
            if note:
                print(f"    Note: {note}")
    
    if not all_apps and not browser_sites and not specific_apps:
        print("\n  ✅ No camera access history found")
    
    return all_apps

def get_all_camera_permissions():
    """Get all apps that have permission to access the camera."""
    print("\n" + "=" * 70)
    print("  🔐 APPS WITH CAMERA PERMISSION")
    print("=" * 70)
    
    ps_command = '''
    $results = @()
    
    # Check NonPackaged apps
    $nonPackagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackagedApps"
    if (Test-Path $nonPackagedPath) {
        Get-ChildItem $nonPackagedPath | ForEach-Object {
            $appPath = $_.PSChildName -replace '#', '\\'
            $value = (Get-ItemProperty $_.PSPath -Name Value -ErrorAction SilentlyContinue).Value
            $results += @{
                App = $appPath
                Type = "Desktop App"
                Permission = $value
            }
        }
    }
    
    # Check Packaged apps
    $packagedPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    Get-ChildItem $packagedPath -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -ne "NonPackagedApps" } | ForEach-Object {
        $appName = $_.PSChildName
        $value = (Get-ItemProperty $_.PSPath -Name Value -ErrorAction SilentlyContinue).Value
        $results += @{
            App = $appName
            Type = "Store App"  
            Permission = $value
        }
    }
    
    $results | ConvertTo-Json -Depth 3
    '''
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=30
        )
        
        if result.stdout.strip() and result.stdout.strip() != 'null':
            apps = json.loads(result.stdout.strip())
            if not isinstance(apps, list):
                apps = [apps]
            
            allowed = [a for a in apps if a.get('Permission') == 'Allow']
            denied = [a for a in apps if a.get('Permission') == 'Deny']
            
            if allowed:
                print(f"\n  ✅ ALLOWED ({len(allowed)} apps):")
                print("-" * 70)
                for app in allowed:
                    app_name = app.get('App', 'Unknown')
                    if '\\' in str(app_name):
                        display_name = os.path.basename(str(app_name))
                    else:
                        display_name = str(app_name).split('_')[0] if '_' in str(app_name) else str(app_name)
                    print(f"    ✓ {display_name}")
            
            if denied:
                print(f"\n  ❌ DENIED ({len(denied)} apps):")
                print("-" * 70)
                for app in denied:
                    app_name = app.get('App', 'Unknown')
                    if '\\' in str(app_name):
                        display_name = os.path.basename(str(app_name))
                    else:
                        display_name = str(app_name).split('_')[0] if '_' in str(app_name) else str(app_name)
                    print(f"    ✗ {display_name}")
            
            return apps
            
        print("\n  No camera permissions found")
        return []
        
    except Exception as e:
        print(f"\n  ⚠️ Error getting permissions: {e}")
        return []

def check_camera_privacy_settings():
    """Check system-wide camera privacy settings."""
    print("\n" + "=" * 70)
    print("  ⚙️ CAMERA PRIVACY SETTINGS")
    print("=" * 70)
    
    ps_command = '''
    $settings = @{}
    
    # Check if camera access is enabled system-wide
    $globalPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    if (Test-Path $globalPath) {
        $globalValue = (Get-ItemProperty $globalPath -Name Value -ErrorAction SilentlyContinue).Value
        $settings.GlobalAccess = $globalValue
    }
    
    # Check user-level setting
    $userPath = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
    if (Test-Path $userPath) {
        $userValue = (Get-ItemProperty $userPath -Name Value -ErrorAction SilentlyContinue).Value
        $settings.UserAccess = $userValue
    }
    
    $settings | ConvertTo-Json
    '''
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=15
        )
        
        if result.stdout.strip():
            settings = json.loads(result.stdout.strip())
            
            global_access = settings.get('GlobalAccess', 'Unknown')
            user_access = settings.get('UserAccess', 'Unknown')
            
            print(f"\n  System-wide camera access: ", end="")
            if global_access == 'Allow':
                print("✅ Enabled")
            elif global_access == 'Deny':
                print("❌ Disabled")
            else:
                print(f"⚠️ {global_access}")
            
            print(f"  User camera access: ", end="")
            if user_access == 'Allow':
                print("✅ Enabled")
            elif user_access == 'Deny':
                print("❌ Disabled")
            else:
                print(f"⚠️ {user_access}")
                
    except Exception as e:
        print(f"\n  ⚠️ Error checking settings: {e}")

def list_camera_devices():
    """List all camera devices on the system."""
    print("\n" + "=" * 70)
    print("  🎥 DETECTED CAMERA DEVICES")
    print("=" * 70)
    
    ps_command = '''
    Get-PnpDevice -Class Camera -Status OK | Select-Object FriendlyName, InstanceId, Status | ConvertTo-Json
    '''
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=15
        )
        
        if result.stdout.strip() and result.stdout.strip() != 'null':
            devices = json.loads(result.stdout.strip())
            if not isinstance(devices, list):
                devices = [devices]
            
            print(f"\n  Found {len(devices)} camera(s):\n")
            for i, device in enumerate(devices, 1):
                print(f"  [{i}] {device.get('FriendlyName', 'Unknown Camera')}")
                print(f"      Status: {device.get('Status', 'Unknown')}")
                print(f"      ID: {device.get('InstanceId', 'Unknown')[:50]}...")
                print()
        else:
            print("\n  No cameras detected")
            
    except Exception as e:
        print(f"\n  ⚠️ Error listing cameras: {e}")

if __name__ == "__main__":
    while True:
        print("\n" + "=" * 70)
        print("       📷 CAMERA MONITOR & HISTORY CHECKER")
        print("=" * 70)
        print("\nOptions:")
        print("  1. Check if camera is currently in use")
        print("  2. View camera access history (last 7 days)")
        print("  3. View all apps with camera permission")
        print("  4. Check camera privacy settings")
        print("  5. List camera devices")
        print("  6. Full report (all of the above)")
        print("  7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            get_camera_currently_in_use()
        elif choice == '2':
            get_camera_history_last_7_days()
        elif choice == '3':
            get_all_camera_permissions()
        elif choice == '4':
            check_camera_privacy_settings()
        elif choice == '5':
            list_camera_devices()
        elif choice == '6':
            list_camera_devices()
            check_camera_privacy_settings()
            get_camera_currently_in_use()
            get_camera_history_last_7_days()
            get_all_camera_permissions()
        elif choice == '7':
            print("\nExiting...")
            break
        else:
            print("\n  ⚠️ Invalid option. Please select 1-7.")
        
        print("\n" + "=" * 70)
        input("\nPress Enter to return to main menu...")
