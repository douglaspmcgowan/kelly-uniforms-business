[CmdletBinding()]
param(
    [switch]$RequireRemoteTree
)

$ErrorActionPreference = 'Stop'
$repository = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$tools = Join-Path $env:USERPROFILE '.agents\tools'
$python = (Get-Command py -ErrorAction Stop).Source
$npm = (Get-Command npm.cmd -ErrorAction Stop).Source
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$gitleaks = Join-Path $env:USERPROFILE 'Tools\gitleaks\gitleaks.exe'

function Invoke-Gate {
    param(
        [Parameter(Mandatory)] [string]$Name,
        [Parameter(Mandatory)] [scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE."
    }
}

if (-not (Test-Path -LiteralPath $gitleaks -PathType Leaf)) {
    throw "Gitleaks is missing from the pinned project verification path: $gitleaks"
}

Push-Location $repository
try {
    Invoke-Gate 'Python recovery tests' {
        & $python -m unittest discover -s scripts -p 'test_*.py'
    }
    Invoke-Gate 'External-data adapter tests' {
        & $pwsh -NoProfile -File '.agents/data/Sync-MtUniformsData.test.ps1'
    }
    Invoke-Gate 'Brand gallery tests' {
        Push-Location 'brand-gallery'
        try { & $npm test } finally { Pop-Location }
    }
    Invoke-Gate 'Storefront contract tests' {
        Push-Location 'storefront'
        try { & $npm test } finally { Pop-Location }
    }
    Invoke-Gate 'Storefront production build' {
        Push-Location 'storefront'
        try { & $npm run build } finally { Pop-Location }
    }
    Invoke-Gate 'Work Scope state validation' {
        & $pwsh -NoProfile -File (Join-Path $tools 'Test-WorkState.ps1') -Root $repository
    }
    Invoke-Gate 'Work Scope view reconciliation' {
        & $pwsh -NoProfile -File (Join-Path $tools 'Reconcile-WorkState.ps1') -Root $repository
    }
    Invoke-Gate 'Secret scan' {
        & $gitleaks dir --no-banner --redact $repository
    }
    Invoke-Gate 'Unstaged whitespace check' {
        & git diff --check
    }
    Invoke-Gate 'Staged whitespace check' {
        & git diff --cached --check
    }

    $forbiddenTracked = @(
        & git ls-files |
            Where-Object {
                $_ -match '(^|/)(__pycache__|state\.lock)(/|$)' -or
                $_ -match '\.(pyc|lock\.json)$'
            }
    )
    if ($forbiddenTracked.Count -gt 0) {
        throw "Runtime-only files are tracked: $($forbiddenTracked -join ', ')"
    }

    $secretManifest = Get-Content -LiteralPath 'secret-manifest.json' -Raw | ConvertFrom-Json
    if ($null -eq $secretManifest.variables -or @($secretManifest.variables).Count -lt 5) {
        throw 'The value-free secret manifest is missing required recovery handles.'
    }
    $state = Get-Content -LiteralPath '.agents/work/state.json' -Raw | ConvertFrom-Json
    if ($state.project.remote -ne 'github.com/douglaspmcgowan/kelly-uniforms-business') {
        throw 'Work Scope is not bound to the project remote.'
    }

    if ($RequireRemoteTree) {
        Invoke-Gate 'Remote refresh' { & git fetch origin }
        $localTree = (& git rev-parse 'HEAD^{tree}').Trim()
        $remoteTree = (& git rev-parse 'origin/master^{tree}').Trim()
        if ($LASTEXITCODE -ne 0 -or $localTree -ne $remoteTree) {
            throw 'The verified repository tree is not present on origin/master.'
        }
    }

    [pscustomobject]@{
        Result = 'PASS'
        PythonTests = 'passed'
        DataAdapter = 'passed'
        BrandGallery = 'passed'
        Storefront = 'tested-and-built'
        WorkScope = 'valid-and-reconciled'
        SecretScan = 'passed'
        RuntimeFilesTracked = 0
        RemoteTree = if ($RequireRemoteTree) { 'matches-origin-master' } else { 'not-required' }
    } | ConvertTo-Json
}
finally {
    Pop-Location
}
