# Representative restore drill v3

V3 preserves the frozen v1 reconstruction scenario and v2 manifest-directed verifier selection while making authority inspection bytecode-free.

Before importing any package-local module, V3 sets Python's `dont_write_bytecode` process flag. It rejects an authority containing any `__pycache__` directory or `.pyc` file before verifier loading, after verifier loading, after pre-drill verification, and after post-drill verification.

The verifier path remains restricted to a portable `tools/package_*_generation.py` file declared by the authority manifest. The drill retains the synthetic/non-promotable boundary, raw-first staging, full reconstruction checks, critical authority hashes, and disposable output.

```powershell
py tools\run_recovery_drill_v3.py run <verified-authority> <new-disposable-destination>
```

Success requires zero Python cache artifacts in the authority before and after the run.
