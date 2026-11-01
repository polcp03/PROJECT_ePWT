# Records wheel_capture output to a CSV for N seconds and shows, once per second,
# how many magnet passes (polled falling edges) and interrupt edges it saw.
# Usage: powershell -ExecutionPolicy Bypass -File capture.ps1 <seconds> <out.csv>
param([int]$Seconds = 60, [string]$Out = "capture.csv")

$p = New-Object System.IO.Ports.SerialPort COM4, 921600
$p.DtrEnable = $false
$p.RtsEnable = $false
$p.Open()
$p.DiscardInBuffer()
$w = New-Object System.IO.StreamWriter($Out, $false)
$w.WriteLine("t_us,level,isr_edges")
Write-Host "Grabando $Seconds s en $Out - gira la rueda" -ForegroundColor Cyan
$end = (Get-Date).AddSeconds($Seconds)
$pending = ""
$passes = 0; $isr = 0; $tick = (Get-Date).AddSeconds(1); $sec = 0
while ((Get-Date) -lt $end) {
  $pending += $p.ReadExisting()
  $parts = $pending -split "`n"
  $pending = $parts[-1]
  foreach ($l in $parts[0..($parts.Count - 2)]) {
    $l = $l.Trim()
    if ($l -match '^(\d+),([01]),(\d+)$') {
      $w.WriteLine($l)
      if ($Matches[2] -eq '0') { $passes++ }
      $isr += [int]$Matches[3]
    }
  }
  if ((Get-Date) -ge $tick) {
    $sec++
    $color = if ($passes -gt 0) { 'Green' } else { 'Gray' }
    Write-Host ("{0,3} s   imanes: {1,4}   disparos interrupcion: {2,6}" -f $sec, $passes, $isr) -ForegroundColor $color
    $passes = 0; $isr = 0; $tick = $tick.AddSeconds(1)
  }
  Start-Sleep -Milliseconds 20
}
$w.Close(); $p.Close()
Write-Host "Hecho. Guardado en $Out" -ForegroundColor Cyan
