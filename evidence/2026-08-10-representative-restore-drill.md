# Representative agency-order restore drill evidence

## Outcome

The drill passed against a disposable copy of the real REC-012 authority.

- Authority: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\backups\business-continuity\2026-08-10-rec012`
- Disposable output: `C:\Users\dougl\Data\Projects\kelly-uniforms-business\isolated-restores\rec012-agency-drill-20260810`
- Classification: `synthetic-drill-never-client-data`
- Authority unchanged: yes
- Import run: `synthetic-restore-drill-v1`
- Import status: `reconciled`
- Normalized rows: 22
- Source-manifest rows added: 5
- Lineage rows: 22
- Package checksummed files after drill: 4,501
- Package source-manifest rows after drill: 542
- SQLite integrity: `ok`
- Foreign-key errors: 0

## Reconstructed scenario

The disposable database contains one linked row in each required table: business account, account member, tax exemption, entitlement, product, variant, price list, price-list entry, order, order line, customization, purchase order, invoice, payment, refund, fulfillment, fulfillment line, return, return line, production work order, production operation, and audit event.

Financial and quantity checks:

- order total: 12,500 minor units;
- payment: 12,500 minor units;
- partial refund: 2,500 minor units;
- fulfilled quantity: 2;
- returned quantity: 1.

## Commands and verification

- TDD red: `py -m unittest scripts.test_run_recovery_drill` failed twice because `run_recovery_drill.py` did not exist.
- Contract-pressure failures during implementation identified and corrected mixed-entity snapshot packaging, incomplete monetary-reconciliation fields, and the package-manifest prerequisite.
- Focused green: `py -m unittest scripts.test_run_recovery_drill` passed 2 tests.
- Real drill: `py scripts\run_recovery_drill.py run <REC-012> <disposable-output>` passed in 195.7 seconds.

The drill re-ran the REC-012 verifier after importing into the disposable copy and compared the authority's package manifest, SQLite database, and checksum-manifest hashes before and after. The authority did not change.
