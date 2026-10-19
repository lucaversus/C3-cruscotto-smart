param(
    [ValidatePattern('^COM[0-9]+$')][string]$Porta = 'COM3',
    [ValidateSet('esp32-hw394-logger', 'esp32-hw394-vehicle')]
    [string]$Profilo = 'esp32-hw394-logger',
    [switch]$AttendiBoot,
    [switch]$SoloMonitor,
    [switch]$Riavvia
)

# Avviare in un terminale visibile. Nessun caricamento nascosto o monitor concorrente.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot '.tools/pio-venv/Scripts/python.exe'
$firmwareFolder = Join-Path $projectRoot 'data-logger/firmware/logger'
$serialFolder = Join-Path $projectRoot '.tools/serial'
if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Runtime PlatformIO locale assente: $pythonExe"
}
New-Item -ItemType Directory -Path $serialFolder -Force | Out-Null
$env:PLATFORMIO_CORE_DIR = Join-Path $env:USERPROFILE 'Documents/Codex/pio-c3'
$env:PYTHONUNBUFFERED = '1'
$Host.UI.RawUI.WindowTitle = "C3+AI - Caricamento e monitor $Porta"
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$uploadLog = Join-Path $serialFolder "upload-$stamp.log"
$statePath = Join-Path $serialFolder 'ultimo-caricamento.json'
$state = [ordered]@{ porta=$Porta; profilo=$Profilo; fase='caricamento'; log=$uploadLog; exit_code=$null }
$state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
Write-Host "=== C3+AI / Data Logger - $Profilo su $Porta ===" -ForegroundColor Cyan
Write-Host 'Compilazione e caricamento visibili; poi monitor seriale a 115200 baud.'
Write-Host "Log caricamento: $uploadLog"
if ($AttendiBoot -and -not $SoloMonitor) {
    $state.fase = 'attesa_boot'
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host 'TIENI PREMUTO BOOT SULLA ESP32, POI PREMI INVIO QUI.' -ForegroundColor Yellow
    Write-Host 'Rilascia BOOT quando compare Writing at...'
    Read-Host 'Premi Invio mantenendo BOOT premuto' | Out-Null
    $state.fase = 'caricamento'
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
}
Push-Location $projectRoot
try {
    if (-not $SoloMonitor) {
    & $pythonExe -m platformio run --project-dir $firmwareFolder -e $Profilo --target upload --upload-port $Porta |
        Tee-Object -FilePath $uploadLog
    $uploadExit = $LASTEXITCODE
    $state.exit_code = $uploadExit
    if ($uploadExit -ne 0) {
        $state.fase = 'caricamento_fallito'
        $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
        Write-Host "Caricamento non riuscito (codice $uploadExit). Monitor non aperto." -ForegroundColor Red
        return
    }
    }
    $state.fase = 'monitor_seriale'
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host '=== MONITOR SERIALE ===' -ForegroundColor Green
    Write-Host 'Comandi firmware con Invio: status | stop | help. Ctrl+C chiude il monitor.'
    Write-Host 'Senza modulo SD: ATTESA SD, nessuna registrazione.'
    $serialLog = Join-Path $serialFolder "monitor-$stamp.log"
    $monitorArgs = @((Join-Path $projectRoot 'tools/monitor-seriale.py'), '--port', $Porta, '--baud', '115200', '--log', $serialLog)
    if (-not $SoloMonitor -or $Riavvia) { $monitorArgs += '--reset' }
    & $pythonExe @monitorArgs
    $state.fase = 'monitor_chiuso'
    $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
} finally {
    Pop-Location
}
