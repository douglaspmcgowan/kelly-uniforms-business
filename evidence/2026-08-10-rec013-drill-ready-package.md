# REC-013 drill-ready package attempt

## Ruling

REC-013 is an immutable failed checkpoint and must not be treated as the current recovery authority.

Package creation and the package-local structural verifier passed. An additional package-local representative drill from the isolated extraction failed before copying or importing data because `tools/run_recovery_drill.py` dispatched REC-013 to the hard-coded REC-012 verifier. The older verifier correctly rejected the successor generation.

Observed failure:

- isolated package: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\isolated-restores\rec013-20260810\2026-08-10-rec013`
- command: packaged `tools\run_recovery_drill.py run <REC-013> <disposable-destination>` from `C:\Windows\Temp`
- result: failed with `ValueError: package generation is not REC-012`
- data mutation: none; failure occurred during the initial authority-verification gate

## Corrective action

A regression test was added that requires the drill to select the verifier declared by the authority manifest. The drill now loads the allowed package-local `tools/package_*_generation.py` verifier and reuses it for both pre- and post-drill authority checks.

REC-013 remains preserved as evidence. The corrected tool must be packaged into a successor generation and the package-only representative drill must pass before that successor is promoted.
