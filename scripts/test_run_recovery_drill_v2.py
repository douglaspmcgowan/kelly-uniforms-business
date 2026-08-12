import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
MODULE_PATH = SCRIPT_DIR / "run_recovery_drill_v2.py"


def load_drill():
    if not MODULE_PATH.is_file():
        raise AssertionError("run_recovery_drill_v2.py is missing")
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("run_recovery_drill_v2", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerationAwareRecoveryDrillTests(unittest.TestCase):
    def test_authority_verifier_follows_manifest_packaged_tool(self):
        """Fails if a successor package is sent to an older hard-coded verifier."""
        drill = load_drill()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "tools"
            tools.mkdir()
            (tools / "package_drill_ready_generation.py").write_text(
                "GENERATION = 'REC-013'\n"
                "def verify_generation(root, require_empty=False):\n"
                "    return {'valid': True}\n",
                encoding="utf-8",
            )
            (root / "package-manifest.json").write_text(
                json.dumps(
                    {
                        "generation": "REC-013",
                        "commerce_import": {
                            "tool": "tools/package_drill_ready_generation.py"
                        },
                    }
                ),
                encoding="utf-8",
            )
            verifier = drill.authority_verifier(root)

        self.assertEqual(verifier.GENERATION, "REC-013")
        self.assertTrue(callable(verifier.verify_generation))

    def test_authority_verifier_rejects_path_escape(self):
        """Fails if an authority manifest can load code outside its packaged tools directory."""
        drill = load_drill()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "package-manifest.json").write_text(
                json.dumps(
                    {
                        "commerce_import": {
                            "tool": "../outside/package_untrusted_generation.py"
                        }
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "allowed portable tool path"):
                drill.authority_verifier(root)


if __name__ == "__main__":
    unittest.main()
