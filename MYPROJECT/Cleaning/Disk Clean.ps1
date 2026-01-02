Write-Host "=== Disk Cleanup started ===" -ForegroundColor Cyan

# 1. User TEMP
Write-Host "Cleaning user TEMP..."
Remove-Item "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. System TEMP
Write-Host "Cleaning system TEMP..."
Remove-Item "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Windows Update cache
Write-Host "Cleaning Windows Update cache..."
Stop-Service wuauserv -Force -ErrorAction SilentlyContinue
Remove-Item "C:\Windows\SoftwareDistribution\Download\*" -Recurse -Force -ErrorAction SilentlyContinue
Start-Service wuauserv -ErrorAction SilentlyContinue

# 4. Delivery Optimization cache
Write-Host "Cleaning Delivery Optimization cache..."
Remove-Item "C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache\*" `
-Recurse -Force -ErrorAction SilentlyContinue

# 5. Prefetch
Write-Host "Cleaning Prefetch..."
Remove-Item "C:\Windows\Prefetch\*" -Recurse -Force -ErrorAction SilentlyContinue

# 6. Windows Logs (SAFE ONLY)
Write-Host "Cleaning Windows logs (safe)..."
wevtutil el |
Where-Object { $_ -notmatch "Analytic|Debug" } |
ForEach-Object {
    wevtutil cl "$_" 2>$null
}

# 7. Recycle Bin
Write-Host "Emptying Recycle Bin..."
Clear-RecycleBin -Force -ErrorAction SilentlyContinue

# 8. WinSxS cleanup (safe)
Write-Host "Cleaning WinSxS (old updates)..."
DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase | Out-Null

Write-Host "=== Disk Cleanup completed successfully ===" -ForegroundColor Green
