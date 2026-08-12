# Cache-free operational recovery package contract v1

REC-015 supersedes REC-014 after the latter's self-test created an excluded, unchecksummed Python cache file.

REC-015 sets Python's no-bytecode flag before package imports, removes inherited cache files only in the successor build, rejects every `__pycache__` directory and `.pyc` file, and requires:

`physical files = checksummed files + SHA256SUMS.txt`

The package-local V3 drill runs before promotion and must leave the authority cache-free and unchanged while reconstructing the 22-row representative agency transaction in a disposable copy.

```powershell
py tools\package_clean_recovery_generation.py verify <recovery-root>
py tools\run_recovery_drill_v3.py run <recovery-root> <new-disposable-destination>
py tools\package_clean_recovery_generation.py stage-import <recovery-root> <export-manifest>
```

Fresh REC-015 private rows remain zero. Authenticated OpenCart/Ecwid sources, primary account-control evidence, and approved encrypted offsite custody remain required for full completion. Clover authenticated export remains excluded by DEC-005.
