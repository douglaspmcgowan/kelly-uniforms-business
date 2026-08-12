# OpenCart native-export capture runbook

Use this runbook after hosting or database access is available. The capture preserves authoritative source bytes before any restoration, inspection, or normalization.

## Required source layout

Prepare a new local directory outside Git:

```text
source-export/
  database.sql       required complete MySQL or MariaDB dump
  webroot/           required exact OpenCart document root
  storage/           optional external DIR_STORAGE tree
  config/            optional root and admin config copies
```

The database dump should preserve schema, data, character sets/collations, auto-increment state, triggers, views, routines, events, and table engines. Record the dump method and whether non-transactional tables were locked; OpenCart installations can contain MyISAM tables, so `--single-transaction` alone may not produce a coherent backup.

The webroot should include images, both OpenCart config files, `.htaccess`, PHP settings, Composer metadata, extension installers, OCMOD output, and Journal theme files. External storage should include downloads, uploads, logs, and generated modifications. Include a separate Journal Import/Export artifact when the admin provides one.

## Capture command

```powershell
py scripts\capture_opencart_native_export.py `
  C:\path\to\source-export `
  C:\Users\dougl\Data\Projects\kelly-uniforms-business\private\business-continuity\opencart-native-YYYYMMDD
```

The destination must not already exist. The tool copies through a temporary sibling directory and promotes the capture only after every source file is hashed and inventoried. It rejects symbolic links and Windows junctions/reparse points so the capture cannot silently escape the declared source tree.

## Output

- `raw/database.sql` and the exact `raw/webroot`, `raw/storage`, and `raw/config` trees
- `inventory/files.ndjson` with portable source/captured paths, SHA-256, byte count, completeness, and restricted sensitivity
- `capture-manifest.json` with root reconciliation, counts, aggregate bytes, inventory hash, and an explicit `sql_parsed: false` statement

The manifest and inventory contain no source-file contents. Treat the whole capture as restricted because SQL dumps and configuration files can contain customer data, password hashes, mail/payment credentials, API material, encryption keys, sessions, and private notes.

## Restore and normalization boundary

Do not regex-parse the SQL dump. Restore it into a disposable compatible MySQL/MariaDB instance, inspect `information_schema` to discover the installed OpenCart version, table prefix, stores, languages, currencies, extensions, and Journal/non-core tables, then emit the commerce import bundle. Use one new immutable recovery generation per capture. Never expose a restored admin/API surface until all credentials have been reset.

The current normalized schema intentionally does not claim complete coverage for translations, SEO, manufacturers, attributes/filters, product specials/discounts, tax/shipping/payment rules, order history, customer groups, extension/layout configuration, or Journal configuration. Preserve those sources exactly and report unsupported mappings rather than inventing normalized semantics.
