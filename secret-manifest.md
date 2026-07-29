# Secret manifest

Project: kelly-uniforms-business

This generated view contains variable names and operating metadata only. Secret values, vault session keys, recovery keys, and access tokens are forbidden.

| Variable | Purpose | Provider | Trust boundary | Owner | Rotation | Consumers | Status |
|---|---|---|---|---|---|---|---|
| `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` | Ecwid password; value stays outside repository files and chat | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | approved bws-injected Ecwid browser login broker | broker-required |
| `MT_UNIFORMS_ECWID_ADMIN_USERNAME` | Ecwid login name; value stays outside repository files and chat | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | approved bws-injected Ecwid browser login broker | broker-required |
| `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` | Website-admin password; value stays outside repository files and chat | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | approved bws-injected website browser login broker | broker-required |
| `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` | Website-admin login name; value stays outside repository files and chat | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | approved bws-injected website browser login broker | broker-required |
| `PROJECT_DATA_ROOT` | Stable local root for client-provided inputs and generated project outputs | Windows environment or project launcher | local project data | Douglas | when the project data location changes | agents and project tooling | configured-value-required |

Canonical source: `secret-manifest.json`
Refresh: `C:\Users\dougl\.agents\tools\Update-SecretManifest.cmd -Repository <repo>`
