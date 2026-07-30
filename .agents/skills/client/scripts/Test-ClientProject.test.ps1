$ErrorActionPreference = 'Stop'

$root = Join-Path $env:TEMP ('client-project-v3-test-' + [Guid]::NewGuid().ToString('N'))
$repo = Join-Path $root 'repo'
$verifier = Join-Path $PSScriptRoot 'Test-ClientProject.ps1'

try {
    New-Item -ItemType Directory -Path $repo -Force | Out-Null
    $files = @{
        'AGENTS.md' = "# Project`n"
        'CLIENT.md' = @"
# Client profile
## Identity
## Business
## Stakeholders and decisions
## Current digital estate
## Brand
## Constraints and risks
## AI context
## Evidence status
"@
        'DELIVERABLES.md' = @"
# Deliverables
## Delivery rules
## Register
DEL-001 Requested
## Detail
## Change record
"@
        'SOURCES.md' = @"
# Sources and assets
## Source ledger
MSG-001
## Asset ledger
## Decisions
## Provenance gaps
"@
        'TASK.md' = @"
# Task
## Goal
Fixture
## Active
## Queue
## Blocked
## Needs decision
## Completed
## Verification
"@
        'STATUS.md' = "# Status`n"
        'LOG.md' = "# Log`n"
        'data-manifest.yaml' = "version: 2`nproject: `"fixture`"`ndata_root_env: `"PROJECT_DATA_ROOT`"`nassets: []`n"
        'secret-manifest.json' = "{`"schemaVersion`":1,`"project`":`"fixture`",`"variables`":[]}`n"
        'skills-manifest.json' = "{`"schemaVersion`":2,`"project`":`"fixture`",`"bindings`":[]}`n"
    }
    foreach ($name in $files.Keys) {
        [System.IO.File]::WriteAllText(
            (Join-Path $repo $name),
            $files[$name],
            [System.Text.UTF8Encoding]::new($false)
        )
    }

    $output = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $verifier -Repository $repo 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Valid v3 client project was rejected:`n$($output -join [Environment]::NewLine)"
    }

    Write-Output 'Test-ClientProject v3 compatibility test passed.'
}
finally {
    if (Test-Path -LiteralPath $root) {
        Remove-Item -LiteralPath $root -Recurse -Force
    }
}
