"""Verify local initialization keeps harness data separate from the application."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("init_env", HARNESS / "scripts/init_env.py")
init_env = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(init_env)


class EnvironmentTests(unittest.TestCase):
    def prepare(self, root):
        harness = root / ".autopoiesis"
        harness.mkdir()
        (harness / ".env.example").write_bytes((HARNESS / ".env.example").read_bytes())
        return harness

    def test_initialization_contains_generated_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = self.prepare(root)
            self.assertTrue(init_env.initialize(harness))
            self.assertEqual(list(root.iterdir()), [harness])
            for name in ("state", "state/skills", "tmp", "cache"):
                self.assertTrue((harness / name).is_dir())
            values = dict(
                line.split("=", 1)
                for line in (harness / ".env").read_text().splitlines()
                if line and not line.startswith("#")
            )
            for name in ("LOCAL_BACKEND_API_KEY", "OH_SECRET_KEY"):
                self.assertEqual(len(values[name]), 64)
                int(values[name], 16)
            self.assertNotEqual(values["LOCAL_BACKEND_API_KEY"], values["OH_SECRET_KEY"])

    def test_existing_configuration_and_state_survive_initialization(self):
        with tempfile.TemporaryDirectory() as directory:
            harness = self.prepare(Path(directory))
            original = b"OH_SECRET_KEY=existing-key\nGH_TOKEN=existing-token\n"
            (harness / ".env").write_bytes(original)
            (harness / "state").mkdir()
            state = harness / "state/session.json"
            state.write_text("existing session")
            skills = harness / "state/skills"
            skills.mkdir()
            user_skill = skills / "user-guidance.md"
            user_skill.write_text("Keep user guidance")
            self.assertFalse(init_env.initialize(harness))
            self.assertEqual((harness / ".env").read_bytes(), original)
            self.assertEqual(state.read_text(), "existing session")
            self.assertEqual(user_skill.read_text(), "Keep user guidance")
            self.assertTrue((harness / "tmp").is_dir())
            self.assertTrue((harness / "cache").is_dir())

    def test_script_uses_its_location_instead_of_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = self.prepare(root)
            scripts = harness / "scripts"
            scripts.mkdir()
            script = scripts / "init_env.py"
            script.write_bytes((HARNESS / "scripts/init_env.py").read_bytes())
            result = subprocess.run(
                [sys.executable, str(script)], cwd=root, capture_output=True, text=True, timeout=10
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((harness / ".env").is_file())
            self.assertFalse((root / ".env").exists())
            self.assertNotIn("LOCAL_BACKEND_API_KEY=", result.stdout)
            self.assertNotIn("OH_SECRET_KEY=", result.stdout)


if __name__ == "__main__":
    unittest.main()
