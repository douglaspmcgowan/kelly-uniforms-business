# REC-012 binary-ready recovery package evidence

## Outcome

REC-012 was created from the verified REC-011 authority and packages the OpenCart native-export capture, Ecwid JSON capture, Ecwid binary/media capture, staged importer, schemas, contracts, and package-local verification chain.

- Generation: `REC-012`
- Parent: `REC-011`
- Readiness: `opencart-and-ecwid-json-binary-tools-packaged-awaiting-authenticated-exports`
- Physical files: `4,495`
- Checksummed files: `4,494`
- Source-manifest rows: `537`
- Commerce tables: `35`
- Normalized/private rows: `0`
- SQLite integrity: `ok`
- Foreign-key errors: `0`
- Missing-media capture: `430 / 430`
- Public runtime capture: `34 / 35`; the sole inherited failure remains the retired AddThis reference.

## Authorities and hashes

Primary directory:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec012`

Restricted redundant directory:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\2026-08-10-rec012`

Primary and restricted directories each contain 4,495 files. The authority hashes match byte-for-byte:

- `package-manifest.json`: `2369c2dcadf7af50207dc0ddbb7e08646fec2265d891fcee95e7015a7230b5a2`
- `mt_uniforms_recovery.sqlite`: `5f49cfc2d02fd537167704fde5839e8475f3c696b9395d5e93feb3bdbd785e0a`
- `SHA256SUMS.txt`: `2448a4728daa3297a5eeb810bb70895da972c2bed81bc693b84e234c9dca70b7`

Primary archive:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec012.tar.gz`

Restricted redundant archive:
`C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\mt-uniforms-recovery-2026-08-10-rec012.tar.gz`

- Archive SHA-256, both copies: `a2157f29475e4679c05adb16e4a1ff137c2ba6214486e93fd27d6db687380b23`

## Verification

- Repository verifier: `py scripts\package_binary_ready_generation.py verify <primary>` passed.
- Isolated archive restore: extracted under `C:\Users\dougl\Data\Projects\kelly-uniforms-business\isolated-restores\rec012-20260810\2026-08-10-rec012`.
- Package-only verifier: invoked packaged `tools\package_binary_ready_generation.py` from `C:\Windows\Temp`; passed without repository imports.
- Full suite: `py -m unittest discover -s scripts -p "test_*.py"` passed 61 tests with one ordinary-symlink capability skip; the Windows junction/reparse regression executed and passed.
- Syntax: `py -m py_compile scripts\package_binary_ready_generation.py scripts\capture_ecwid_binaries.py` passed.
- Patch hygiene: `git diff --check` passed; existing line-ending warnings were informational.

## Remaining boundary

REC-012 proves that the acquisition and recovery toolchain is self-contained. It does not claim authenticated private exports were obtained. Those rows intentionally remain empty until an Ecwid API token with the declared read scopes and an OpenCart hosting/database export or valid attended admin session are available. Clover remains deferred by client decision.
