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
        self.assertEqual(["josh", "tommy", "marry", "peter", "jinny"], [item["name"] for item in registry["agents"]])
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

    def test_jinny_diagram_role_and_authority(self) -> None:
        repository_root = SCRIPT.parents[4]
        registry = agent_workspace.parse_registry(
            (repository_root / ".agents" / "team" / "agents.yaml").read_text(
                encoding="utf-8"
            )
        )
        jinny = agent_workspace.agent_record(registry, "jinny")
        self.assertEqual(".agents/agents/diagram-designer.md", jinny["role"])
        self.assertTrue((repository_root / jinny["role"]).is_file())
        self.assertEqual("repository-wide", jinny["scope"])
        self.assertEqual("josh", jinny["reports_to"])
        self.assertEqual("jinny", jinny["workspace_key"])
        self.assertEqual([], jinny["capabilities"])
        agent_workspace.validate_delivery(
            registry, assignee="jinny", delivery="none", authorized_by="ittikorn"
        )
        with self.assertRaisesRegex(agent_workspace.Blocked, "cannot delegate"):
            agent_workspace.validate_delivery(
                registry, assignee="tommy", delivery="open-pr", authorized_by="jinny"
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

    def prepare_args(self, *scopes: str) -> list[str]:
        args = [
            "prepare",
            "--agent",
            "tommy",
            "--type",
            "docs",
            "--topic",
            "scope-task",
            "--delivery",
            "open-pr",
            "--authorized-by",
            "josh",
            "--task",
            "Check how several scopes are given",
        ]
        for scope in scopes:
            args += ["--scope", scope]
        return args

    def test_comma_in_a_scope_blocks_before_branch_and_metadata(self) -> None:
        workspace = self.create_tommy()
        state = self.host / ".workspace" / ".state"
        before = sorted(path.name for path in state.glob("*")) if state.exists() else []
        blocked = self.cli(*self.prepare_args("e-commerce/doc,e-commerce/db"), expected=2)
        self.assertIn("comma", str(blocked["reason"]))
        self.assertIn("repeat --scope once per path", str(blocked["reason"]))
        self.assertIn("--scope e-commerce/doc --scope", str(blocked["reason"]))
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())
        self.assertEqual("", self.git(workspace, "branch", "--list", "docs/tommy-scope-task").stdout.strip())
        after = sorted(path.name for path in state.glob("*")) if state.exists() else []
        self.assertEqual(before, after)
        self.assertFalse((state / "tommy.json").exists())
        # one of several values with a comma blocks as well
        mixed = self.cli(*self.prepare_args("e-commerce/doc", "e-commerce/db,tasks"), expected=2)
        self.assertIn("comma", str(mixed["reason"]))
        self.assertFalse((state / "tommy.json").exists())

    def test_separate_scope_flags_are_recorded_one_by_one(self) -> None:
        self.create_tommy()
        prepared = self.cli(*self.prepare_args("e-commerce/doc", "e-commerce/db"))
        self.assertEqual("prepared", prepared["status"])
        self.assertEqual(["e-commerce/doc", "e-commerce/db"], prepared["scope"])

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
        self.assertIn("open pull request whose assignment is not suspended", str(blocked["reason"]))
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


    # ---- suspend: a task whose pull request is open gives the workspace back, and the pull request comes back later ----
    PR_URL = "https://github.com/example/system-analysis-and-design/pull/{number}"

    def pr_item(self, branch: str, head: str, number: int = 5, state: str = "OPEN") -> dict[str, object]:
        return {
            "state": state,
            "mergedAt": None,
            "baseRefName": "main",
            "headRefName": branch,
            "headRefOid": head,
            "url": self.PR_URL.format(number=number),
            "number": number,
        }

    def prepare_tommy_task(self, topic: str, task: str, expected: int = 0, extra_env: dict[str, str] | None = None):
        return self.cli(
            "prepare", "--agent", "tommy", "--type", "docs", "--topic", topic, "--delivery", "open-pr",
            "--authorized-by", "josh", "--task", task, "--scope", "e-commerce", expected=expected, extra_env=extra_env,
        )

    def start_pushed_task(self, topic: str = "first-task", task: str = "First task") -> tuple[Path, dict[str, object], str, str]:
        workspace = self.create_tommy()
        prepared = self.prepare_tommy_task(topic, task)
        branch = str(prepared["branch"])
        (workspace / "e-commerce").mkdir(exist_ok=True)
        (workspace / "e-commerce" / f"{topic}.md").write_text("change\n", encoding="utf-8")
        self.git(workspace, "add", "e-commerce")
        self.git(workspace, "commit", "-m", f"docs: {topic}")
        self.git(workspace, "push", "-u", "origin", branch)
        return workspace, prepared, branch, self.git(workspace, "rev-parse", "HEAD").stdout.strip()

    def suspend(self, token: object, pr_list: list[dict[str, object]], expected: int = 0):
        return self.cli(
            "suspend", "--agent", "tommy", "--token", str(token), expected=expected,
            extra_env={"FAKE_GH_LIST_JSON": json.dumps(pr_list)},
        )

    def record_path(self, branch: str) -> Path:
        return self.host / ".workspace" / ".state" / "tommy-prs" / f"{branch.replace('/', '__')}.json"

    def assignment_file(self) -> Path:
        return self.host / ".workspace" / ".state" / "tommy.json"

    def test_suspend_returns_to_main_and_lets_the_next_task_start(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        suspended = self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        self.assertEqual("suspended", suspended["status"])
        record = json.loads(self.record_path(branch).read_text(encoding="utf-8"))
        self.assertEqual(
            {"assignment", "pr", "head", "state_at_delivery", "delivered_at"}, set(record)
        )
        self.assertEqual(self.PR_URL.format(number=5), record["pr"])
        self.assertEqual(head, record["head"])
        self.assertEqual(branch, record["assignment"]["branch"])
        self.assertEqual("First task", record["assignment"]["task"])
        self.assertFalse(self.assignment_file().exists())
        self.assertFalse((self.host / ".workspace" / ".locks" / "tommy.json").exists())
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())
        status = self.cli("status", "--agent", "tommy")
        self.assertEqual(branch, status["suspended"][0]["branch"])
        # the next task can start although the first pull request is still open
        second = self.prepare_tommy_task(
            "second-task", "Second task", extra_env={"FAKE_GH_LIST_JSON": json.dumps([self.pr_item(branch, head)])}
        )
        self.assertEqual("prepared", second["status"])
        self.assertEqual("docs/tommy-second-task", second["branch"])

    def test_prepare_still_blocks_when_one_open_pull_request_is_not_suspended(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        other = self.pr_item("docs/tommy-other", "c" * 40, number=9)
        blocked = self.prepare_tommy_task(
            "second-task", "Second task", expected=2,
            extra_env={"FAKE_GH_LIST_JSON": json.dumps([self.pr_item(branch, head), other])},
        )
        self.assertIn("not suspended", str(blocked["reason"]))
        self.assertIn("/pull/9", str(blocked["reason"]))
        self.assertNotIn("/pull/5", str(blocked["reason"]))

    def test_suspend_blocks_without_an_open_pull_request_a_matching_head_or_a_clean_pushed_branch(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        token = prepared["lock_token"]
        no_pr = self.suspend(token, [], expected=2)
        self.assertIn("no open pull request", str(no_pr["reason"]))
        wrong_head = self.suspend(token, [self.pr_item(branch, "b" * 40)], expected=2)
        self.assertIn("does not match the local HEAD", str(wrong_head["reason"]))
        other_branch = self.suspend(token, [self.pr_item("docs/tommy-elsewhere", head)], expected=2)
        self.assertIn("no open pull request", str(other_branch["reason"]))
        wrong_token = self.suspend("not-the-token", [self.pr_item(branch, head)], expected=2)
        self.assertIn("token does not match", str(wrong_token["reason"]))
        (workspace / "dirty.txt").write_text("untracked\n", encoding="utf-8")
        dirty = self.suspend(token, [self.pr_item(branch, head)], expected=2)
        self.assertIn("changes", str(dirty["reason"]))
        (workspace / "dirty.txt").unlink()
        (workspace / "e-commerce" / "later.md").write_text("later\n", encoding="utf-8")
        self.git(workspace, "add", "e-commerce")
        self.git(workspace, "commit", "-m", "docs: a commit that is not pushed")
        local_head = self.git(workspace, "rev-parse", "HEAD").stdout.strip()
        unpushed = self.suspend(token, [self.pr_item(branch, local_head)], expected=2)
        self.assertIn("not pushed", str(unpushed["reason"]))
        # nothing was moved by the refused attempts
        self.assertTrue(self.assignment_file().exists())
        self.assertFalse(self.record_path(branch).exists())
        self.assertEqual(branch, self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_suspend_blocks_on_main_and_without_the_lock(self) -> None:
        workspace = self.create_tommy()
        blocked = self.suspend("a" * 32, [], expected=2)
        self.assertIn("lock is missing", str(blocked["reason"]))
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_resume_restores_the_suspended_assignment_and_suspend_works_again(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        env = {"FAKE_GH_JSON": json.dumps(self.pr_item(branch, head))}

        def resume(task: str = "First task", expected: int = 0):
            return self.cli(
                "prepare", "--agent", "tommy", "--type", "docs", "--topic", "first-task", "--delivery", "open-pr",
                "--authorized-by", "josh", "--task", task, "--scope", "e-commerce", "--resume-pr", "5",
                expected=expected, extra_env=env,
            )

        different = resume(task="Another task", expected=2)
        self.assertIn("does not match", str(different["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())
        stale = self.cli(
            "prepare", "--agent", "tommy", "--type", "docs", "--topic", "first-task", "--delivery", "open-pr",
            "--authorized-by", "josh", "--task", "First task", "--scope", "e-commerce", "--resume-pr", "5",
            expected=2, extra_env={"FAKE_GH_JSON": json.dumps(self.pr_item(branch, "d" * 40))},
        )
        self.assertIn("does not match the pull-request head", str(stale["reason"]))
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())
        self.assertTrue(self.record_path(branch).exists())
        resumed = resume()
        self.assertEqual("resumed", resumed["status"])
        self.assertEqual(branch, self.git(workspace, "branch", "--show-current").stdout.strip())
        self.assertTrue(self.assignment_file().exists())
        self.assertFalse(self.record_path(branch).exists())
        again = self.suspend(resumed["lock_token"], [self.pr_item(branch, head)])
        self.assertEqual("suspended", again["status"])

    def test_resume_is_blocked_while_another_task_is_active(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        second = self.prepare_tommy_task(
            "second-task", "Second task", extra_env={"FAKE_GH_LIST_JSON": json.dumps([self.pr_item(branch, head)])}
        )
        self.cli("release", "--agent", "tommy", "--token", str(second["lock_token"]))
        blocked = self.cli(
            "prepare", "--agent", "tommy", "--type", "docs", "--topic", "first-task", "--delivery", "open-pr",
            "--authorized-by", "josh", "--task", "First task", "--scope", "e-commerce", "--resume-pr", "5",
            expected=2, extra_env={"FAKE_GH_JSON": json.dumps(self.pr_item(branch, head))},
        )
        self.assertIn("does not match", str(blocked["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        self.assertEqual("docs/tommy-second-task", self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_resume_is_blocked_when_active_assignment_metadata_remains_on_main(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        record = json.loads(self.record_path(branch).read_text(encoding="utf-8"))
        self.assignment_file().write_text(json.dumps(record["assignment"]), encoding="utf-8")
        blocked = self.cli(
            "prepare", "--agent", "tommy", "--type", "docs", "--topic", "first-task", "--delivery", "open-pr",
            "--authorized-by", "josh", "--task", "First task", "--scope", "e-commerce", "--resume-pr", "5",
            expected=2, extra_env={"FAKE_GH_JSON": json.dumps(self.pr_item(branch, head))},
        )
        self.assertIn("finish or suspend it before resuming another", str(blocked["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())

    def test_park_closes_a_suspended_assignment_only_after_the_merge(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        not_merged = self.cli(
            "park", "--agent", "tommy", "--pr", "5", expected=2,
            extra_env={"FAKE_GH_JSON": json.dumps(self.pr_item(branch, head))},
        )
        self.assertIn("not merged", str(not_merged["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        merged_item = self.pr_item(branch, head, state="MERGED")
        merged_item["mergedAt"] = "2026-11-11T12:00:00Z"
        wrong_head = dict(merged_item, headRefOid="e" * 40)
        mismatch = self.cli("park", "--agent", "tommy", "--pr", "5", expected=2, extra_env={"FAKE_GH_JSON": json.dumps(wrong_head)})
        self.assertIn("does not match the merged pull-request head", str(mismatch["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        parked = self.cli("park", "--agent", "tommy", "--pr", "5", extra_env={"FAKE_GH_JSON": json.dumps(merged_item)})
        self.assertEqual("parked", parked["status"])
        self.assertTrue(parked["suspended_record_removed"])
        self.assertFalse(self.record_path(branch).exists())
        gone = command(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=workspace, env=self.env
        )
        self.assertNotEqual(0, gone.returncode)
        self.assertEqual("main", self.git(workspace, "branch", "--show-current").stdout.strip())

    def owner_updates_branch(self, branch: str, diverge: bool) -> str:
        """The owner presses 'update branch' on GitHub: a commit lands on the task branch (or the history is replaced when diverge)."""
        updater = self.root / ("updater-diverge" if diverge else "updater")
        self.git(self.root, "clone", "--branch", "main" if diverge else branch, self.remote_url, str(updater))
        if diverge:
            self.git(updater, "switch", "-c", branch)
        (updater / "owner-update.md").write_text("update\n", encoding="utf-8")
        self.git(updater, "add", "owner-update.md")
        self.git(updater, "commit", "-m", "chore: update branch")
        if diverge:
            self.git(updater, "push", "--force", "origin", branch)
        else:
            self.git(updater, "push", "origin", branch)
        return self.git(updater, "rev-parse", "HEAD").stdout.strip()

    def test_park_of_a_suspended_assignment_accepts_a_branch_the_owner_updated(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        new_head = self.owner_updates_branch(branch, diverge=False)
        merged_item = self.pr_item(branch, new_head, state="MERGED")
        merged_item["mergedAt"] = "2026-11-13T12:00:00Z"
        parked = self.cli("park", "--agent", "tommy", "--pr", "5", extra_env={"FAKE_GH_JSON": json.dumps(merged_item)})
        self.assertEqual("parked", parked["status"])
        self.assertFalse(self.record_path(branch).exists())
        gone = command(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=workspace, env=self.env)
        self.assertNotEqual(0, gone.returncode)

    def test_park_of_a_suspended_assignment_blocks_when_the_local_branch_is_not_an_ancestor(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        new_head = self.owner_updates_branch(branch, diverge=True)
        merged_item = self.pr_item(branch, new_head, state="MERGED")
        merged_item["mergedAt"] = "2026-11-13T12:00:00Z"
        blocked = self.cli("park", "--agent", "tommy", "--pr", "5", expected=2, extra_env={"FAKE_GH_JSON": json.dumps(merged_item)})
        self.assertIn("does not match the merged pull-request head", str(blocked["reason"]))
        self.assertTrue(self.record_path(branch).exists())
        kept = command(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=workspace, env=self.env)
        self.assertEqual(0, kept.returncode)

    def test_park_of_a_suspended_assignment_leaves_the_current_task_alone(self) -> None:
        workspace, prepared, branch, head = self.start_pushed_task()
        self.suspend(prepared["lock_token"], [self.pr_item(branch, head)])
        second = self.prepare_tommy_task(
            "second-task", "Second task", extra_env={"FAKE_GH_LIST_JSON": json.dumps([self.pr_item(branch, head)])}
        )
        self.cli("release", "--agent", "tommy", "--token", str(second["lock_token"]))
        merged_item = self.pr_item(branch, head, state="MERGED")
        merged_item["mergedAt"] = "2026-11-11T12:00:00Z"
        parked = self.cli("park", "--agent", "tommy", "--pr", "5", extra_env={"FAKE_GH_JSON": json.dumps(merged_item)})
        self.assertEqual("parked", parked["status"])
        self.assertEqual("docs/tommy-second-task", self.git(workspace, "branch", "--show-current").stdout.strip())
        self.assertTrue(self.assignment_file().exists())
        self.assertFalse(self.record_path(branch).exists())


if __name__ == "__main__":
    unittest.main()
