# Export a .pptx to PDF using the installed PowerPoint.
#
# The PDF is the transport format: it looks identical on any machine, opens in
# any browser, and survives Google Drive without a conversion step. The .pptx
# stays the editable source.
#
#   powershell -File 09_reviews/_pdf.ps1 09_reviews/C00-kickoff.pptx
param(
    [Parameter(Mandatory = $true)][string]$Deck,
    [string]$Out
)
$Deck = (Resolve-Path $Deck).Path
if (-not $Out) { $Out = [IO.Path]::ChangeExtension($Deck, ".pdf") }

$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Deck, $true, $false, $false)
$pres.SaveAs($Out, 32)          # 32 = ppSaveAsPDF
$pres.Close()
$app.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null

"{0}  ({1:N1} MB)" -f $Out, ((Get-Item $Out).Length / 1MB)
