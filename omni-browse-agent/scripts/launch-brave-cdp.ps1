$port = $env:OMNI_CDP_PORT
if (-not $port) { $port = "9222" }
$profile = "$env:TEMP\omnibrowse-brave-cdp"
$brave = "${env:ProgramFiles}\BraveSoftware\Brave-Browser\Application\brave.exe"
if (-not (Test-Path $brave)) { $brave = "${env:LOCALAPPDATA}\BraveSoftware\Brave-Browser\Application\brave.exe" }
Start-Process -FilePath $brave -ArgumentList "--remote-debugging-port=$port", "--user-data-dir=$profile", "about:blank"
Write-Host "Brave launched with CDP at http://127.0.0.1:$port"

