[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('Publish', 'Restore', 'Verify')]
    [string]$Action,
    [Parameter(Mandatory)][string]$Repository,
    [Parameter(Mandatory)][string]$Project,
    [Parameter(Mandatory)][string]$AssetId,
    [Parameter(Mandatory)][string]$RelativeDestination,
    [Parameter(Mandatory)][string]$DataRoot,
    [Parameter(Mandatory)][string]$SyncRoot
)

$ErrorActionPreference = 'Stop'

if ($Project -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') {
    throw "Project name is malformed."
}
if ($RelativeDestination -notmatch '^(inputs|runtime|outputs|private|backups)[/\\]') {
    throw "Asset '$AssetId' is outside the supported project-data classes."
}

function ConvertFrom-ManifestScalar([string]$Value) {
    $trimmed = $Value.Trim()
    if ($trimmed.StartsWith('"')) { return ($trimmed | ConvertFrom-Json) }
    if ($trimmed.StartsWith("'")) { return $trimmed.Substring(1, $trimmed.Length - 2).Replace("''", "'") }
    return $trimmed
}

function Get-ManifestAssetContract {
    $repositoryRoot = [System.IO.Path]::GetFullPath($Repository)
    if (-not (Test-Path -LiteralPath $repositoryRoot -PathType Container)) {
        throw "Repository is unavailable."
    }
    $manifestPath = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot 'data-manifest.yaml'))
    $repositoryPrefix = $repositoryRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $manifestPath.StartsWith($repositoryPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
        -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw "Project data manifest is unavailable."
    }

    $assets = [System.Collections.Generic.List[hashtable]]::new()
    $current = $null
    foreach ($line in Get-Content -LiteralPath $manifestPath) {
        if ($line -match '^  - ([a-z_][a-z0-9_]*):\s*(.*)$') {
            $current = @{}
            $assets.Add($current)
            $current[$Matches[1]] = ConvertFrom-ManifestScalar $Matches[2]
            continue
        }
        if ($null -ne $current -and $line -match '^    ([a-z_][a-z0-9_]*):\s*(.*)$') {
            $current[$Matches[1]] = ConvertFrom-ManifestScalar $Matches[2]
        }
    }

    $matches = @($assets | Where-Object { [string]$_.id -eq $AssetId })
    if ($matches.Count -ne 1) { throw "Manifest must contain exactly one asset named '$AssetId'." }
    $asset = $matches[0]
    if ([string]$asset.project -ne $Project -or [string]$asset.local_destination -ne $RelativeDestination) {
        throw "Adapter arguments do not match the manifest contract for '$AssetId'."
    }
    $hashMatch = [regex]::Match([string]$asset.integrity_rule, '(?i)SHA-256\s+([0-9a-f]{64})')
    if (-not $hashMatch.Success) { throw "Manifest asset '$AssetId' has no authoritative SHA-256." }
    return [pscustomobject]@{ ExpectedSha256 = $hashMatch.Groups[1].Value.ToLowerInvariant() }
}

function Assert-NoReparseAncestors([string]$Path) {
    $current = [System.IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Configured path contains a reparse point: $current"
            }
        }
        $parent = [System.IO.Path]::GetDirectoryName($current.TrimEnd('\', '/'))
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -eq $current) { break }
        $current = $parent
    }
}

function Assert-NoReparsePoint {
    param([string]$Path, [string]$Boundary)

    $boundaryFull = [System.IO.Path]::GetFullPath($Boundary).TrimEnd('\', '/')
    $candidateFull = [System.IO.Path]::GetFullPath($Path)
    $relative = $candidateFull.Substring($boundaryFull.Length).TrimStart('\', '/')
    $current = $boundaryFull
    if (Test-Path -LiteralPath $current) {
        $rootItem = Get-Item -LiteralPath $current -Force
        if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Project data boundary contains a reparse point: $current"
        }
    }
    foreach ($segment in @($relative -split '[/\\]' | Where-Object { $_ })) {
        $current = Join-Path $current $segment
        if (-not (Test-Path -LiteralPath $current)) { break }
        $item = Get-Item -LiteralPath $current -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Asset '$AssetId' path contains a reparse point: $current"
        }
    }
}

function Resolve-ContainedAssetPath {
    param([string]$Root, [string]$ProjectName, [string]$RelativePath)

    Assert-NoReparseAncestors $Root
    if ([System.IO.Path]::IsPathRooted($RelativePath) -or $RelativePath -match '(^|[/\\])\.\.([/\\]|$)') {
        throw "Asset '$AssetId' has an unsafe relative destination."
    }
    $projectRoot = [System.IO.Path]::GetFullPath((Join-Path $Root $ProjectName))
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $RelativePath))
    $prefix = $projectRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Asset '$AssetId' resolves outside its project data root."
    }
    Assert-NoReparsePoint -Path $candidate -Boundary $projectRoot
    return $candidate
}

function Get-Hash([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Copy-Immutable {
    param([string]$Source, [string]$Destination, [string]$ExpectedSha256)

    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        throw "Source asset is unavailable: $Source"
    }
    $sourceHash = Get-Hash $Source
    if ($sourceHash -ne $ExpectedSha256) {
        throw "Source asset does not match the manifest SHA-256: $AssetId"
    }
    if (Test-Path -LiteralPath $Destination) {
        if (-not (Test-Path -LiteralPath $Destination -PathType Leaf)) {
            throw "Destination exists but is not a file: $Destination"
        }
        $destinationHash = Get-Hash $Destination
        if ($destinationHash -eq $ExpectedSha256) {
            return [pscustomobject]@{ Result = 'PASS'; Match = $true; Sha256 = $sourceHash; Changed = $false }
        }
        return [pscustomobject]@{ Result = 'ATTENTION_REQUIRED'; Match = $false; Sha256 = $sourceHash; ExistingSha256 = $destinationHash; Changed = $false }
    }

    $parent = Split-Path $Destination -Parent
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    Assert-NoReparsePoint -Path $Destination -Boundary ([System.IO.Path]::GetDirectoryName($parent))
    $temporary = "$Destination.copying-$([guid]::NewGuid().ToString('N'))"
    try {
        Copy-Item -LiteralPath $Source -Destination $temporary
        if ((Get-Hash $temporary) -ne $ExpectedSha256) {
            throw "Copied asset failed SHA-256 verification: $AssetId"
        }
        Assert-NoReparsePoint -Path $Destination -Boundary ([System.IO.Path]::GetDirectoryName($parent))
        if (Test-Path -LiteralPath $Destination) {
            throw "Destination appeared during the copy and was not overwritten: $Destination"
        }
        [System.IO.File]::Move($temporary, $Destination)
        if (-not (Test-Path -LiteralPath $Destination -PathType Leaf) -or
            (Get-Hash $Destination) -ne $ExpectedSha256) {
            throw "Final asset failed exact-path verification: $AssetId"
        }
    }
    finally {
        if (Test-Path -LiteralPath $temporary) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
    return [pscustomobject]@{ Result = 'PASS'; Match = $true; Sha256 = $sourceHash; Changed = $true }
}

$contract = Get-ManifestAssetContract
$expectedSha256 = [string]$contract.ExpectedSha256
$localPath = Resolve-ContainedAssetPath -Root $DataRoot -ProjectName $Project -RelativePath $RelativeDestination
$syncPath = Resolve-ContainedAssetPath -Root $SyncRoot -ProjectName $Project -RelativePath $RelativeDestination

switch ($Action) {
    'Publish' {
        if ($RelativeDestination -match '^(private|backups)[/\\]') {
            return [pscustomobject]@{
                Result = 'ATTENTION_REQUIRED'
                Match = $false
                Changed = $false
                Reason = 'Private assets require an encrypted artifact before offsite publication.'
            }
        }
        return Copy-Immutable -Source $localPath -Destination $syncPath -ExpectedSha256 $expectedSha256
    }
    'Restore' { return Copy-Immutable -Source $syncPath -Destination $localPath -ExpectedSha256 $expectedSha256 }
    'Verify' {
        $localHash = Get-Hash $localPath
        $syncHash = Get-Hash $syncPath
        $match = $localHash -eq $expectedSha256 -and $syncHash -eq $expectedSha256
        return [pscustomobject]@{
            Result = if ($match) { 'PASS' } else { 'ATTENTION_REQUIRED' }
            Match = $match
            LocalSha256 = $localHash
            SyncSha256 = $syncHash
            Changed = $false
        }
    }
}
