Param(
    [string]$Target = 'http://localhost:5000',
    [int]$Threshold
)

# Allow threshold from environment if not passed
if (-not $PSBoundParameters.ContainsKey('Threshold')) {
    if ($env:ZAP_FAIL_THRESHOLD) {
        try { $Threshold = [int]$env:ZAP_FAIL_THRESHOLD } catch { $Threshold = 0 }
    } else {
        $Threshold = 0
    }
}

$reportDir = Join-Path (Get-Location) 'zap-reports'
if (-not (Test-Path $reportDir)) { New-Item -ItemType Directory -Path $reportDir | Out-Null }

Write-Host "Starting full ZAP scan against $Target"

$candidateImages = @(
    'ghcr.io/zaproxy/zaproxy:stable',
    'softwaresecurityproject/zap-stable',
    'zaproxy/zap-stable'
)

$selectedImage = $null
foreach ($img in $candidateImages) {
    Write-Host "Trying to pull Docker image: $img"
    & docker pull $img
    $pullExit = $LASTEXITCODE
    if ($pullExit -eq 0) {
        Write-Host "Pulled image: $img"
        $selectedImage = $img
        break
    } else {
        Write-Warning "Pull failed for $img (exit $pullExit)"
    }
}

if (-not $selectedImage) {
    Write-Error "Failed to pull any candidate ZAP images."
    Write-Error "Possible causes: network access, Docker Hub rate limits, or image name/tag changes."
    Write-Host "Diagnóstico rápido: ejecutar 'docker search zap2docker' y 'docker login' si procede."
    exit 125
}

# Run zap-full-scan using the selected image
$dockerArgs = @(
    'run', '--rm', 
    '-v', "${reportDir}:/zap/wrk:rw",
    '-t',
    $selectedImage,
    'zap-full-scan.py', '-t', $Target,
    '-r', 'zap-full-report.html', '-J', 'zap-full-report.json'
)
& docker @dockerArgs
$dockerExit = $LASTEXITCODE
Write-Host "Docker zap-full-scan exit code: $dockerExit"

$jsonReport = Join-Path $reportDir 'zap-full-report.json'
if (-not (Test-Path $jsonReport)) {
    Write-Host 'No ZAP JSON report generated'
    exit 0
}

$data = Get-Content $jsonReport -Raw | ConvertFrom-Json
$high = 0
if ($data.site) {
    foreach ($site in $data.site) {
        if ($site.alerts) {
            foreach ($alert in $site.alerts) {
                if ($alert.risk -in @('High','Critical')) { $high++ }
            }
        }
    }
}

Write-Host "ZAP high/critical alerts: $high"
Write-Host "ZAP fail threshold: $Threshold"

if ($high -gt $Threshold) {
    Write-Error "Failing: $high alerts > threshold $Threshold"
    exit 2
}

Write-Host "ZAP scan complete. Reports in $reportDir"
exit 0
