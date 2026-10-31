# Serial monitor for can_logger. Type start / stop / ls and press Enter. Ctrl+C to quit.
# Waits for COM4 to appear and reconnects if the USB cable is unplugged.
$line = ""
while ($true) {
  Write-Host "waiting for the ESP32 on COM4 (plug the USB cable)..." -ForegroundColor DarkGray
  while (-not ([System.IO.Ports.SerialPort]::GetPortNames() -contains 'COM4')) { Start-Sleep -Milliseconds 500 }
  $p = New-Object System.IO.Ports.SerialPort COM4, 921600
  $p.DtrEnable = $false
  $p.RtsEnable = $false
  try { $p.Open() } catch { Write-Host "COM4 busy (close the Arduino IDE)" -ForegroundColor Red; Start-Sleep 2; continue }
  Write-Host "COM4 open - type start / stop and press Enter. SPI errors show in yellow." -ForegroundColor Green
  try {
    while ($true) {
      $txt = $p.ReadExisting()
      foreach ($l in ($txt -split "`n")) {
        if ($l -match 'SPI err (\d+)' -and [int]$Matches[1] -gt 0) { Write-Host $l.TrimEnd() -ForegroundColor Yellow }
        elseif ($l.Trim()) { Write-Host $l.TrimEnd() }
      }
      while ([Console]::KeyAvailable) {
        $k = [Console]::ReadKey($true)
        if ($k.Key -eq 'Enter') { Write-Host "> $line" -ForegroundColor Cyan; $p.WriteLine($line); $line = "" }
        elseif ($k.Key -eq 'Backspace') { if ($line.Length) { $line = $line.Substring(0, $line.Length - 1) } }
        else { $line += $k.KeyChar }
      }
      Start-Sleep -Milliseconds 50
    }
  } catch {
    Write-Host "ESP32 disconnected" -ForegroundColor Red
  } finally {
    $p.Close()
  }
}
