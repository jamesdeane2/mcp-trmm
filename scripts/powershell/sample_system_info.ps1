# Get System Information
# This is a sample script to demonstrate the local scripts feature
# Returns basic system information about the Windows machine

Write-Host "=== System Information ===" -ForegroundColor Cyan
Write-Host ""

# Computer Name
Write-Host "Computer Name: $env:COMPUTERNAME" -ForegroundColor Green

# Operating System
$os = Get-CimInstance -ClassName Win32_OperatingSystem
Write-Host "OS: $($os.Caption)" -ForegroundColor Green
Write-Host "OS Version: $($os.Version)" -ForegroundColor Green
Write-Host "Build Number: $($os.BuildNumber)" -ForegroundColor Green

# Memory
$totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedRAM = [math]::Round($totalRAM - $freeRAM, 2)
Write-Host ""
Write-Host "Total RAM: ${totalRAM} GB" -ForegroundColor Yellow
Write-Host "Used RAM: ${usedRAM} GB" -ForegroundColor Yellow
Write-Host "Free RAM: ${freeRAM} GB" -ForegroundColor Yellow

# Disk Space
Write-Host ""
Write-Host "Disk Space:" -ForegroundColor Cyan
Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $drive = $_.DeviceID
    $totalSpace = [math]::Round($_.Size / 1GB, 2)
    $freeSpace = [math]::Round($_.FreeSpace / 1GB, 2)
    $usedSpace = [math]::Round($totalSpace - $freeSpace, 2)
    $percentFree = [math]::Round(($freeSpace / $totalSpace) * 100, 2)
    
    Write-Host "  $drive - Total: ${totalSpace} GB, Used: ${usedSpace} GB, Free: ${freeSpace} GB (${percentFree}% free)" -ForegroundColor Yellow
}

# Uptime
$uptime = (Get-Date) - $os.LastBootUpTime
Write-Host ""
Write-Host "System Uptime: $($uptime.Days) days, $($uptime.Hours) hours, $($uptime.Minutes) minutes" -ForegroundColor Green

Write-Host ""
Write-Host "=== End System Information ===" -ForegroundColor Cyan
