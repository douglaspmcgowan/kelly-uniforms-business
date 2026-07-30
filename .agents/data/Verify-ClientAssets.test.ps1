$ErrorActionPreference = 'Stop'

$root = Join-Path $env:TEMP ('kelly-client-assets-test-' + [Guid]::NewGuid().ToString('N'))
$repo = Join-Path $root 'repo'
$dataRoot = Join-Path $root 'data'
$projectRoot = Join-Path $dataRoot 'fixture-project'
$assetPath = Join-Path $projectRoot 'inputs\client-provided\fixture.txt'
$script = Join-Path $PSScriptRoot 'Verify-ClientAssets.ps1'

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

try {
    New-Item -ItemType Directory -Path $repo, (Split-Path -Parent $assetPath) -Force | Out-Null
    [System.IO.File]::WriteAllText($assetPath, 'verified fixture', [System.Text.UTF8Encoding]::new($false))
    $hash = (Get-FileHash -LiteralPath $assetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifest = @"
version: 2
project: "fixture-project"
data_root_env: "PROJECT_DATA_ROOT"
assets:
  - id: "fixture"
    project: "fixture-project"
    class: "immutable-file"
    authority: "test fixture"
    local_destination: "inputs/client-provided/fixture.txt"
    adapter: ".agents/data/Verify-ClientAssets.ps1"
    version_rule: "exact fixture generation"
    integrity_rule: "SHA-256 equals sha256:$hash"
    restore_verifier: "run the client asset verifier"
"@
    [System.IO.File]::WriteAllText(
        (Join-Path $repo 'data-manifest.yaml'),
        $manifest,
        [System.Text.UTF8Encoding]::new($false)
    )

    $passed = & $script -Repository $repo -DataRoot $dataRoot
    Assert-True ($passed -match '1 asset') 'Valid immutable client asset did not pass verification.'

    [System.IO.File]::AppendAllText($assetPath, 'tampered')
    $tamperRejected = $false
    try {
        & $script -Repository $repo -DataRoot $dataRoot | Out-Null
    }
    catch {
        $tamperRejected = $_.Exception.Message -match 'hash mismatch'
    }
    Assert-True $tamperRejected 'Tampered immutable client asset was accepted.'

    Write-Output 'Verify-ClientAssets tests passed.'
}
finally {
    if (Test-Path -LiteralPath $root) {
        Remove-Item -LiteralPath $root -Recurse -Force
    }
}
