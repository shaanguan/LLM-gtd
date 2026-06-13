import plistlib
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "setup"))

import create_launchd
import doctor
import init
import install_quickcapture
import state


class InitHelpersTest(unittest.TestCase):
    def test_validate_hhmm_accepts_24_hour_time(self):
        self.assertEqual(init.validate_hhmm("09:30", "morning time"), "09:30")
        self.assertEqual(init.validate_hhmm("23:59", "evening time"), "23:59")

    def test_validate_hhmm_rejects_invalid_time(self):
        with self.assertRaises(ValueError):
            init.validate_hhmm("9:30", "morning time")
        with self.assertRaises(ValueError):
            init.validate_hhmm("24:00", "morning time")

    def test_copy_template_preserves_existing_user_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template"
            dest = root / "vault"
            (template / "00 - Inbox").mkdir(parents=True)
            (template / "00 - Inbox" / "README.md").write_text("template", encoding="utf-8")
            (template / "00 - Inbox" / ".gitkeep").write_text("", encoding="utf-8")
            (template / "CLAUDE.md").write_text("template agent", encoding="utf-8")
            (dest / "00 - Inbox").mkdir(parents=True)
            (dest / "00 - Inbox" / "README.md").write_text("user", encoding="utf-8")

            init.copy_template(template, dest)

            self.assertEqual((dest / "00 - Inbox" / "README.md").read_text(encoding="utf-8"), "user")
            self.assertFalse((dest / "00 - Inbox" / ".gitkeep").exists())
            self.assertFalse((dest / "CLAUDE.md").exists())

    def test_render_conditionals_supports_negated_features(self):
        text = """<!-- IF !feature.okr -->
No OKR
<!-- ELSE -->
OKR
<!-- ENDIF -->
"""

        self.assertEqual(init.render_conditionals(text, {"okr": False}), "No OKR\n")
        self.assertEqual(init.render_conditionals(text, {"okr": True}), "OKR\n")


class LaunchdTest(unittest.TestCase):
    def test_build_plists_are_valid_xml_and_escape_paths(self):
        vault = "/tmp/GTD & Stuff"
        plists = dict(create_launchd.build_plists(vault, "/usr/bin/python3"))

        export_data = plistlib.loads(plists["com.llm-gtd.export-dashboard"].encode("utf-8"))
        snapshot_data = plistlib.loads(plists["com.llm-gtd.git-snapshot"].encode("utf-8"))

        self.assertEqual(export_data["EnvironmentVariables"]["GTD_VAULT"], vault)
        self.assertEqual(snapshot_data["WorkingDirectory"], vault)

    def test_git_snapshot_command_commits_only_when_needed(self):
        command = create_launchd.build_git_snapshot_command("/tmp/GTD & Stuff")

        self.assertIn("cd '/tmp/GTD & Stuff' || exit 1", command)
        self.assertIn("if ! git diff --cached --quiet; then", command)
        self.assertIn('echo "No changes to snapshot"', command)


class QuickCaptureTest(unittest.TestCase):
    def test_launchagent_template_renders_environment(self):
        template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.gtd.quickcapture</string>
  <key>ProgramArguments</key><array><string>__QUICKCAPTURE_BIN__</string></array>
  <key>EnvironmentVariables</key>
  <dict><key>GTD_INBOX_DIR</key><string>__INBOX_DIR__</string></dict>
</dict>
</plist>
"""

        rendered = install_quickcapture.render_launchagent_plist(
            template,
            Path("/tmp/GTD & Stuff/Scripts/QuickCapture.bin"),
            Path("/tmp/GTD & Stuff/00 - Inbox"),
        )
        data = plistlib.loads(rendered.encode("utf-8"))

        self.assertEqual(data["ProgramArguments"], ["/tmp/GTD & Stuff/Scripts/QuickCapture.bin"])
        self.assertEqual(data["EnvironmentVariables"]["GTD_INBOX_DIR"], "/tmp/GTD & Stuff/00 - Inbox")


class StateAndDoctorTest(unittest.TestCase):
    def test_setup_state_tracks_next_pending_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()

            data = state.update_setup_state(
                vault,
                steps={"detect_repo": "ok", "ask_preferences": "ok"},
                capabilities={"vault": "ok"},
            )

            self.assertEqual(data["next_step"], "init_vault")
            loaded = state.load_setup_state(vault)
            self.assertEqual(loaded["capabilities"]["vault"], "ok")

    def test_doctor_capabilities_detect_core_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            for dirname in doctor.REQUIRED_DIRS:
                (vault / dirname).mkdir(parents=True, exist_ok=True)
            for filename in doctor.REQUIRED_FILES:
                (vault / filename).write_text("", encoding="utf-8")

            capabilities = doctor.build_capabilities(vault)

            self.assertEqual(capabilities["vault"], "ok")
            self.assertEqual(capabilities["dashboard"], "ok")


if __name__ == "__main__":
    unittest.main()
