[CmdletBinding()]
param(
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$productName = 'Elbeco Tek2 Cargo Pocket Trousers'
$wwwOrigin = 'https://www.mtuniforms.com'
$bareOrigin = 'https://mtuniforms.com'
$addUri = "$wwwOrigin/index.php?route=checkout/cart/add"
$cartPath = '/index.php?route=checkout/cart'
$session = [Microsoft.PowerShell.Commands.WebRequestSession]::new()
$session.UserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/127 Safari/537.36'

$body = @{
    product_id = '814'
    quantity = '1'
    'option[845]' = '4824'
    'option[846]' = '4839'
    'option[847]' = '4854'
}

$addResponse = Invoke-WebRequest -Uri $addUri -Method Post -WebSession $session `
    -ContentType 'application/x-www-form-urlencoded; charset=UTF-8' -Body $body
$addJson = $addResponse.Content | ConvertFrom-Json
$wwwCart = Invoke-WebRequest -Uri "$wwwOrigin$cartPath" -WebSession $session
$bareCart = Invoke-WebRequest -Uri "$bareOrigin$cartPath" -WebSession $session

$wwwCookieMetadata = @(
    $session.Cookies.GetCookies([uri]"$wwwOrigin/") |
        ForEach-Object { [ordered]@{ name = $_.Name; domain = $_.Domain; path = $_.Path; secure = $_.Secure } }
)
$bareCookieMetadata = @(
    $session.Cookies.GetCookies([uri]"$bareOrigin/") |
        ForEach-Object { [ordered]@{ name = $_.Name; domain = $_.Domain; path = $_.Path; secure = $_.Secure } }
)
$sessionCookies = @($wwwCookieMetadata | Where-Object name -eq 'OCSESSID')

$result = [ordered]@{
    schema_version = 1
    captured_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    product = [ordered]@{
        public_product_id = 814
        name = $productName
        selected_option_value_ids = @(4824, 4839, 4854)
    }
    add_to_cart = [ordered]@{
        request_host = 'www.mtuniforms.com'
        http_status = [int]$addResponse.StatusCode
        success = -not [string]::IsNullOrWhiteSpace([string]$addJson.success)
        generated_cart_link_uses_bare_host = ([string]$addJson.success -match 'https://mtuniforms\.com/index\.php\?route=checkout/cart')
    }
    cart_reads = [ordered]@{
        www = [ordered]@{ http_status = [int]$wwwCart.StatusCode; contains_added_product = ($wwwCart.Content -match [regex]::Escape($productName)) }
        bare = [ordered]@{ http_status = [int]$bareCart.StatusCode; contains_added_product = ($bareCart.Content -match [regex]::Escape($productName)) }
    }
    cookie_metadata = [ordered]@{
        www = $wwwCookieMetadata
        bare = $bareCookieMetadata
        session_cookie_domains = @($sessionCookies | ForEach-Object domain | Sort-Object -Unique)
        values_recorded = $false
    }
    conclusion = 'confirmed-www-bare-host-session-split'
}

if (-not $result.add_to_cart.success) { throw 'Option-complete add-to-cart did not return success.' }
if (-not $result.add_to_cart.generated_cart_link_uses_bare_host) { throw 'Successful add did not generate the expected bare-host cart link.' }
if (-not $result.cart_reads.www.contains_added_product) { throw 'The www-host cart did not retain the added product.' }
if ($result.cart_reads.bare.contains_added_product) { throw 'The bare-host cart unexpectedly retained the www-host session product.' }
if ($sessionCookies.Count -eq 0) { throw 'No OCSESSID cookie was observed after add-to-cart.' }
if (@($sessionCookies | Where-Object { $_.domain -notmatch '(^|\.)www\.mtuniforms\.com$' }).Count -gt 0) {
    throw 'The observed OpenCart session cookie was not scoped to the www host.'
}

$json = $result | ConvertTo-Json -Depth 8
if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
    $parent = Split-Path -Parent $resolvedOutput
    if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    [System.IO.File]::WriteAllText($resolvedOutput, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
}

$json
