# Render a .pptx to PNG slides using the installed PowerPoint.
# There is no LibreOffice on this machine, so this is the only way to see what
# the deck actually looks like before opening it by hand.
#
#   powershell -File 09_reviews/_render.ps1 <deck.pptx> <outdir> [width]
param(
    [Parameter(Mandatory = $true)][string]$Deck,
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$Width = 1600
)
$Deck = (Resolve-Path $Deck).Path
if (Test-Path $Out) { Remove-Item "$Out\*" -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Force $Out | Out-Null
$Out = (Resolve-Path $Out).Path

$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($Deck, $true, $false, $false)
$pres.Export($Out, "PNG", $Width, [int]($Width * 9 / 16))
$n = $pres.Slides.Count
$pres.Close()
$app.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($app) | Out-Null

# PowerPoint names exports in the UI language (Diapositiva1.PNG / Slide1.PNG)
# and does not zero-pad. Normalise to slide-01.png so they sort correctly.
Get-ChildItem "$Out\*.PNG" | ForEach-Object {
    if ($_.BaseName -match '(\d+)$') {
        $i = [int]$Matches[1]
        Rename-Item $_.FullName ("slide-{0:d2}.png" -f $i)
    }
}
"rendered $n slides -> $Out"
