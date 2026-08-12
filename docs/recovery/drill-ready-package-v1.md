# Drill-ready recovery package contract v1

REC-013 is the current offline recovery authority. It inherits REC-012 and adds:

- the package-local representative agency-order restore drill;
- a value-free service/account-control continuity inventory;
- current root recovery status and completion audit documents generated for REC-013;
- explicit separation between proven public/offline recovery, tool-ready authenticated acquisition, and unavailable primary account evidence.

## Package-local commands

```powershell
py tools\package_drill_ready_generation.py verify <recovery-root>
py tools\run_recovery_drill.py run <recovery-root> <new-disposable-destination>
py tools\package_drill_ready_generation.py stage-import <recovery-root> <export-manifest>
```

The drill creates a synthetic, permanently non-promotable copy. It never populates the REC-013 authority. Fresh private commerce and import rows in REC-013 remain zero until authenticated source exports are staged.

`RECOVERY-STATUS.md`, `COMPLETION-AUDIT.md`, and `business-continuity/service-account-control-inventory.json` are current package-level operational documents. Earlier inherited generations remain immutable historical evidence.

REC-013 does not claim private OpenCart or Ecwid data, hosting files, registrar control, account payer/renewal evidence, or encrypted offsite custody. Clover authenticated export remains excluded by DEC-005.
