#!/usr/bin/env python3
"""Capture an OpenCart native export as immutable, restricted source evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath


FORMAT = "mt-uniforms-opencart-native-capture/v1"
REQUIRED_ROOTS = ("database.sql", "webroot")
OPTIONAL_ROOTS = ("storage", "config")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable(relative: Path) -> str:
    value = relative.as_posix()
    if relative.is_absolute() or PureWindowsPath(value).is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe source path: {value}")
    return value


def _validate_source(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise ValueError("source export directory does not exist")
    if destination.exists():
        raise ValueError("destination already exists; captures are immutable")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("source and destination must be distinct, non-nested paths")
    if not (source / "database.sql").is_file():
        raise ValueError("required database.sql file is missing")
    if not (source / "webroot").is_dir():
        raise ValueError("required webroot directory is missing")
    for path in source.rglob("*"):
        is_junction = getattr(path, "is_junction", lambda: False)()
        if path.is_symlink() or is_junction:
            raise ValueError(
                f"symbolic link or reparse point is not allowed: "
                f"{_portable(path.relative_to(source))}"
            )


def _source_files(source: Path) -> list[Path]:
    files = [source / "database.sql"]
    for root_name in (*REQUIRED_ROOTS[1:], *OPTIONAL_ROOTS):
        root = source / root_name
        if root.is_dir():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(files, key=lambda path: path.relative_to(source).as_posix())


def capture_export(
    source: Path,
    destination: Path,
    captured_at: str | None = None,
) -> dict:
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    _validate_source(source, destination)
    files = _source_files(source)
    now = captured_at or utc_now()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    try:
        inventory = []
        total_bytes = 0
        for source_file in files:
            source_relative = source_file.relative_to(source)
            source_path = _portable(source_relative)
            captured_relative = Path("raw") / source_relative
            target = temporary / captured_relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target)
            size = target.stat().st_size
            total_bytes += size
            inventory.append(
                {
                    "source_path": source_path,
                    "captured_path": captured_relative.as_posix(),
                    "sha256": sha256_file(target),
                    "bytes": size,
                    "sensitivity": "restricted",
                    "completeness": "complete-file",
                }
            )
        inventory_path = temporary / "inventory" / "files.ndjson"
        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory_path.write_text(
            "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in inventory),
            encoding="utf-8",
            newline="\n",
        )
        roots = {
            name: {
                "present": (source / name).exists(),
                "kind": "file" if name == "database.sql" else "directory",
                "required": name in REQUIRED_ROOTS,
                "file_count": sum(
                    1
                    for row in inventory
                    if row["source_path"] == name or row["source_path"].startswith(name + "/")
                ),
            }
            for name in (*REQUIRED_ROOTS, *OPTIONAL_ROOTS)
        }
        manifest = {
            "format": FORMAT,
            "captured_at": now,
            "status": "captured",
            "sensitivity": "restricted",
            "capture_method": "native-export-byte-copy",
            "sql_parsed": False,
            "required_roots": list(REQUIRED_ROOTS),
            "roots": roots,
            "source_files": len(inventory),
            "source_bytes": total_bytes,
            "inventory": {
                "path": "inventory/files.ndjson",
                "sha256": sha256_file(inventory_path),
                "bytes": inventory_path.stat().st_size,
            },
            "normalization_status": "not-normalized",
        }
        (temporary / "capture-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        temporary.rename(destination)
        return {
            "format": FORMAT,
            "status": "captured",
            "source_files": len(inventory),
            "source_bytes": total_bytes,
            "destination": str(destination),
        }
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(capture_export(args.source, args.destination), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
