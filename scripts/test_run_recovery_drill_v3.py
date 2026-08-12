import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
MODULE_PATH = SCRIPT_DIR / "run_recovery_drill_v3.py"


def load_drill():
    if not MODULE_PATH.is_file():
        raise AssertionError("run_recovery_drill_v3.py is missing")
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("run_recovery_drill_v3", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CacheFreeRecoveryDrillTests(unittest.TestCase):
    def test_manifest_verifier_load_writes_no_bytecode(self):
        """Fails if verifier loading mutates the authority with unchecksummed Python cache files."""
        drill = load_drill()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "tools"
            tools.mkdir()
            (tools / "verifier_helper.py").write_text("VALUE = 'REC-015'\n", encoding="utf-8")
            (tools / "package_clean_recovery_generation.py").write_text(
                "import verifier_helper\n"
                "GENERATION = verifier_helper.VALUE\n"
                "def verify_generation(root, require_empty=False):\n"
                "    return {'valid': True}\n",
                encoding="utf-8",
            )
            (root / "package-manifest.json").write_text(
                json.dumps(
                    {
                        "commerce_import": {
                            "tool": "tools/package_clean_recovery_generation.py"
                        }
                    }
                ),
                encoding="utf-8",
            )

            verifier = drill.authority_verifier(root)
            drill.assert_no_cache_artifacts(root)

        self.assertEqual(verifier.GENERATION, "REC-015")

    def test_cache_guard_rejects_existing_pyc(self):
        """Fails if a recovery authority can contain excluded, unchecksummed bytecode."""
        drill = load_drill()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cache = root / "tools" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "unsafe.pyc").write_bytes(b"bytecode")

            with self.assertRaisesRegex(ValueError, "Python cache artifacts"):
                drill.assert_no_cache_artifacts(root)


if __name__ == "__main__":
    unittest.main()
