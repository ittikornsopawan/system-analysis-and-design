from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agent_workspace.py"
PREFLIGHT = SCRIPT.parents[2] / "commit-and-pr" / "scripts" / "preflight.py"
SPEC = importlib.util.spec_from_file_location("agent_workspace", SCRIPT)
assert SPEC and SPEC.loader
agent_workspace = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_workspace)


REGISTRY = """\
version: 1
authorized_user: ittikorn
default_branch: main
workspace_root: .workspace
agents:
  - name: josh
    enabled: true
    role: .agents/agents/system-analyst.md
    title: SA Lead
    scope: repository-wide
    reports_to: ittikorn
    workspace_key: josh
    capabilities:
      - delegate-delivery
  - name: tommy
    enabled: true
    role: .agents/agents/system-analyst.md
    title: System Analyst
    scope: e-commerce
    reports_to: josh
    workspace_key: tommy
    capabilities: []
  - name: marry
    enabled: true
    role: .agents/agents/system-analyst.md
    title: System Analyst
    scope: e-commerce
    reports_to: josh
    workspace_key: marry
    capabilities: []
"""


def command(argv: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class RegistryTests(unittest.TestCase):
    def test_repository_registry_is_valid(self) -> None:
        repository_root = SCRIPT.parents[4]
        registry = agent_workspace.parse_registry(
            (repository_root / ".agents" / "team" / "agents.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(["josh", "tommy", "marry", "peter"], [item["name"] for item in registry["agents"]])
        peter = agent_workspace.agent_record(registry, "peter")
        self.assertEqual(".agents/agents/system-analyst.md", peter["role"])
        self.assertEqual("repository-wide", peter["scope"])
        self.assertEqual("josh", peter["reports_to"])
        self.assertEqual("peter", peter["workspace_key"])
        self.assertEqual([], peter["capabilities"])
        agent_workspace.validate_delivery(
            registry, assignee="peter", delivery="open-pr", authorized_by="ittikorn"
        )
        with self.assertRaisesRegex(agent_workspace.Blocked, "cannot delegate"):
            agent_workspace.validate_delivery(
                registry, assignee="tommy", delivery="open-pr", authorized_by="peter"
            )

    def test_registry_and_delegated_authority(self) -> None:
        registry = agent_workspace.parse_registry(REGISTRY)
        agent_workspace.validate_delivery(
            registry,
            assignee="tommy",
            delivery="open-pr",
            authorized_by="josh",
        )
        with self.assertRaisesRegex(agent_workspace.Blocked, "cannot delegate"):
            agent_workspace.validate_delivery(
                registry,
                assignee="tommy",
                delivery="open-pr",
                authorized_by="marry",
            )
        with self.assertRaisesRegex(agent_workspace.Blocked, "self-authorize"):
            agent_workspace.validate_delivery(
                registry,
                assignee="josh",
                delivery="open-pr",
                authorized_by="josh",
            )

    def test_duplicate_and_unsafe_names_are_rejected(self) -> None:
        duplicate = REGISTRY + """\
  - name: tommy
    enabled: true
    role: .agents/agents/system-analyst.md
    title: Duplicate
    scope: e-commerce
    reports_to: josh
    workspace_key: tommy
    capabilities: []
"""
        with self.assertRaisesRegex(agent_workspace.Blocked, "duplicate registry agent"):
            agent_workspace.parse_registry(duplicate)
        with self.assertRaisesRegex(agent_workspace.Blocked, "invalid agent name"):
            agent_workspace.agent_record(agent_workspace.parse_registry(REGISTRY), "../tommy")


class WorkspaceIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.origin = self.root / "origin.git"
        self.seed = self.root / "seed"
        self.host = self.root / "host"
        self.gitconfig = self.root / "gitconfig"
        self.remote_url = "https://github.com/example/system-analysis-and-design.git"
        self.env = os.environ.copy()
        self.env["GIT_CONFIG_GLOBAL"] = str(self.gitconfig)
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        self.fake_bin = self.root / "bin"
        self.fake_bin.mkdir()
        fake_gh = self.fake_bin / "gh"
        fake_gh.write_text(
            "#!/bin/sh\n"
            "if [ \"$2\" = \"list\" ]; then\n"
            "  printf '%s\\n' \"${FAKE_GH_LIST_JSON:-[]}\"\n"
            "else\n"
            "  printf '%s\\n' \"$FAKE_GH_JSON\"\n"
            "fi\n",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        self.env["PATH"] = f"{self.fake_bin}{os.pathsep}{self.env.get('PATH', '')}"
        self.env["FAKE_GH_LIST_JSON"] = "[]"

        self.git(self.root, "config", "--file", str(self.gitconfig), "user.name", "Workspace Test")
        self.git(
            self.root,
            "config",
            "--file",
            str(self.gitconfig),
            "user.email",
            "workspace-test@example.invalid",
        )
        self.git(
            self.root,
            "config",
            "--file",
            str(self.gitconfig),
            f"url.file://{self.origin}.insteadOf",
            self.remote_url,
        )

        self.git(self.root, "init", "--bare", str(self.origin))
        self.git(self.root, "init", "-b", "main", str(self.seed))
        (self.seed / ".agents" / "team").mkdir(parents=True)
        (self.seed / ".agents" / "agents").mkdir(parents=True)
        (self.seed / ".agents" / "skills" / "agent-workspace" / "scripts").mkdir(
            parents=True
        )
        (self.seed / ".agents" / "skills" / "commit-and-pr" / "scripts").mkdir(
            parents=True
        )
        (self.seed / ".agents" / "team" / "agents.yaml").write_text(REGISTRY, encoding="utf-8")
        (self.seed / ".agents" / "agents" / "system-analyst.md").write_text(
            "---\nname: System Analyst\ndescription: Test role.\n---\n",
            encoding="utf-8",
        )
        shutil.copy2(
            SCRIPT,
            self.seed
            / ".agents"
            / "skills"
            / "agent-workspace"
            / "scripts"
            / "agent_workspace.py",
        )
        shutil.copy2(
            PREFLIGHT,
            self.seed / ".agents" / "skills" / "commit-and-pr" / "scripts" / "preflight.py",
        )
        (self.seed / ".gitignore").write_text("/.workspace/\n", encoding="utf-8")
        (self.seed / "README.md").write_text("baseline\n", encoding="utf-8")
        self.git(self.seed, "add", ".gitignore", ".agents", "README.md")
        self.git(self.seed, "commit", "-m", "chore: seed test repository")
        self.git(self.seed, "remote", "add", "origin", self.remote_url)
        self.git(self.seed, "push", "-u", "origin", "main")
        self.git(self.origin, "symbolic-ref", "HEAD", "refs/heads/main")
        self.git(self.root, "clone", "--branch", "main", self.remote_url, str(self.host))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = command(["git", *args], cwd=cwd, env=self.env)
        if result.returncode != 0:
            self.fail(f"git {' '.join(args)} failed: {result.stderr or result.stdout}")
        return result

    def cli(
        self,
        *args: str,
        expected: int = 0,
        extra_env: dict[str, str] | None = None,
    ) -> dict[str, object]:
        env = self.env.copy()
        if extra_env:
            env.update(extra_env)
        result = command(
            [sys.executable, "-B", str(SCRIPT), *args, "--host", str(self.host)],
            cwd=self.host,
            env=env,
        )
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        stream = result.stdout if result.returncode == 0 else result.stderr
        return json.loads(stream)

    def create_tommy(self) -> Path:
        result = self.cli("create", "--agent", "tommy")
        self.assertEqual("created", result["status"])
        workspace = self.host / ".workspace" / "tommy"
        self.assertTrue((workspace / ".git").is_dir())
        self.assertEqual(
            self.remote_url,
            self.git(workspace, "config", "--get", "remote.origin.url").stdout.strip(),
        )
        return workspace

    def prepare_tommy(self) -> tuple[Path, dict[str, object]]:
        workspace = self.create_tommy()
        prepared = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "sample-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Create the sample documentation",
            "--scope",
            "e-commerce",
            "--baseline-command",
            "git status --porcelain",
        )
        self.assertEqual("prepared", prepared["status"])
        self.assertEqual("docs/tommy-sample-task", prepared["branch"])
        return workspace, prepared

    def test_create_prepare_lock_and_release(self) -> None:
        workspace, prepared = self.prepare_tommy()
        blocked = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "other-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Create another document",
            "--scope",
            "e-commerce",
            expected=2,
        )
        self.assertIn("locked", str(blocked["reason"]))
        released = self.cli(
            "release",
            "--agent",
            "tommy",
            "--token",
            str(prepared["lock_token"]),
        )
        self.assertEqual("released", released["status"])
        self.assertEqual(
            "docs/tommy-sample-task",
            self.git(workspace, "branch", "--show-current").stdout.strip(),
        )

    def test_untrusted_authority_and_dirty_workspace_block(self) -> None:
        local_registry = REGISTRY.rsplit("    capabilities: []", 1)[0] + """\
    capabilities:
      - delegate-delivery
"""
        (self.host / ".agents" / "team" / "agents.yaml").write_text(
            local_registry,
            encoding="utf-8",
        )
        workspace = self.create_tommy()
        unauthorized = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "unsafe-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "marry",
            "--task",
            "Attempt an unauthorized task",
            "--scope",
            "e-commerce",
            expected=2,
        )
        self.assertIn("cannot delegate", str(unauthorized["reason"]))
        (workspace / "untracked.txt").write_text("do not delete\n", encoding="utf-8")
        dirty = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "dirty-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Attempt a dirty task",
            "--scope",
            "e-commerce",
            expected=2,
        )
        self.assertIn("tracked or untracked changes", str(dirty["reason"]))
        self.assertTrue((workspace / "untracked.txt").exists())

    def test_symlinked_workspace_root_blocks_without_touching_target(self) -> None:
        escape = self.root / "escape"
        escape.mkdir()
        (self.host / ".workspace").symlink_to(escape, target_is_directory=True)
        blocked = self.cli("create", "--agent", "tommy", expected=2)
        self.assertIn("must not be a symlink", str(blocked["reason"]))
        self.assertEqual([], list(escape.iterdir()))

    def test_linked_worktree_cannot_impersonate_a_managed_clone(self) -> None:
        workspace = self.host / ".workspace" / "tommy"
        workspace.parent.mkdir()
        self.git(self.host, "worktree", "add", "-b", "docs/tommy-linked", str(workspace))
        blocked = self.cli("status", "--agent", "tommy", expected=2)
        self.assertIn("full clone", str(blocked["reason"]))

    def test_baseline_cannot_modify_the_branch_starting_point(self) -> None:
        workspace = self.create_tommy()
        blocked = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "generated-baseline",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Prove baseline contamination is blocked",
            "--scope",
            "e-commerce",
            "--baseline-command",
            "touch generated.txt",
            expected=2,
        )
        self.assertIn("tracked or untracked changes", str(blocked["reason"]))
        self.assertTrue((workspace / "generated.txt").exists())
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_existing_open_agent_pr_blocks_a_new_assignment(self) -> None:
        workspace = self.create_tommy()
        open_pr = json.dumps(
            [
                {
                    "state": "OPEN",
                    "baseRefName": "release/next",
                    "headRefName": "docs/tommy-previous-task",
                    "headRefOid": "a" * 40,
                    "url": "https://github.com/example/system-analysis-and-design/pull/8",
                    "number": 8,
                }
            ]
        )
        blocked = self.cli(
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "new-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Start a new task",
            "--scope",
            "e-commerce",
            expected=2,
            extra_env={"FAKE_GH_LIST_JSON": open_pr},
        )
        self.assertIn("already has an open pull request", str(blocked["reason"]))
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_commit_preflight_rejects_paths_outside_assignment_scope(self) -> None:
        workspace, prepared = self.prepare_tommy()
        (workspace / "outside.md").write_text("outside scope\n", encoding="utf-8")
        result = command(
            [
                sys.executable,
                "-B",
                ".agents/skills/commit-and-pr/scripts/preflight.py",
                "--base",
                "main",
            ],
            cwd=workspace,
            env=self.env,
        )
        self.assertEqual(1, result.returncode, msg=result.stdout + result.stderr)
        self.assertIn("changed paths exceed assignment scope", result.stdout)
        self.cli(
            "release",
            "--agent",
            "tommy",
            "--token",
            str(prepared["lock_token"]),
        )

    def test_clearing_agent_marker_cannot_bypass_managed_preflight(self) -> None:
        workspace, prepared = self.prepare_tommy()
        (workspace / "outside.md").write_text("outside scope\n", encoding="utf-8")
        self.git(workspace, "config", "--unset", "agent.name")
        result = command(
            [
                sys.executable,
                "-B",
                ".agents/skills/commit-and-pr/scripts/preflight.py",
                "--base",
                "main",
            ],
            cwd=workspace,
            env=self.env,
        )
        self.assertEqual(1, result.returncode, msg=result.stdout + result.stderr)
        self.assertIn("identity markers do not match", result.stdout)
        self.cli(
            "release",
            "--agent",
            "tommy",
            "--token",
            str(prepared["lock_token"]),
        )

    def test_park_uses_merged_pr_evidence_and_preserves_remote_branch(self) -> None:
        workspace, prepared = self.prepare_tommy()
        branch = str(prepared["branch"])
        (workspace / "e-commerce").mkdir()
        (workspace / "e-commerce" / "change.md").write_text(
            "task change\n",
            encoding="utf-8",
        )
        self.git(workspace, "add", "e-commerce/change.md")
        self.git(workspace, "commit", "-m", "docs: add task change")
        self.git(workspace, "push", "-u", "origin", branch)
        head = self.git(workspace, "rev-parse", "HEAD").stdout.strip()
        self.cli(
            "release",
            "--agent",
            "tommy",
            "--token",
            str(prepared["lock_token"]),
        )

        integrator = self.root / "integrator"
        self.git(self.root, "clone", "--branch", "main", self.remote_url, str(integrator))
        (integrator / "merged.md").write_text("squash result\n", encoding="utf-8")
        self.git(integrator, "add", "merged.md")
        self.git(integrator, "commit", "-m", "docs: simulate merged result")
        self.git(integrator, "push", "origin", "main")

        gh_payload = json.dumps(
            {
                "state": "MERGED",
                "mergedAt": "2026-11-06T12:00:00Z",
                "baseRefName": "main",
                "headRefName": branch,
                "headRefOid": head,
                "url": "https://github.com/example/system-analysis-and-design/pull/1",
                "number": 1,
            }
        )
        cross_repository = self.cli(
            "park",
            "--agent",
            "tommy",
            "--pr",
            "https://github.com/other/repository/pull/1",
            expected=2,
            extra_env={"FAKE_GH_JSON": gh_payload},
        )
        self.assertIn("does not belong", str(cross_repository["reason"]))
        self.assertEqual(branch, self.git(workspace, "branch", "--show-current").stdout.strip())
        parked = self.cli(
            "park",
            "--agent",
            "tommy",
            "--pr",
            "1",
            extra_env={
                "FAKE_GH_JSON": gh_payload,
            },
        )
        self.assertEqual("parked", parked["status"])
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())
        local_branch = command(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=workspace,
            env=self.env,
        )
        self.assertNotEqual(0, local_branch.returncode)
        remote_branch = self.git(workspace, "ls-remote", "--heads", "origin", branch)
        self.assertIn(branch, remote_branch.stdout)
        self.assertEqual(
            self.git(workspace, "rev-parse", "main").stdout.strip(),
            self.git(workspace, "rev-parse", "origin/main").stdout.strip(),
        )


if __name__ == "__main__":
    unittest.main()
