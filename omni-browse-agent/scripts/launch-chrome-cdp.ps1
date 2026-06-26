$port = $env:OMNI_CDP_PORT
if (-not $port) { $port = "9222" }
$profile = "$env:TEMP\omnibrowse-chrome-cdp"
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
if (-not (Test-Path $chrome)) { $chrome = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe" }
Start-Process -FilePath $chrome -ArgumentList "--remote-debugging-port=$port", "--user-data-dir=$profile", "about:blank"
Write-Host "Chrome launched with CDP at http://127.0.0.1:$port"

