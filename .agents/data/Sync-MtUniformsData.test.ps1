[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$adapter = Join-Path $PSScriptRoot 'Sync-MtUniformsData.ps1'
$sandbox = Join-Path ([System.IO.Path]::GetTempPath()) ("mtuniforms-data-test-" + [guid]::NewGuid().ToString('N'))
$dataRoot = Join-Path $sandbox 'data'
$syncRoot = Join-Path $sandbox 'sync'
$repository = Join-Path $sandbox 'repo'
$relative = 'inputs/sample/source.txt'

try {
    New-Item -ItemType Directory -Path (Join-Path $dataRoot 'kelly-uniforms-business\inputs\sample') -Force | Out-Null
    New-Item -ItemType Directory -Path $syncRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $repository -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Value 'known payload' -NoNewline
    $knownHash = (Get-FileHash -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifest = @"
version: 2
project: "kelly-uniforms-business"
data_root_env: "PROJECT_DATA_ROOT"
assets:
  - id: "sample"
    project: "kelly-uniforms-business"
    class: "immutable-file"
    authority: "test fixture"
    local_destination: "inputs/sample/source.txt"
    adapter: ".agents/data/Sync-MtUniformsData.ps1"
    version_rule: "immutable"
    integrity_rule: "SHA-256 $knownHash"
    restore_verifier: "test"
  - id: "private-sample"
    project: "kelly-uniforms-business"
    class: "portable-export"
    authority: "test fixture"
    local_destination: "private/recovery/raw-export.zip"
    adapter: ".agents/data/Sync-MtUniformsData.ps1"
    version_rule: "immutable"
    integrity_rule: "SHA-256 $knownHash"
    restore_verifier: "test"
  - id: "directory-publish"
    project: "kelly-uniforms-business"
    class: "immutable-file"
    authority: "test fixture"
    local_destination: "inputs/directory-publish/source.txt"
    adapter: ".agents/data/Sync-MtUniformsData.ps1"
    version_rule: "immutable"
    integrity_rule: "SHA-256 $knownHash"
    restore_verifier: "test"
  - id: "directory-restore"
    project: "kelly-uniforms-business"
    class: "immutable-file"
    authority: "test fixture"
    local_destination: "inputs/directory-restore/source.txt"
    adapter: ".agents/data/Sync-MtUniformsData.ps1"
    version_rule: "immutable"
    integrity_rule: "SHA-256 $knownHash"
    restore_verifier: "test"
  - id: "recovery-backup"
    project: "kelly-uniforms-business"
    class: "portable-export"
    authority: "test fixture"
    local_destination: "backups/business-continuity/recovery.tar.gz"
    adapter: ".agents/data/Sync-MtUniformsData.ps1"
    version_rule: "immutable"
    integrity_rule: "SHA-256 $knownHash"
    restore_verifier: "test"
"@
    Set-Content -LiteralPath (Join-Path $repository 'data-manifest.yaml') -Value $manifest -NoNewline

    $publish = & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($publish.Result -ne 'PASS') { throw 'Publish did not pass.' }

    Remove-Item -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative")
    $restore = & $adapter -Action Restore -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($restore.Result -ne 'PASS') { throw 'Restore did not pass.' }

    $verify = & $adapter -Action Verify -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($verify.Result -ne 'PASS' -or -not $verify.Match) { throw 'Verify did not confirm a matching copy.' }

    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Value 'changed payload' -NoNewline
    $mismatch = & $adapter -Action Verify -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($mismatch.Result -ne 'ATTENTION_REQUIRED' -or $mismatch.Match) { throw 'Verify did not flag divergence.' }
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Value 'known payload' -NoNewline
    Set-Content -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$relative") -Value 'changed payload' -NoNewline
    $divergentPublish = & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($divergentPublish.Result -ne 'ATTENTION_REQUIRED' -or $divergentPublish.Changed) { throw 'Publish overwrote or accepted a divergent destination.' }
    Set-Content -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$relative") -Value 'known payload' -NoNewline
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Value 'changed payload' -NoNewline
    $divergentRestore = & $adapter -Action Restore -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($divergentRestore.Result -ne 'ATTENTION_REQUIRED' -or $divergentRestore.Changed) { throw 'Restore overwrote or accepted a divergent destination.' }

    $privateRelative = 'private/recovery/raw-export.zip'
    New-Item -ItemType Directory -Path (Join-Path $dataRoot 'kelly-uniforms-business\private\recovery') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$privateRelative") -Value 'restricted payload' -NoNewline
    $privatePublish = & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'private-sample' -RelativeDestination $privateRelative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($privatePublish.Result -ne 'ATTENTION_REQUIRED' -or $privatePublish.Changed) { throw 'Unencrypted private publish was not refused.' }
    if (Test-Path -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$privateRelative")) { throw 'Private payload was copied to sync storage.' }

    $backupRelative = 'backups/business-continuity/recovery.tar.gz'
    New-Item -ItemType Directory -Path (Join-Path $dataRoot 'kelly-uniforms-business\backups\business-continuity') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$backupRelative") -Value 'known payload' -NoNewline
    $backupPublish = & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'recovery-backup' -RelativeDestination $backupRelative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($backupPublish.Result -ne 'ATTENTION_REQUIRED' -or $backupPublish.Changed) { throw 'Unencrypted recovery backup publish was not refused.' }
    if (Test-Path -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$backupRelative")) { throw 'Recovery backup was copied to sync storage.' }

    $unsafeRejected = $false
    try {
        & $adapter -Action Verify -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'unsafe' -RelativeDestination '..\escape.txt' -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $unsafeRejected = $true }
    if (-not $unsafeRejected) { throw 'Traversal path was not rejected.' }

    $projectRejected = $false
    try {
        & $adapter -Action Verify -Repository $repository -Project '..' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $projectRejected = $true }
    if (-not $projectRejected) { throw 'Malformed project name was not rejected.' }

    New-Item -ItemType Directory -Path (Join-Path $dataRoot 'kelly-uniforms-business\inputs\directory-publish') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $dataRoot 'kelly-uniforms-business\inputs\directory-publish\source.txt') -Value 'known payload' -NoNewline
    New-Item -ItemType Directory -Path (Join-Path $syncRoot 'kelly-uniforms-business\inputs\directory-publish\source.txt') -Force | Out-Null
    $directoryPublishRejected = $false
    try {
        & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'directory-publish' -RelativeDestination 'inputs/directory-publish/source.txt' -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $directoryPublishRejected = $true }
    if (-not $directoryPublishRejected) { throw 'Publish accepted a directory as the destination leaf.' }

    New-Item -ItemType Directory -Path (Join-Path $syncRoot 'kelly-uniforms-business\inputs\directory-restore') -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $syncRoot 'kelly-uniforms-business\inputs\directory-restore\source.txt') -Value 'known payload' -NoNewline
    New-Item -ItemType Directory -Path (Join-Path $dataRoot 'kelly-uniforms-business\inputs\directory-restore\source.txt') -Force | Out-Null
    $directoryRestoreRejected = $false
    try {
        & $adapter -Action Restore -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'directory-restore' -RelativeDestination 'inputs/directory-restore/source.txt' -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $directoryRestoreRejected = $true }
    if (-not $directoryRestoreRejected) { throw 'Restore accepted a directory as the destination leaf.' }

    Remove-Item -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$relative")
    Set-Content -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative") -Value 'tampered payload' -NoNewline
    $tamperRejected = $false
    try {
        & $adapter -Action Publish -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $tamperRejected = $true }
    if (-not $tamperRejected) { throw 'Publish accepted bytes that do not match the manifest checksum.' }

    Remove-Item -LiteralPath (Join-Path $dataRoot "kelly-uniforms-business\$relative")
    New-Item -ItemType Directory -Path (Split-Path (Join-Path $syncRoot "kelly-uniforms-business\$relative") -Parent) -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $syncRoot "kelly-uniforms-business\$relative") -Value 'tampered payload' -NoNewline
    $tamperedRestoreRejected = $false
    try {
        & $adapter -Action Restore -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot | Out-Null
    }
    catch { $tamperedRestoreRejected = $true }
    if (-not $tamperedRestoreRejected) { throw 'Restore accepted bytes that do not match the manifest checksum.' }
    $tamperedVerify = & $adapter -Action Verify -Repository $repository -Project 'kelly-uniforms-business' -AssetId 'sample' -RelativeDestination $relative -DataRoot $dataRoot -SyncRoot $syncRoot
    if ($tamperedVerify.Result -ne 'ATTENTION_REQUIRED' -or $tamperedVerify.Match) { throw 'Verify accepted tampered or missing bytes.' }

    'Sync-MtUniformsData tests passed.'
}
finally {
    if (Test-Path -LiteralPath $sandbox) {
        Remove-Item -LiteralPath $sandbox -Recurse -Force
    }
}
