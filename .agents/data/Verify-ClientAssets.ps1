[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Repository,

    [string]$DataRoot = $env:PROJECT_DATA_ROOT,

    [string]$AssetId
)

$ErrorActionPreference = 'Stop'
$repo = [System.IO.Path]::GetFullPath($Repository)
if (-not (Test-Path -LiteralPath $repo -PathType Container)) {
    throw "Repository directory does not exist: $repo"
}
if ([string]::IsNullOrWhiteSpace($DataRoot)) {
    throw 'PROJECT_DATA_ROOT is not configured and -DataRoot was not supplied.'
}
$dataRootPath = [System.IO.Path]::GetFullPath($DataRoot)
$manifestPath = Join-Path $repo 'data-manifest.yaml'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Data manifest does not exist: $manifestPath"
}

$lines = [System.IO.File]::ReadAllLines($manifestPath)
$project = $null
$assets = [System.Collections.Generic.List[object]]::new()
$current = $null

foreach ($line in $lines) {
    if ($line -match '^project:\s*"(?<value>[A-Za-z0-9][A-Za-z0-9._-]*)"\s*$') {
        $project = [string]$Matches.value
        continue
    }
    if ($line -match '^\s{2}- id:\s*"(?<value>[a-z0-9][a-z0-9._-]*)"\s*$') {
        if ($current) { $assets.Add([pscustomobject]$current) }
        $current = @{
            Id = [string]$Matches.value
            Destination = $null
            ExpectedHash = $null
        }
        continue
    }
    if (-not $current) { continue }
    if ($line -match '^\s{4}local_destination:\s*"(?<value>[^"]+)"\s*$') {
        $current.Destination = [string]$Matches.value
        continue
    }
    if ($line -match '^\s{4}integrity_rule:\s*"SHA-256 equals sha256:(?<value>[a-fA-F0-9]{64})"\s*$') {
        $current.ExpectedHash = ([string]$Matches.value).ToLowerInvariant()
    }
}
if ($current) { $assets.Add([pscustomobject]$current) }

if ([string]::IsNullOrWhiteSpace($project)) {
    throw 'The data manifest has no valid top-level project identifier.'
}
if (-not $assets.Count) {
    Write-Output "Client asset verification passed: $project (0 assets)."
    exit 0
}

$selected = @($assets)
if (-not [string]::IsNullOrWhiteSpace($AssetId)) {
    $selected = @($assets | Where-Object { $_.Id -eq $AssetId })
    if ($selected.Count -ne 1) {
        throw "Unknown or duplicated asset id: $AssetId"
    }
}

$projectDataRoot = [System.IO.Path]::GetFullPath((Join-Path $dataRootPath $project))
$projectPrefix = $projectDataRoot.TrimEnd('\') + '\'
foreach ($asset in $selected) {
    if ([string]::IsNullOrWhiteSpace($asset.Destination)) {
        throw "Asset '$($asset.Id)' has no local_destination."
    }
    if ([string]::IsNullOrWhiteSpace($asset.ExpectedHash)) {
        throw "Asset '$($asset.Id)' has no supported SHA-256 integrity rule."
    }
    $relative = ([string]$asset.Destination).Replace('/', '\')
    $path = [System.IO.Path]::GetFullPath((Join-Path $projectDataRoot $relative))
    if (-not $path.StartsWith($projectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Asset '$($asset.Id)' resolves outside the project data root."
    }
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Asset '$($asset.Id)' is missing at its declared local destination."
    }
    $actualHash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $asset.ExpectedHash) {
        throw "Asset '$($asset.Id)' hash mismatch."
    }
}

$noun = if ($selected.Count -eq 1) { 'asset' } else { 'assets' }
Write-Output "Client asset verification passed: $project ($($selected.Count) $noun)."
