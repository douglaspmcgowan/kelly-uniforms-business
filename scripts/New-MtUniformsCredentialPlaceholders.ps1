<#
.SYNOPSIS
Creates empty MT Uniforms credential placeholders in Bitwarden so Douglas can
fill in the values himself.

.DESCRIPTION
Creates two Bitwarden Password Manager login items with EMPTY username and
password fields:

  MT Uniforms - OpenCart Website Admin   (https://www.mtuniforms.com/admin/)
  MT Uniforms - Ecwid Admin              (https://my.ecwid.com/)

Optionally also creates the four value-free Secrets Manager secrets named in
ACCESS.md, when the Secrets Manager CLI (bws) is installed and a machine-account
token is available.

This script never reads, prints, or logs a credential value. It writes empty
strings only. Douglas opens Bitwarden afterwards and types the real values in.

.PARAMETER Folder
Bitwarden folder name to place the items in. Created if missing.

.PARAMETER WhatIf
Show what would be created without creating it.

.EXAMPLE
  bw login          # only if never logged in on this machine
  $env:BW_SESSION = bw unlock --raw
  pwsh -File .\scripts\New-MtUniformsCredentialPlaceholders.ps1

.NOTES
Run this yourself. Do not paste BW_SESSION, tokens, or passwords into an agent
chat, a repository file, or a terminal transcript that is shared.
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Folder = 'MT Uniforms'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$bw = (Get-Command bw -ErrorAction SilentlyContinue)?.Source
if (-not $bw) {
    throw 'The Bitwarden CLI (bw) was not found on PATH. Install it, then re-run.'
}

$status = (& $bw status | ConvertFrom-Json).status
if ($status -ne 'unlocked') {
    throw "The Bitwarden vault is '$status', not 'unlocked'. Run: `$env:BW_SESSION = bw unlock --raw"
}

& $bw sync | Out-Null

# --- folder -----------------------------------------------------------------
$folderId = $null
$existingFolder = (& $bw list folders | ConvertFrom-Json) |
    Where-Object { $_.name -eq $Folder } | Select-Object -First 1
if ($existingFolder) {
    $folderId = $existingFolder.id
    Write-Output "Folder '$Folder' already exists."
}
elseif ($PSCmdlet.ShouldProcess("Bitwarden folder '$Folder'", 'create')) {
    $folderJson = & $bw get template folder | ConvertFrom-Json
    $folderJson.name = $Folder
    $folderId = ($folderJson | ConvertTo-Json -Compress |
        & $bw encode | & $bw create folder | ConvertFrom-Json).id
    Write-Output "Created folder '$Folder'."
}

# --- login items ------------------------------------------------------------
$items = @(
    @{
        Name  = 'MT Uniforms - OpenCart Website Admin'
        Uri   = 'https://www.mtuniforms.com/admin/'
        Notes = @(
            'OpenCart administration for the live mtuniforms.com storefront.'
            'Controls: Journal 3 theme modules and layouts (including the Header Notice),'
            'catalog, products, orders, customers, payment/shipping config, store URL.'
            'This is the login required to publish the temporary ordering notice (DEL-001).'
            'Leave username/password empty here until Douglas fills them in.'
        ) -join "`n"
    },
    @{
        Name  = 'MT Uniforms - Ecwid Admin'
        Uri   = 'https://my.ecwid.com/'
        Notes = @(
            'Separate Ecwid commerce control panel supplied by the client.'
            'As of the 2026-07-31 public scope, Ecwid renders NO part of mtuniforms.com.'
            'Its current role is unverified: possibly abandoned, a back-office catalog,'
            'or a separate sales channel. Needed only to answer that question (DEL-002).'
            'Leave username/password empty here until Douglas fills them in.'
        ) -join "`n"
    }
)

$existingItems = & $bw list items --search 'MT Uniforms' | ConvertFrom-Json

foreach ($spec in $items) {
    $already = $existingItems | Where-Object { $_.name -eq $spec.Name } | Select-Object -First 1
    if ($already) {
        Write-Output "Item '$($spec.Name)' already exists - left untouched."
        continue
    }
    if (-not $PSCmdlet.ShouldProcess("Bitwarden login item '$($spec.Name)'", 'create with empty credentials')) {
        continue
    }

    $item = & $bw get template item | ConvertFrom-Json
    $item.type = 1
    $item.name = $spec.Name
    $item.notes = $spec.Notes
    $item.folderId = $folderId

    $login = & $bw get template item.login | ConvertFrom-Json
    $login.username = ''
    $login.password = ''
    $login.totp = ''
    $uri = & $bw get template item.login.uri | ConvertFrom-Json
    $uri.uri = $spec.Uri
    $uri.match = $null
    $login.uris = @($uri)
    $item.login = $login

    $item | ConvertTo-Json -Depth 10 -Compress | & $bw encode | & $bw create item | Out-Null
    Write-Output "Created '$($spec.Name)' with EMPTY username and password."
}

& $bw sync | Out-Null

Write-Output ''
Write-Output 'Done. Open Bitwarden and fill in the two items.'
Write-Output 'Nothing in this script read, printed, or stored a credential value.'
