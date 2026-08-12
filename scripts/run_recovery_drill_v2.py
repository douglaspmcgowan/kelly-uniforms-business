#!/usr/bin/env python3
"""Generation-aware successor for the representative recovery drill."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath, PureWindowsPath

import run_recovery_drill as v1


def authority_verifier(root: Path):
    root = Path(root).resolve()
    manifest = json.loads((root / "package-manifest.json").read_text(encoding="utf-8"))
    relative_value = manifest.get("commerce_import", {}).get("tool")
    if not isinstance(relative_value, str) or not relative_value:
        raise ValueError("authority manifest does not declare a package verifier")
    relative = PurePosixPath(relative_value)
    if (
        relative.is_absolute()
        or PureWindowsPath(relative_value).is_absolute()
        or ".." in relative.parts
        or len(relative.parts) != 2
        or relative.parts[0] != "tools"
        or not relative.name.startswith("package_")
        or not relative.name.endswith("_generation.py")
    ):
        raise ValueError("authority package verifier path is not an allowed portable tool path")
    module_path = root / Path(*relative.parts)
    if not module_path.is_file():
        raise ValueError(f"authority package verifier is missing: {relative_value}")
    spec = importlib.util.spec_from_file_location(
        f"_mt_uniforms_authority_verifier_{uuid.uuid4().hex}", module_path
    )
    if spec is None or spec.loader is None:
        raise ValueError("authority package verifier could not be loaded")
    module = importlib.util.module_from_spec(spec)
    tool_directory = str(module_path.parent)
    sys.path.insert(0, tool_directory)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path and sys.path[0] == tool_directory:
            sys.path.pop(0)
    if not callable(getattr(module, "verify_generation", None)):
        raise ValueError("authority package verifier has no verify_generation function")
    return module


def run_drill(authority: Path, destination: Path, schema: Path | None = None) -> dict:
    authority = Path(authority).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError(f"drill destination already exists: {destination}")
    if not authority.is_dir():
        raise ValueError(f"authority package does not exist: {authority}")
    if authority == destination or authority in destination.parents or destination in authority.parents:
        raise ValueError("authority and drill destination must be distinct and non-nested")
    schema = (
        Path(schema).resolve()
        if schema
        else Path(__file__).parents[1] / "schemas" / "commerce-import-bundle-v1.schema.json"
    )
    verifier = authority_verifier(authority)
    verifier.verify_generation(authority, require_empty=True)
    authority_before = v1._authority_hashes(authority)
    temporary = destination.with_name(f".{destination.name}.building-{uuid.uuid4().hex}")
    fixture = destination.with_name(f".{destination.name}.fixture-{uuid.uuid4().hex}")
    try:
        shutil.copytree(authority, temporary)
        marker = {
            "classification": "synthetic-drill-never-client-data",
            "authority": authority.name,
            "run_id": v1.RUN_ID,
            "promotable": False,
            "drill_version": "v2-generation-aware",
        }
        (temporary / "DRILL-ONLY.json").write_text(
            json.dumps(marker, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        manifest = v1.build_fixture_bundle(fixture)
        import_report = v1.package_import_ready_generation.stage_and_import_bundle(
            temporary, manifest, schema
        )
        package_report = v1.recovery_package.verify_package(temporary)
        reconstruction = v1.verify_reconstruction(
            temporary / v1.recovery_package.DATABASE_FILE
        )
        verifier.verify_generation(authority, require_empty=True)
        authority_after = v1._authority_hashes(authority)
        if authority_before != authority_after:
            raise ValueError("authority package changed during the recovery drill")
        temporary.rename(destination)
        return {
            "valid": True,
            "drill_version": "v2-generation-aware",
            "classification": "synthetic-drill-never-client-data",
            "authority_generation": getattr(verifier, "GENERATION", "unknown"),
            "authority_unchanged": True,
            "destination": str(destination),
            "import": import_report,
            "package": package_report,
            "reconstruction": reconstruction,
        }
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(fixture, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-fixture")
    build.add_argument("destination", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("database", type=Path)
    run = sub.add_parser("run")
    run.add_argument("authority", type=Path)
    run.add_argument("destination", type=Path)
    run.add_argument("--schema", type=Path)
    args = parser.parse_args()
    if args.command == "build-fixture":
        report = {"manifest": str(v1.build_fixture_bundle(args.destination))}
    elif args.command == "verify":
        report = v1.verify_reconstruction(args.database)
    else:
        report = run_drill(args.authority, args.destination, args.schema)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
