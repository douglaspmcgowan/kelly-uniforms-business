# Task

## Goal

Publish the requested temporary ordering notice through an authorized, reversible production edit.

## Active

<!-- No active production work is authorized. -->

## Queue

- [ ] T1 — Authenticate at the verified OpenCart administration URL and confirm the installed Journal controls and permissions. | after: D1, D2 | evidence: authenticated identity and current Journal configuration verified
- [ ] T2 — Preview the temporary notice in Admin Only mode and verify it on desktop and mobile. | after: T1 | evidence: preview captures and acceptance checks pass
- [ ] T3 — Publish the notice, verify the public storefront, and record the rollback state. | after: T2 | evidence: public desktop/mobile checks and recovery record pass

## Blocked

- [!] D1 — Confirm that the four website-admin Secrets Manager records are populated and that the order email and phone line are ready. | evidence: value-free readiness confirmation

## Needs decision

- [?] D2 — Choose the authorized manual-login path or approve and complete the reviewed Secrets Manager-to-browser broker. | after: D1 | evidence: selected access path recorded without credential values

## Completed

- [x] Project source, client constraints, access contract, website runbook, and prior task state reviewed.
- [x] Legacy task files preserved verbatim under `.agents/archive/pre-harness-v3/`.
- [x] Initial local repository baseline committed before harness onboarding.
- [x] T0 — Established and verified the local harness v3 baseline without publishing or editing the live website. | evidence: project verifier, client/data tests, seven asset hashes, Gitleaks, and local commit

## Constraints

- Keep credentials in Bitwarden Secrets Manager; never place secret values in repository files, logs, screenshots, or chat.
- Do not enumerate Bitwarden projects or secrets. Use only exact allowlisted identifiers.
- Do not change DNS, hosting, mail, payment settings, or unrelated storefront content.
- Preview before publication and preserve a verified rollback path.
- Keep this onboarding local: no remote, push, pull request, deployment, or live website edit is authorized by the onboarding task.

## Verification

- Next: `C:\Users\dougl\.agents\tools\Test-AgentProjectState.cmd -Repository C:\tmp\onboard-kelly-uniforms`
