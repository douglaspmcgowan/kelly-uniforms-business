# REC-015 cache-free operational recovery evidence

## Outcome

REC-015 is the current verified offline recovery authority. It supersedes the preserved REC-013 verifier-dispatch failure and REC-014 unchecksummed-bytecode checkpoint.

- Generation: `REC-015`
- Parent: `REC-014`
- Readiness: `cache-free-operational-recovery-self-test-proven-awaiting-authenticated-exports`
- Drill status: `proven-cache-free-package-local-copy`
- Physical files: 4,509
- Checksummed files: 4,508 plus `SHA256SUMS.txt`
- Source-manifest rows: 553
- Python cache artifacts: 0
- Private normalized/import rows: 0
- Service/account-control inventory: 10 value-free services
- SQLite integrity: `ok`
- Foreign-key errors: 0

## Recovery drill

The package-local V3 drill ran during creation before promotion and again from the isolated archive extraction under `C:\Windows\Temp`.

- authority generation selected from manifest: `REC-015`
- authority unchanged: yes
- authority cache artifacts after drill: 0
- staged import: reconciled
- normalized rows in disposable copy: 22
- lineage rows: 22
- fulfilled quantity: 2
- returned quantity: 1
- order total: 12,500 minor units
- payment: 12,500 minor units
- partial refund: 2,500 minor units
- disposable output: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\isolated-restores\rec015-agency-drill-20260810`

## Authorities and hashes

Primary:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec015`

Restricted redundant copy:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\2026-08-10-rec015`

Isolated restore:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\isolated-restores\rec015-20260810\2026-08-10-rec015`

All three contain 4,509 files, zero cache artifacts after package-only verification/drill, and matching critical hashes:

- `package-manifest.json`: `8112b942f5d400f14e5a7a92375e55d95b1cebc5239313618e40be770584d55b`
- `mt_uniforms_recovery.sqlite`: `0f89a430d2159e0ae85de915ffa8acf093cec4973e9d4ab9146e61aa0b0f1e7a`
- `SHA256SUMS.txt`: `d255d5c435f80737a6f27b67928a3d1105df4af55226861382e347e65afeef3e`
- `RECOVERY-STATUS.md`: `b4c52e2a30aa68ad3303169a4ac1c0e850f742ec6512970cd8ae93953774e424`
- `COMPLETION-AUDIT.md`: `b1727a3729ab464f33836169de7f4509a94961fb8949d60fe86aa7c57e0eef01`
- service/account inventory: `531768dd463e34d91b48be530a753bff198499273c264e165dc9f7e168305fed`

Primary archive:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec015.tar.gz`

Restricted archive:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\mt-uniforms-recovery-2026-08-10-rec015.tar.gz`

- archive SHA-256, both copies: `ea8ed13e562e2d3e9f564cfcf07da5916973359a29fca8f8dc31b58e13bb1774`

## Verification

- Package verifier from isolated extraction and `C:\Windows\Temp`: passed.
- V3 drill from isolated extraction and `C:\Windows\Temp`: passed.
- Physical/checksum equality: passed.
- Primary/restricted/isolated critical-byte identity: passed.
- Full repository suite: 73 tests passed, one ordinary-symlink capability skip; Windows junction/reparse tests executed.
- Syntax checks: passed.
- `git diff --check`: passed with informational pre-existing line-ending warnings.

## Remaining boundary

REC-015 proves all currently closable offline acquisition, preservation, import, provenance, representative-reconstruction, and custody-integrity pathways. It intentionally does not claim unavailable authenticated OpenCart/Ecwid exports, primary account-control records, or encrypted offsite custody. Clover authenticated export remains excluded by DEC-005.
