# Secret manifest

Project: kelly-uniforms-business

This generated view contains variable names and operating metadata only. Secret values, vault session keys, recovery keys, and access tokens are forbidden.

| Variable | Purpose | Provider | Trust boundary | Owner | Rotation | Consumers | Status |
|---|---|---|---|---|---|---|---|
| `ECWID_SECRET_TOKEN` | Read-only Ecwid REST API token for immutable recovery capture; Bitwarden key mtuniforms.ECWID_SECRET_TOKEN in the Agent Runtime project | Bitwarden Secrets Manager | client production recovery capture | Douglas | on compromise, capture completion, scope change, or provider policy | bws command mtuniforms-ecwid-complete-capture, scripts/capture_ecwid_api_v2.py, scripts/capture_ecwid_binaries.py | awaiting-value-and-broker-registration |
| `MT_UNIFORMS_ECWID_ADMIN_PASSWORD` | Ecwid control-panel password; Bitwarden key mtuniforms.ECWID_ADMIN_PASSWORD in the Agent Runtime project | Bitwarden Secrets Manager | client production administration | Douglas | rotate now; partially exposed in a prior agent session transcript | bws command mtuniforms-ecwid-admin-login | awaiting-value |
| `MT_UNIFORMS_ECWID_ADMIN_USERNAME` | Ecwid control-panel login name; Bitwarden key mtuniforms.ECWID_ADMIN_USERNAME in the Agent Runtime project | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | bws command mtuniforms-ecwid-admin-login | awaiting-value |
| `MT_UNIFORMS_WEBSITE_ADMIN_PASSWORD` | OpenCart administration password; Bitwarden key mtuniforms.WEBSITE_ADMIN_PASSWORD in the Agent Runtime project | Bitwarden Secrets Manager | client production administration | Douglas | ROTATE NOW; this value was pasted in cleartext into a prior agent session and is stored in a local transcript | bws command mtuniforms-opencart-admin-login | rotation-required |
| `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` | OpenCart administration login name; Bitwarden key mtuniforms.WEBSITE_ADMIN_USERNAME in the Agent Runtime project | Bitwarden Secrets Manager | client production administration | Douglas | on compromise, ownership change, or provider policy | bws command mtuniforms-opencart-admin-login | awaiting-value |
| `PROJECT_DATA_ROOT` | Stable local root for client-provided inputs and generated project outputs | Windows environment or project launcher | local project data | Douglas | when the project data location changes | agents and project tooling | configured-value-required |

Canonical source: `secret-manifest.json`
Refresh: `C:\Users\dougl\.agents\tools\Update-SecretManifest.cmd -Repository <repo>`
