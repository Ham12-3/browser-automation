$port = $env:OMNI_CDP_PORT
if (-not $port) { $port = "9222" }
$profile = "$env:TEMP\omnibrowse-edge-cdp"
$edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edge)) { $edge = "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe" }
Start-Process -FilePath $edge -ArgumentList "--remote-debugging-port=$port", "--user-data-dir=$profile", "about:blank"
Write-Host "Edge launched with CDP at http://127.0.0.1:$port"

