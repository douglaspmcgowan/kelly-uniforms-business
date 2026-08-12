# Commerce bundle importer v2

Date: 2026-08-10

## Result

Added a successor normalized-bundle importer that preserves the frozen REC-008 importer and closes two failures identified before building the OpenCart native-export adapter.

1. Category insertion is dependency-aware. A child whose normalized ID sorts before its parent now imports successfully because category rows are topologically ordered. Cyclic hierarchies fail closed.
2. Joined and derived rows can record every contributing source artifact, native record ID, and source locator. Each declared contributor receives its own `record_lineage` row and must reference an artifact in the validated bundle.

The importer retains v1 validation, allowlisted target tables/columns, source-manifest registration, transaction boundaries, idempotent identical runs, changed-manifest rejection, reconciliation, foreign-key verification, and failure-evidence retention.

## Verification

TDD red state: both tests failed because `import_commerce_bundle_v2.py` did not exist.

Green tests:

- a child category with lexical ID `a-child` imported only after its parent `z-parent`;
- one product/category membership produced two exact lineage rows from separate category and product snapshot artifacts;
- reconciliation counted the enclosing product source record once even though its joined target row referenced a category contributor.

Command: `py -m unittest scripts.test_import_commerce_bundle_v2`
Result: 2 tests passed.

## Remaining OpenCart boundary

A native OpenCart capture still requires a compatible disposable MariaDB/MySQL restore, schema/prefix/version/extension discovery, exact SQL/webroot/storage/config preservation, secret-scrubbed table snapshots, Journal inventory/export, media hashing, and unsupported-field reporting. No live database or hosting export is currently accessible.
