import json
import os
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "setup"))

import create_launchd
import components
import doctor
import init
import install_quickcapture
import state
import uninstall


class InitHelpersTest(unittest.TestCase):
    def test_init_requires_vault_flag(self):
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "setup" / "init.py"), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--vault", result.stdout)
        self.assertNotIn("--non-interactive", result.stdout)

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
            template = Path(tmp) / "template"
            dest = Path(tmp) / "dest"
            (template / "00 - Inbox").mkdir(parents=True)
            (template / "00 - Inbox" / "Day 1 - Brain Dump.md").write_text("onboarding", encoding="utf-8")
            (template / "00 - Inbox" / "real-capture.md").write_text("keep", encoding="utf-8")
            (template / "keep.md").write_text("template", encoding="utf-8")
            init.copy_template(template, dest)
            self.assertFalse((dest / "00 - Inbox" / "Day 1 - Brain Dump.md").exists())
            self.assertTrue((dest / "00 - Inbox" / "real-capture.md").exists())
            self.assertTrue((dest / "keep.md").exists())

    def test_copy_template_preserves_existing_user_files_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "template"
            dest = root / "vault"
            (template / "00 - Inbox").mkdir(parents=True)
            (template / "00 - Inbox" / "README.md").write_text("template", encoding="utf-8")
            (template / "00 - Inbox" / ".gitkeep").write_text("", encoding="utf-8")
            (template / "AGENTS.md").write_text("template agent", encoding="utf-8")
            (dest / "00 - Inbox").mkdir(parents=True)
            (dest / "00 - Inbox" / "README.md").write_text("user", encoding="utf-8")

            init.copy_template(template, dest)

            self.assertEqual((dest / "00 - Inbox" / "README.md").read_text(encoding="utf-8"), "user")
            self.assertFalse((dest / "00 - Inbox" / ".gitkeep").exists())
            self.assertFalse((dest / "AGENTS.md").exists())

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

    def test_setup_report_lists_automation_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            state.update_setup_state(
                vault,
                capabilities={"launchd": "ok", "agent_cron": "ok", "git_snapshots": "ok"},
            )

            report = init.write_setup_report(vault)
            content = report.read_text(encoding="utf-8")

            self.assertIn("launchd", content)
            self.assertIn("agent_cron", content)
            self.assertIn("com.llm-gtd.export-dashboard", content)
            self.assertIn("com.llm-gtd.git-snapshot", content)
            self.assertIn("agent-cron-guide", content)

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

    def test_doctor_warns_when_knowledge_contract_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            (vault / "AGENTS.md").write_text("Old instructions mention knowledge/gtd only.", encoding="utf-8")

            issues = doctor.check_knowledge_contract(vault)
            messages = [msg for _, msg in issues]

            self.assertTrue(any("knowledge/evidence contract" in msg for msg in messages))
            self.assertTrue(any("knowledge-link.txt" in msg for msg in messages))

    def test_doctor_warns_when_knowledge_link_is_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            (vault / "AGENTS.md").write_text(
                "Knowledge & Evidence Contract\n"
                "Methodology is model-assisted\n"
                "Classify the query before answering\n"
                "Answer compounding\n"
                "knowledge/gtd",
                encoding="utf-8",
            )
            (vault / ".llm-gtd").mkdir()
            (vault / ".llm-gtd" / "knowledge-link.txt").write_text("path: /definitely/missing/gtd\n", encoding="utf-8")

            issues = doctor.check_knowledge_contract(vault)

            self.assertTrue(any("does not point to a directory" in msg for _, msg in issues))


class UninstallTest(unittest.TestCase):
    def test_uninstall_preserves_user_asset_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            for dirname in uninstall.USER_ASSET_DIRS:
                folder = vault / dirname
                folder.mkdir(parents=True)
                (folder / "note.md").write_text("user data", encoding="utf-8")

            rc = uninstall.uninstall(str(vault))

            self.assertEqual(rc, 0)
            for dirname in uninstall.USER_ASSET_DIRS:
                self.assertTrue((vault / dirname).is_dir())
                self.assertEqual((vault / dirname / "note.md").read_text(encoding="utf-8"), "user data")

    def test_uninstall_marks_runtime_cleanup_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            for dirname in uninstall.USER_ASSET_DIRS:
                (vault / dirname).mkdir(parents=True)

            rc = uninstall.uninstall(str(vault))
            loaded = state.load_setup_state(vault)

            self.assertEqual(rc, 0)
            self.assertEqual(loaded["capabilities"]["agent_cron"], "runtime_cleanup_pending")
            self.assertEqual(loaded["capabilities"]["im_docs"], "runtime_cleanup_pending")


class AgentCronTest(unittest.TestCase):
    def test_runtime_prompt_contains_vault_path(self):
        import agent_cron
        prompt = agent_cron.build_runtime_prompt("/tmp/GTD", "morning / 早", "morning brief")
        self.assertIn("/tmp/GTD", prompt)
        self.assertIn("morning brief", prompt)

    def test_default_jobs_count(self):
        import agent_cron
        jobs = agent_cron.default_jobs("/tmp/GTD")
        self.assertEqual(len(jobs), 3)
        self.assertEqual(jobs[0].key, "morning")


class VersionTest(unittest.TestCase):
    def test_compare_versions(self):
        import version
        self.assertEqual(version.compare_versions("2.3.3", "2.4.0"), -1)
        self.assertEqual(version.compare_versions("2.4.0", "2.4.0"), 0)
        self.assertEqual(version.compare_versions("2.5.0", "2.4.0"), 1)

    def test_read_repo_version(self):
        import version
        expected = (REPO_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version.read_repo_version(), expected)

    def test_check_for_updates_offline(self):
        import version
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            (vault / ".llm-gtd").mkdir()
            (vault / ".llm-gtd" / "version").write_text("2.3.0\n", encoding="utf-8")
            status = version.check_for_updates(
                local_repo_version="2.4.0",
                vault_version="2.3.0",
                fetch_remote=False,
            )
            self.assertTrue(status["update_available"])
            self.assertTrue(status["vault_behind_repo"])


class SkillContractTest(unittest.TestCase):
    def test_skill_documents_semantic_injection_ambiguity(self):
        text = (REPO_ROOT / "skills" / "llm-gtd" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Semantic-injection only", text)
        self.assertIn("GTD Inbox", text)
        self.assertIn("memory/wiki", text)

    def test_skill_documents_render_and_im_surface_duties(self):
        text = (REPO_ROOT / "skills" / "llm-gtd" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Render And IM Surface Duties", text)
        self.assertIn("External Surfaces", text)
        self.assertIn("Scheduling doc / online docs", text)
        self.assertIn("runtime_cleanup_pending", text)

    def test_skill_setup_requires_preference_questionnaire(self):
        text = (REPO_ROOT / "skills" / "llm-gtd" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("全部默认", text)
        self.assertIn("Round 1", text)
        self.assertIn("--install-quickcapture", text)
        self.assertNotIn("| 14 | Install QuickCapture", text)

    def test_skill_setup_includes_full_playbook(self):
        text = (REPO_ROOT / "skills" / "llm-gtd" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Step 0", text)
        self.assertIn("create_launchd.py", text)
        self.assertIn("--verify", text)
        self.assertIn("Obsidian", text)
        self.assertIn("Final summary", text)
        self.assertIn("Setup pitfalls", text)
        self.assertIn("skip-automation", text)

    def test_skill_documents_onboard_cold_start_menu(self):
        text = (REPO_ROOT / "skills" / "llm-gtd" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("七天 GTD 冷启动", text)
        self.assertIn("直接告诉我", text)
        self.assertIn("链接或文件", text)
        self.assertIn("粘贴清单", text)
        self.assertIn("import_onboarding.py", text)
        self.assertIn("--no-open", text)

    def test_maintenance_map_routes_host_and_render_views(self):
        text = (REPO_ROOT / "docs" / "maintenance-map.md").read_text(encoding="utf-8")

        self.assertIn("Operational / install view", text)
        self.assertIn("Experience / render view", text)
        self.assertIn("Semantic-injection only", text)
        self.assertIn("Scheduling doc", text)

    def test_architecture_documents_online_doc_lifecycle(self):
        text = (REPO_ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

        self.assertIn("External surfaces", text)
        self.assertIn("Online document responsibility", text)
        self.assertIn("runtime_cleanup_pending", text)

    def test_rendered_agents_contains_knowledge_evidence_contract(self):
        template = (REPO_ROOT / "vault-template" / "AGENTS.md").read_text(encoding="utf-8")
        rendered = init.render_conditionals(
            template,
            {"okr": False, "doc_sync": False, "side_project": False, "knowledge_base": True},
        )
        rendered = init.render_im_conditionals(rendered, "none")
        rendered = init.render_placeholders(
            rendered,
            {
                "repo.path": str(REPO_ROOT),
                "vault.path": "/tmp/GTD",
                "user.name": "User",
                "user.role": "Knowledge Worker",
                "user.im_channel": "IM",
                "user.im_assistant": "assistant",
                "user.timezone": "Asia/Shanghai",
                "user.performance_cycle": "current cycle",
                "user.side_project_name": "Side Project",
                "config.rendered_at": "2026-06-14",
                "config.okr_file": "05 - Reference/OKR.md",
                "config.collaborators_file": "05 - Reference/collaborators.md",
                "config.morning_time": "10:30",
                "config.evening_time": "22:30",
                "config.weekly_time": "Sun 21:00",
                "doc.scheduling_id": "<paste-your-doc-id>",
                "doc.daily_id": "<paste-your-doc-id>",
                "dashboard_url": "file:///tmp/GTD/Dashboard.html",
                "doc_scheduling_url": "#",
                "doc_daily_url": "#",
            },
        )

        self.assertIn("Knowledge & Evidence Contract", rendered)
        self.assertIn("Methodology is model-assisted", rendered)
        self.assertIn("Classify the query before answering", rendered)
        self.assertIn("Answer compounding", rendered)


class UpgradeTest(unittest.TestCase):
    def test_component_hash_is_stable(self):
        manifest = {item["id"]: item for item in components.load_manifest(REPO_ROOT)}
        first = components.component_hash(manifest["dashboard"], REPO_ROOT)
        second = components.component_hash(manifest["dashboard"], REPO_ROOT)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_gtd_knowledge_base_component_hash_is_stable(self):
        manifest = {item["id"]: item for item in components.load_manifest(REPO_ROOT)}
        first = components.component_hash(manifest["gtd_knowledge_base"], REPO_ROOT)
        second = components.component_hash(manifest["gtd_knowledge_base"], REPO_ROOT)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_check_json_identifies_changed_component(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            manifest = {item["id"]: item for item in components.load_manifest(REPO_ROOT)}
            dashboard = manifest["dashboard"]
            components.mark_component_applied(vault, dashboard, "old-hash")

            payload = upgrade.status_payload(
                vault,
                REPO_ROOT,
                fetch_remote=False,
                selected_ids={"dashboard"},
            )
            rows = {row["id"]: row for row in payload["components"]}

            self.assertTrue(rows["dashboard"]["changed"])
            self.assertEqual(rows["dashboard"]["action"], "update_dashboard_runtime")

    def test_doc_sync_protocol_requires_runtime_review(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            manifest = {item["id"]: item for item in components.load_manifest(REPO_ROOT)}
            protocol = manifest["doc_sync_protocol"]
            components.mark_component_applied(vault, protocol, "old-hash")

            payload = upgrade.status_payload(
                vault,
                REPO_ROOT,
                fetch_remote=False,
                selected_ids={"doc_sync_protocol"},
            )

            self.assertTrue(payload["components"][0]["changed"])
            self.assertEqual(payload["components"][0]["action"], "update_doc_sync_protocol")
            self.assertIn(
                {"component": "doc_sync_protocol", "action": "review_online_doc_sync_rules"},
                payload["runtime_actions_required"],
            )

    def test_build_init_command_uses_preferences(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            state.update_setup_state(
                vault,
                preferences={
                    "agent_platform": "hermes",
                    "im_platform": "telegram",
                    "morning_time": "09:00",
                    "evening_time": "21:00",
                    "features": {"okr": False, "doc_sync": False},
                },
            )
            cmd = upgrade.build_init_command(vault, REPO_ROOT)
            joined = " ".join(cmd)
            self.assertIn("--agent-platform hermes", joined)
            self.assertIn("--im-platform telegram", joined)
            self.assertIn("--disable-okr", joined)
            self.assertIn("--disable-doc-sync", joined)

    def test_apply_dashboard_app_does_not_rerender_agents(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            agents = vault / "AGENTS.md"
            agents.write_text("keep me", encoding="utf-8")

            original = upgrade.APPLIERS["dashboard_app"]
            try:
                upgrade.APPLIERS["dashboard_app"] = lambda vault, repo_root: {"app": "mocked"}
                rc = upgrade.apply_upgrade(
                    vault,
                    REPO_ROOT,
                    pull_repo=False,
                    selected_ids={"dashboard_app"},
                    force=True,
                )
            finally:
                upgrade.APPLIERS["dashboard_app"] = original

            self.assertEqual(rc, 0)
            self.assertEqual(agents.read_text(encoding="utf-8"), "keep me")

    def test_apply_gtd_knowledge_base_only_refreshes_link(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            agents = vault / "AGENTS.md"
            agents.write_text("keep me", encoding="utf-8")

            rc = upgrade.apply_upgrade(
                vault,
                REPO_ROOT,
                pull_repo=False,
                selected_ids={"gtd_knowledge_base"},
                force=True,
            )
            link = vault / ".llm-gtd" / "knowledge-link.txt"
            component_state = components.load_component_state(vault)

            self.assertEqual(rc, 0)
            self.assertEqual(agents.read_text(encoding="utf-8"), "keep me")
            self.assertIn("path:", link.read_text(encoding="utf-8"))
            self.assertIn("gtd_knowledge_base", component_state["components"])

    def test_agent_instructions_apply_creates_backup(self):
        import upgrade
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            (vault / "AGENTS.md").write_text("old agents", encoding="utf-8")
            (vault / "CLAUDE.md").write_text("old claude", encoding="utf-8")
            state.update_setup_state(
                vault,
                preferences={"features": {"doc_sync": False}, "im_platform": "none"},
            )

            rc = upgrade.apply_upgrade(
                vault,
                REPO_ROOT,
                pull_repo=False,
                selected_ids={"agent_instructions"},
                force=True,
            )
            backups = list((vault / ".llm-gtd" / "backups").glob("*AGENTS.md"))

            self.assertEqual(rc, 0)
            self.assertTrue(backups)
            self.assertIn("Canonical GTD instructions", (vault / "AGENTS.md").read_text(encoding="utf-8"))


class QueryAuditTest(unittest.TestCase):
    def test_query_audit_appends_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "GTD"
            vault.mkdir()
            (vault / "AGENTS.md").write_text("agent", encoding="utf-8")
            env = {**os.environ, "GTD_VAULT": str(vault)}
            script = REPO_ROOT / "vault-template" / "Scripts" / "query_audit.py"

            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--type",
                    "status",
                    "--mode",
                    "vault-evidence",
                    "--evidence",
                    "02 - Next Actions/foo.md",
                    "--missing",
                    "owner unknown",
                ],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            audit_file = vault / ".llm-gtd" / "logs" / "query-audit.jsonl"
            entry = json.loads(audit_file.read_text(encoding="utf-8").splitlines()[0])

            self.assertEqual(result.returncode, 0)
            self.assertEqual(entry["query_type"], "status")
            self.assertEqual(entry["answer_mode"], "vault-evidence")
            self.assertEqual(entry["evidence_paths"], ["02 - Next Actions/foo.md"])
            self.assertEqual(entry["missing_facts"], ["owner unknown"])


class LaunchdVerifyTest(unittest.TestCase):
    def test_verify_loaded_returns_mapping(self):
        ok, loaded = create_launchd.verify_loaded()
        self.assertIn("com.llm-gtd.export-dashboard", loaded)
        self.assertIn("com.llm-gtd.git-snapshot", loaded)
        self.assertIsInstance(ok, bool)


if __name__ == "__main__":
    unittest.main()
