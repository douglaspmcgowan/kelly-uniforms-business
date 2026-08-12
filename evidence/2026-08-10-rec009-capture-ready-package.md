# REC-009 capture-ready recovery package and isolated restore

Date: 2026-08-10
Generation: `REC-009`
Parent: `REC-008`

## Result

Created an immutable successor recovery generation that preserves the verified REC-008 authority and packages the Ecwid core API capture adapter, importer v2, its payload contract, the capture runbook, and one package-local create/verify/stage-import interface.

Fresh REC-009 contains zero normalized private commerce rows and zero import runs. Authenticated private exports remain absent because the available OpenCart and Ecwid browser tabs were signed out and no secret token was available through an approved process boundary.

## Verification

- TDD red: `py -m unittest scripts.test_package_capture_ready_generation` failed three tests because `package_capture_ready_generation.py` did not exist.
- Focused green: the same command passed 3 tests.
- Real creation: `py scripts\package_capture_ready_generation.py create <REC-008> <REC-009>` returned `valid: true`, generation `REC-009`, parent `REC-008`, readiness `tools-packaged-awaiting-authenticated-exports`, and `normalized_rows: 0`.
- Package inventory: 4,482 checksummed files plus `SHA256SUMS.txt`; 525 `source_manifest` rows; SQLite integrity `ok`; zero foreign-key errors.
- Public authority: 430 previously missing media objects captured, 34 of 35 runtime dependencies present, and the sole retired AddThis dependency preserved as the known disposition.
- Isolated restore: extracted the archive outside the repository and ran `tools\package_capture_ready_generation.py verify` from `C:\Windows\Temp`; it returned `valid: true` using package-local tools only.
- Redundancy: primary and restricted copies matched for the package manifest, SQLite database, checksum manifest, and compressed archive.

## Authority paths

- Primary generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec009`
- Primary archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\archives\mt-uniforms-recovery-2026-08-10-rec009.tar.gz`
- Restricted redundant generation: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\2026-08-10-rec009`
- Restricted redundant archive: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\mt-uniforms-recovery-2026-08-10-rec009.tar.gz`
- Isolated restore: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\isolated-restores\rec009-20260810\2026-08-10-rec009`

## SHA-256 evidence

- `package-manifest.json`: `049596c065199b6663d831e783cecb23f1ca3ef60a53e7abcef6bc1a8258aa4a`
- `mt_uniforms_recovery.sqlite`: `e1072dc328d023e322a57745282c9aeb343092277e48230d7f30dc90c722237b`
- `SHA256SUMS.txt`: `0747a894ffc631a59cfbdf95c18564a1fa1786833fba21327e7e3632d532d35a`
- Archive: `a2866fb416469f62a1fe328ea5f5a40dd3d91a5e4da89bfea29b91fc0e780830` (123,627,727 bytes)

## Remaining boundary

The package is prepared to acquire and normalize authenticated exports, but it does not claim those exports exist. Ecwid adjunct resources/media and OpenCart native database, webroot, external storage, and Journal artifacts remain dependent on authenticated or hosting access.
