# OpenCart native-export capture adapter

Date: 2026-08-10

## Result

Added an atomic, value-safe source acquisition adapter for a complete OpenCart native export. It accepts a required SQL dump and webroot plus optional external storage and configuration trees, copies every source byte without parsing SQL, and writes portable SHA-256/byte inventories with restricted sensitivity.

The adapter rejects existing destinations, missing required roots, nested source/destination paths, symbolic links, and Windows directory junctions/reparse points. A failed capture removes its temporary build directory and leaves no completed-looking destination.

## Verification

- Initial TDD red: 4 tests failed because `capture_opencart_native_export.py` did not exist.
- First green: 4 tests passed with one ordinary-symlink fixture skipped because this Windows user lacks symlink creation privilege.
- Adversarial red: a Windows directory junction escaped the declared source tree and the new regression test failed because the adapter accepted it.
- Fix: the source validator now rejects both symbolic links and Windows junctions/reparse points.
- Final focused command: `py -m unittest scripts.test_capture_opencart_native_export`
- Final focused result: 5 tests passed, with the unavailable ordinary-symlink fixture skipped; the Windows junction regression executed and passed.

## Current boundary

No live OpenCart export was captured. The available admin browser session was signed out, and hosting/database access was not available through an approved process boundary. The adapter is ready for the native dump/webroot/storage/config evidence when that access is supplied.
