# Operational recovery package contract v1

REC-014 supersedes the structurally valid but package-drill-failed REC-013 checkpoint. REC-013 remains immutable failure evidence.

REC-014 packages the generation-aware v2 representative drill and runs that package-local tool against the REC-014 build before the build can be promoted. Proof is recorded only when the drill reports:

- valid reconstruction;
- reconciled staged import;
- unchanged authority hashes;
- zero foreign-key errors;
- 22 normalized and 22 lineage rows in the disposable copy.

The disposable self-test output is removed after verification. The REC-014 authority keeps zero private commerce/import rows.

## Commands

```powershell
py tools\package_operational_recovery_generation.py verify <recovery-root>
py tools\run_recovery_drill_v2.py run <recovery-root> <new-disposable-destination>
py tools\package_operational_recovery_generation.py stage-import <recovery-root> <export-manifest>
```

The verifier fails closed if the drill proof, current REC-014 status documents, service/account inventory, packaged dependencies, checksum inventory, SQLite integrity, lineage, or fresh-empty authority boundary is invalid.

Authenticated OpenCart/Ecwid source bytes, primary account-control evidence, and approved encrypted offsite custody remain required for full business recovery. Clover authenticated export remains excluded by DEC-005.
