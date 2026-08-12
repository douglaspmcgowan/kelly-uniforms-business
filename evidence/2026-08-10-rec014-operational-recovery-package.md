# REC-014 operational recovery package attempt

## Proven behavior

REC-014 corrected the REC-013 generation-dispatch failure. Its mandatory pre-promotion self-test passed, its isolated packaged verifier passed, and its isolated packaged v2 drill passed against authority generation REC-014:

- staged import: reconciled;
- normalized rows: 22;
- lineage rows: 22;
- SQLite integrity: `ok`;
- foreign-key errors: 0;
- authority critical hashes unchanged;
- primary/restricted directory authority files and archives matched.

## Adversarial finding

The final physical-file reconciliation found 4,506 files but only 4,504 checksummed files plus `SHA256SUMS.txt`. The remaining file was:

`tools/__pycache__/package_operational_recovery_generation.cpython-314.pyc`

It was created when the generation-aware drill dynamically loaded the package verifier. The recovery checksum policy deliberately excludes Python cache files, so this bytecode was present but untracked. The same dynamic import could create a cache file in an otherwise immutable authority during a later drill.

## Ruling

REC-014 is preserved as a functionally successful but custody-incomplete checkpoint. It must not be promoted as the current authority. A successor must suppress bytecode during authority-verifier loading, remove inherited cache artifacts only in the successor build, reject every `__pycache__` directory and `.pyc` file, and repeat package-only verifier/drill/hash proof.

Primary archive SHA-256: `a37a96798b9d305aa322c77c5fbbc4de650ab895b269e367c877dacf391eb901`.
