# MT Uniforms access setup

## Intended credential path

Use a dedicated Bitwarden Secrets Manager project for MT Uniforms. Create these four secrets by exact name:

- `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME`
- `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD`
- `MT_UNIFORMS_ECWID_ADMIN_USERNAME`
- `MT_UNIFORMS_ECWID_ADMIN_PASSWORD`

Enter each credential only in the corresponding Bitwarden secret value. Keep credential values, machine-account access tokens, and secret exports out of this repository, chat, screenshots, terminal output, and logs.

## Machine access

Grant a dedicated machine account read-only access to the MT Uniforms Secrets Manager project. The machine account's access token is machine bootstrap material and stays outside the repository.

The installed Bitwarden Secrets Manager CLI supports injecting project secrets as environment variables into one trusted process:

```powershell
bws run --project-id <BITWARDEN_PROJECT_ID> -- <APPROVED-BROKER>
```

The project ID is metadata, though it should be passed through machine-local configuration to keep the repository portable.

## Current control boundary

This computer has Bitwarden Secrets Manager CLI 2.1.0. The existing credential broker supports Bitwarden Password Manager only, and its executable allowlist is empty. A reviewed browser-login broker must be installed and allowlisted before an agent can consume these four Secrets Manager values in a browser session.

The public OpenCart administration login for the live storefront is:

<https://www.mtuniforms.com/admin/>

Use the website-admin secret pair for that login. The Ecwid secret pair belongs to the separate Ecwid control panel whose current operational role remains unverified.

Until that broker exists:

- storing the four secrets prepares the vault correctly;
- agents must not retrieve, print, or copy their values;
- the user completes any interactive login and MFA challenge;
- production changes require a preview, explicit target confirmation, and post-change verification.

## MFA

Keep MFA enabled. Handle a one-time code as a human challenge unless automated TOTP use is separately authorized and implemented through the same reviewed broker.

## References

- Bitwarden Secrets Manager CLI: <https://bitwarden.com/help/secrets-manager-cli/>
- Bitwarden machine accounts: <https://bitwarden.com/help/machine-accounts/>
- Bitwarden Secrets Manager secrets: <https://bitwarden.com/help/secrets/>
