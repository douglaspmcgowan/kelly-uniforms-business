# Source-ready recovery package contract v1

REC-010 is the self-contained acquisition and import authority for the current recovery effort. It inherits every verified REC-009 artifact and adds the OpenCart native-export capture path beside the Ecwid API capture path.

## Package-local commands

```powershell
py tools\package_source_ready_generation.py verify <recovery-root>
py tools\capture_ecwid_api.py <store-id> <capture-destination>
py tools\capture_opencart_native_export.py <source-export> <capture-destination>
py tools\package_source_ready_generation.py stage-import <recovery-root> <export-manifest>
```

The Ecwid command accepts its secret only from `ECWID_SECRET_TOKEN`. The OpenCart command accepts already-exported files and reads no credential value. Both acquisition outputs are restricted and must remain outside Git.

## Fresh-generation invariants

- Parent is a verified, empty REC-009 generation.
- Creation builds in a temporary sibling directory and promotes atomically.
- The complete REC-009 checksum/provenance/media/database authority is retained.
- OpenCart and Ecwid capture tools and runbooks, importer v2, schemas, and contracts are package-local and registered in `source_manifest` with portable hashes and byte counts.
- Fresh private commerce/import tables and import-backed `source_manifest` rows are empty.
- Package-only verification requires no repository files.

## Acquisition status

`opencart-and-ecwid-tools-packaged-awaiting-authenticated-exports` means the acquisition paths exist and have been tested; it does not mean private exports have been captured. Once source access is available, preserve the raw evidence first, normalize into the commerce bundle second, and create another immutable recovery generation for the imported records.
