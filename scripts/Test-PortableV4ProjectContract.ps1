[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$harnessTools = Join-Path $env:USERPROFILE '.agents\tools'
$archive = Join-Path $root '.agents\archive\task-state-migration'
$archiveManifest = Join-Path $archive 'archive-manifest.json'

foreach ($legacy in @('CURRENT-TASK.md', 'WORK_QUEUE.md', 'VERIFY.md')) {
    if (Test-Path -LiteralPath (Join-Path $root $legacy)) {
        throw "Legacy project architecture file remains at repository root: $legacy"
    }
}

if (-not (Test-Path -LiteralPath $archiveManifest -PathType Leaf)) {
    throw 'Task-state migration archive manifest is missing.'
}
$manifest = Get-Content -LiteralPath $archiveManifest -Raw | ConvertFrom-Json
foreach ($entry in @($manifest.files)) {
    $path = Join-Path $archive ([string]$entry.path)
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Archived legacy file is missing: $($entry.path)"
    }
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne [string]$entry.sha256 -or
        (Get-Item -LiteralPath $path).Length -ne [int64]$entry.size_bytes) {
        throw "Archived legacy file failed byte verification: $($entry.path)"
    }
}

$agents = Get-Content -LiteralPath (Join-Path $root 'AGENTS.md') -Raw
if ($agents -notmatch '<!-- agent-harness:portable:v4:start -->' -or
    $agents -match '<!-- agent-harness:portable:v3:start -->') {
    throw 'AGENTS.md is not exclusively on the portable v4 contract.'
}
$provenance = Get-Content -LiteralPath (Join-Path $root '.agents\harness-provenance.json') -Raw | ConvertFrom-Json
if ([string]$provenance.authority -notmatch 'portable-project-contract/v4') {
    throw 'Harness provenance does not declare portable project contract v4.'
}

& (Join-Path $harnessTools 'Manage-Harness.ps1') `
    -Action VerifyProject -Repository $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Harness VerifyProject failed.' }

& (Join-Path $harnessTools 'Test-WorkState.ps1') -Root $root | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Work Scope state validation failed.' }
$reconcile = & (Join-Path $harnessTools 'Reconcile-WorkState.ps1') -Root $root | ConvertFrom-Json
if (-not $reconcile.reconciled -or $reconcile.drifted_files.Count -ne 0) {
    throw 'Work Scope generated views are not reconciled.'
}

[pscustomobject]@{
    Result = 'PASS'
    PortableContract = 'v4'
    ArchivedLegacyFiles = @($manifest.files).Count
    WorkScope = 'valid-and-reconciled'
} | ConvertTo-Json -Compress
