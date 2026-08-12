# MT Uniforms access setup

Last verified on this workstation: 2026-08-10.

## The two logins and why both exist

| Login | URL | What it controls | Needed for |
|---|---|---|---|
| **OpenCart website admin** | <https://www.mtuniforms.com/admin/> | The live storefront. Journal 3 theme modules and layouts (including the Header Notice), catalog and products, orders, customers, information pages, payment/shipping configuration, store URL, error log. | Everything real. `DEL-001` (the notice) and the `DEL-002` host-split fix both live here. |
| **Ecwid control panel** | <https://my.ecwid.com/> (client-supplied) | A separate hosted commerce product with its own catalog, cart, and checkout. Independent of OpenCart. | Answering one question only: what is this account still doing? |

They are two different commerce platforms, not two doors into the same system.
The client supplied both during intake.

**Current evidence on Ecwid:** the 2026-07-31 public scope found no Ecwid script,
asset, iframe, or URL on the home, category, contact, cart, or checkout routes.
Ecwid renders no part of the public site. Three possibilities remain — an
abandoned account, a back-office catalog that feeds OpenCart, or a separate sales
channel (Facebook/Instagram/marketplace) — and only an authenticated look
distinguishes them. Evidence: `evidence/2026-07-31-site-architecture-scope.md`.

Practical consequence: **the OpenCart login is the only one on the critical path.**
The Ecwid login can wait.

## What Douglas has to do to unblock agent login

Pick one path.

### Path A — Douglas signs in, agent drives the session (fastest, no build)

1. Open <https://www.mtuniforms.com/admin/> in the in-app Browser pane.
2. Type the username and password yourself, complete any MFA challenge.
3. Say "you're in, proceed."

The agent then works inside the authenticated session without ever seeing the
credential values. This needs no new tooling and can start immediately. It is
attended: Douglas must be at the keyboard for the sign-in.

### Path B — Agent logs in unattended through the Bitwarden broker

**Broker software is ready, but shared-harness registration is not.** Current
inspection on 2026-08-09 found:

- `scripts\broker\opencart-admin-login.mjs` and `ecwid-admin-login.mjs` —
  headless Playwright login brokers that read their credentials from the
  environment, never print or write a value, scrub the password from any output,
  save an authenticated storage state outside the repository, and exit non-zero
  on failure including an MFA challenge.
- The current `C:\Users\dougl\.agents\tools\bws-command-allowlist.json` has no
  MT Uniforms entries. The previously documented placeholder entries are stale
  and must be restored only after the non-secret Bitwarden IDs are available.
- `secret-manifest.json` updated with the Bitwarden key names under the harness
  `Agent Runtime` project convention.

- **`bws.exe` 2.1.0 installed** at `%USERPROFILE%\Tools\bws\bws.exe`, the broker's
  pinned path. Downloaded from Bitwarden's official `bitwarden/sdk-sm` release
  `bws-v2.1.0` and **verified against their published SHA-256 checksum**
  (`8d6f2b51…f2bd5`). The harness responsibility table lists installing or
  verifying this executable as agent-permitted work.
- **Playwright installed** in `scripts\broker\` and self-tested: headless Chromium
  launches, reaches the live admin page, and all three selectors the broker
  depends on (`input[name="username"]`, `input[name="password"]`,
  `button[type="submit"]`) match the real OpenCart login form.

**Verification boundary.** The broker scripts pass syntax inspection and their
Playwright selectors were previously exercised against the live login page. The
full shared-harness command cannot currently run because its two MT Uniforms
allowlist entries are absent and no approved machine token/resource binding is
provisioned.

**Secrets Manager setup — five value-safe steps, followed by one agent step.** The harness responsibility boundary
(`C:\Users\dougl\.agents\capsule\SECRETS-BITWARDEN.md`) reserves these to him, and
an agent must not perform them:

1. **Create the five secrets** in the `Agent Runtime` Secrets Manager project
    using the prefixed convention: `mtuniforms.WEBSITE_ADMIN_USERNAME`,
    `mtuniforms.WEBSITE_ADMIN_PASSWORD`, `mtuniforms.ECWID_ADMIN_USERNAME`,
    `mtuniforms.ECWID_ADMIN_PASSWORD`, and `mtuniforms.ECWID_SECRET_TOKEN`.
    Values go in Bitwarden only. The last is a scoped, read-only Ecwid API token,
    not the Ecwid control-panel password.
2. **Give the machine account read access** to that project, generate a token,
    then run `C:\Users\dougl\.agents\tools\Set-BwsMachineToken.ps1` and paste it
    at the secure prompt. Never paste it into chat.
3. **Hand back the non-secret project ID and five resource IDs** so the allowlist
    entries can be created. IDs carry no secret value and are safe to send.
4. **Approve the capture command's attendance mode.** An interactive run is the
   default. For an unattended recovery run, Douglas must create the broker's
   per-command unattended grant with his name and date; an agent may not create
   or widen that grant.
5. **Set the least-privilege Ecwid API scopes** before the capture: catalog,
   orders, customers, profile, and only the optional adjunct scopes actually
   needed by the runbook. The token must be provisioned to the `ECWID_SECRET_TOKEN`
   runtime variable by the reviewed `mtuniforms-ecwid-complete-capture` command.

After those steps, the agent can add and verify the reviewed allowlist commands,
then run OpenCart first and Ecwid second. Hosting recovery still needs
a separate value-safe control-panel, SFTP/SSH, or database-export path.

The command remains attended unless its explicit unattended grant exists.

**MFA remains a hard blocker on this path.** If the OpenCart admin requires a
one-time code, unattended login is not possible without separately authorized
TOTP handling. Use Path A in that case.

### Historical note — what was missing before this session

1. **Install the Bitwarden Secrets Manager CLI at the pinned path.**
   `C:\Users\dougl\.agents\tools\Invoke-WithBitwardenSecret.ps1` requires
   `%USERPROFILE%\Tools\bws\bws.exe`. Verified 2026-07-31: `bws` is **not on
   PATH and not installed**. An earlier note in this file claiming
   "Bitwarden Secrets Manager CLI 2.1.0" on this machine was wrong and is
   retired.
2. **Store a read-only machine-account token.** Run
   `C:\Users\dougl\.agents\tools\Set-BwsMachineToken.ps1` and paste the token at
   its secure prompt. It stores the token in Windows Credential Manager under
   `AgentHarness/BitwardenSecretsManager`. Do not paste the token into chat.
3. **Create the four secrets and a Secrets Manager project**, then note the
   project ID and the four resource IDs (IDs are metadata, not secrets).
4. **Write and allowlist a login broker.** This is the real work. The existing
   broker injects secrets as environment variables into **one pre-approved
   non-interactive executable** listed in
   `C:\Users\dougl\.agents\tools\bws-command-allowlist.json`. It cannot drive a
   browser by itself. Someone has to write a headless Playwright script that
   reads `MT_UNIFORMS_WEBSITE_ADMIN_USERNAME` / `..._PASSWORD` from its own
   environment, posts them to the OpenCart login form, and hands back a session
   — then register that script as a new allowlist entry.

   MFA is an open blocker on this path: OpenCart admin MFA, if enabled, needs a
   TOTP secret and separate authorization before unattended login can work.

**Recommendation: Path A for the immediate notice work, Path B for anything
recurring.** Path A is 30 seconds; Path B is now five short steps for Douglas.

### Live-session audit — 2026-08-10

The existing in-app OpenCart administration tab was claimed and inspected; it
resolved to the standard OpenCart login form, so its previous authenticated
session had expired. A separate Ecwid control-panel navigation resolved to
`Login | Ecwid Ecommerce`. Browser discovery exposed no second connected
browser family or authenticated session. No cookie, session store, saved
password, or credential value was inspected. This confirms that Path A still
requires a fresh human sign-in and Path B still requires the non-secret
Bitwarden project/resource bindings described above.

## CREDENTIAL ROTATION REQUIRED

The OpenCart administrator password was pasted in cleartext into a prior agent
session and is stored unencrypted in a local session transcript, as well as in
the originating chat history.

1. Change the OpenCart administrator password at the admin URL.
2. Store the new value only in Bitwarden.
3. Treat the old value as compromised and do not reuse it.

Deleting the transcript does not undo the exposure. Rotation is the only
remediation. The Ecwid credential was partially exposed the same way; rotate it
too. See `evidence/2026-07-31-codex-session-reconciliation.md`.

## Placeholder entries for Douglas to fill in

`scripts\New-MtUniformsCredentialPlaceholders.ps1` creates two Bitwarden Password
Manager login items with **empty** username and password fields:

- `MT Uniforms - OpenCart Website Admin`
- `MT Uniforms - Ecwid Admin`

Run it yourself after unlocking the vault:

```powershell
$env:BW_SESSION = bw unlock --raw
pwsh -File .\scripts\New-MtUniformsCredentialPlaceholders.ps1
```

The Bitwarden CLI (`bw`) is installed on this machine and was `unauthenticated`
on 2026-07-31, so `bw login` may be needed first. The script writes empty strings
only and never reads, prints, or logs a value.

## Browser tooling — in-app browser vs. Claude in Chrome vs. Playwright

Three different surfaces, three different jobs.

| | In-app Browser pane | Claude in Chrome | Playwright |
|---|---|---|---|
| Session | Its own profile, starts logged out | **Douglas's real Chrome, with existing logins** | Fresh context each run, or a saved storage state |
| Who drives | Agent, after a human signs in | Agent, in the live browser | Script, headless |
| Repeatable | No | No | **Yes — same steps every time** |
| Unattended / scheduled | No | No | **Yes** |
| Credential handling | Human types them | Human types them | Injected as env vars by the broker; never seen by the agent |
| Evidence output | Screenshots, a11y tree | Screenshots, a11y tree | Screenshots, video, trace, network log, assertions |
| Blast radius | One tab | **Every logged-in account in that Chrome profile** | Isolated |
| Best for | Attended one-off admin work | Reaching something only the real profile is logged into | Regression checks, verification, unattended login |

### Answering the direct question

**Yes — for the OpenCart admin work, opening the tab and working in it is the
right call.** Sign in once, hand it over, and the agent does the Journal module
edits directly. Playwright would be slower and would add nothing: the task is a
handful of one-time clicks in an admin UI, and every step needs human judgement
about what the installed theme actually exposes.

### Where Playwright genuinely wins

1. **Unattended login.** Only Playwright can consume a Bitwarden-brokered
   credential without a human at the keyboard. That is the entire Path B build.
2. **Repeatable verification.** "Confirm the notice renders on home, category,
   product, and cart at desktop and mobile widths" is four routes × two
   viewports, re-run after every change. A script does it identically each time
   and produces artifacts.
3. **Real mobile emulation.** Journal's own documentation warns that resizing a
   desktop window does not test device-specific module status. Playwright sets a
   genuine mobile user agent and device profile.
4. **Traces and network logs** — the evidence that proved the www/non-www CORS
   failure came from scripted HTTP inspection, not from looking at a page.
5. **Isolation.** A script runs in a clean context. Claude in Chrome operates
   inside the real profile, where a mistake reaches every logged-in account.

### Practical rule for this project

- **Attended admin changes** (publishing the notice, inspecting module 56) →
  in-app Browser pane after Douglas signs in.
- **Verification after any change** → Playwright, scripted, artifacts committed
  as evidence.
- **Claude in Chrome** → only when something needs a session that already exists
  in the real profile. Prefer the other two; the blast radius is larger.

Playwright browsers are already installed on this machine
(`%LOCALAPPDATA%\ms-playwright`). The broker scripts under `scripts\broker\`
need one `npm install` in that folder before they can run.

## Standing rules

- Credential values, machine-account tokens, `BW_SESSION`, and secret exports
  stay out of this repository, chat, screenshots, terminal output, and logs.
- Keep MFA enabled. Treat a one-time code as a human challenge unless automated
  TOTP is separately authorized and implemented through the reviewed broker.
- Production changes require a preview, explicit target confirmation, and
  post-change verification.

## References

- Bitwarden Secrets Manager CLI: <https://bitwarden.com/help/secrets-manager-cli/>
- Bitwarden machine accounts: <https://bitwarden.com/help/machine-accounts/>
- Bitwarden Secrets Manager secrets: <https://bitwarden.com/help/secrets/>
- Bitwarden Password Manager CLI: <https://bitwarden.com/help/cli/>
