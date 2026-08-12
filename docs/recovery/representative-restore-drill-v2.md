# Representative restore drill v2

V2 preserves the frozen v1 fixture, reconstruction checks, synthetic-data classification, staged-import path, and authority-immutability checks. It changes authority verification so successor generations remain executable.

The drill reads `commerce_import.tool` from the authority's package manifest and loads that exact package-local verifier. The path must be a portable `tools/package_*_generation.py` path inside the authority. Absolute paths, traversal, nested paths, missing files, and tools without `verify_generation` are rejected.

The selected verifier runs before the disposable copy is created and again after reconstruction. The authority's package manifest, SQLite database, and checksum manifest hashes must remain unchanged.

```powershell
py tools\run_recovery_drill_v2.py run <verified-authority> <new-disposable-destination>
```

The output remains `synthetic-drill-never-client-data`, contains `DRILL-ONLY.json` with `promotable: false`, and must never replace a recovery authority.
