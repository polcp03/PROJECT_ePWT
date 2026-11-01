# Live serial view for hall_test: magnet lines in green. Ctrl+C to quit.
$p = New-Object System.IO.Ports.SerialPort COM4, 115200
$p.DtrEnable = $false
$p.RtsEnable = $false
$p.ReadTimeout = 500
$p.Open()
$p.DiscardInBuffer()
Write-Host "Leyendo COM4 en vivo. Ctrl+C para salir." -ForegroundColor Cyan
try {
  while ($true) {
    try {
      $line = $p.ReadLine().Trim()
      if ($line -match 'MAGNET') { Write-Host $line -ForegroundColor Green }
      else { Write-Host $line }
    } catch [System.TimeoutException] { }
  }
} finally { $p.Close() }
