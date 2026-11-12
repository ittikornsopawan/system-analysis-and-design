#!/usr/bin/env python3
"""Safely manage persistent full-clone workspaces for named agents."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys
import uuid
from typing import Any, Iterable
from urllib.parse import urlparse


REGISTRY_PATH = ".agents/team/agents.yaml"
ROLE_PREFIX = ".agents/agents/"
DEFAULT_BRANCH = "main"
WORKSPACE_ROOT = ".workspace"
ASSIGNMENT_VERSION = 1
ALLOWED_TYPES = {
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "refactor",
    "test",
}
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
TOPIC_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?$")
ROLE_RE = re.compile(r"^\.agents/agents/[a-z0-9-]+\.md$")
HTTPS_REMOTE_RE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?$"
)
SSH_REMOTE_RE = re.compile(
    r"^git@github\.com:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?$"
)


class Blocked(RuntimeError):
    """A safety gate prevented a mutation."""


def run(
    argv: list[str],
    *,
    cwd: Path,
    check: bool = True,
    redact: Iterable[str] = (),
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise Blocked(f"cannot run {argv[0]!r}: {exc}") from exc
    if check and result.returncode != 0:
        message = (result.stderr or result.stdout or "command failed").strip()
        for value in redact:
            if value:
                message = message.replace(value, "<redacted-origin>")
        raise Blocked(f"{' '.join(argv[:3])} failed: {message}")
    return result


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=cwd, check=check)


def git_root(path: Path) -> Path:
    result = git(path, "rev-parse", "--show-toplevel")
    return Path(result.stdout.strip()).resolve()


def resolve_host(explicit: str | None) -> Path:
    if explicit:
        host = Path(explicit).expanduser().resolve()
    else:
        current_root = git_root(Path.cwd())
        if current_root.parent.name == WORKSPACE_ROOT:
            host = current_root.parent.parent.resolve()
        else:
            host = current_root
    if not (host / ".git").exists():
        raise Blocked(f"primary checkout is not a Git repository: {host}")
    if git_root(host) != host:
        raise Blocked(f"primary checkout is not the Git root: {host}")
    return host


def validate_slug(value: str, label: str = "slug") -> str:
    if not SLUG_RE.fullmatch(value):
        raise Blocked(f"invalid {label}: {value!r}")
    return value


def validate_topic(value: str) -> str:
    if not TOPIC_RE.fullmatch(value):
        raise Blocked(f"invalid topic slug: {value!r}")
    return value


def parse_scalar(value: str, *, line: int) -> Any:
    if not value:
        raise Blocked(f"registry line {line}: missing scalar value")
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "[]":
        return []
    if value.isdigit():
        return int(value)
    if value.startswith(("'", '"')):
        if len(value) < 2 or value[-1] != value[0]:
            raise Blocked(f"registry line {line}: unterminated quoted scalar")
        try:
            parsed = json.loads(value) if value.startswith('"') else value[1:-1]
        except (json.JSONDecodeError, IndexError) as exc:
            raise Blocked(f"registry line {line}: invalid quoted scalar") from exc
        if not isinstance(parsed, str):
            raise Blocked(f"registry line {line}: scalar must be a string")
        return parsed
    if any(token in value for token in ("&", "*", "!!", "{", "}", "[", "]")):
        raise Blocked(f"registry line {line}: unsupported YAML feature")
    return value


def split_key_value(text: str, *, line: int) -> tuple[str, str]:
    if ":" not in text:
        raise Blocked(f"registry line {line}: expected key: value")
    key, value = text.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
        raise Blocked(f"registry line {line}: invalid key {key!r}")
    return key, value.strip()


def parse_registry(text: str) -> dict[str, Any]:
    top: dict[str, Any] = {}
    agents: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    capability_mode = False

    for number, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw:
            raise Blocked(f"registry line {number}: tabs are not allowed")
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw.strip()

        if indent == 0:
            capability_mode = False
            key, value = split_key_value(content, line=number)
            if key in top:
                raise Blocked(f"registry line {number}: duplicate key {key!r}")
            if key == "agents":
                if value:
                    raise Blocked(f"registry line {number}: agents must be a block list")
                top[key] = agents
            else:
                top[key] = parse_scalar(value, line=number)
            current = None
            continue

        if indent == 2 and content.startswith("- "):
            if "agents" not in top:
                raise Blocked(f"registry line {number}: agent before agents block")
            current = {}
            agents.append(current)
            capability_mode = False
            key, value = split_key_value(content[2:].strip(), line=number)
            current[key] = parse_scalar(value, line=number)
            continue

        if indent == 4 and current is not None:
            key, value = split_key_value(content, line=number)
            if key in current:
                raise Blocked(f"registry line {number}: duplicate agent key {key!r}")
            if key == "capabilities" and not value:
                current[key] = []
                capability_mode = True
            else:
                current[key] = parse_scalar(value, line=number)
                capability_mode = False
            continue

        if indent == 6 and current is not None and capability_mode and content.startswith("- "):
            value = parse_scalar(content[2:].strip(), line=number)
            if not isinstance(value, str):
                raise Blocked(f"registry line {number}: capability must be a string")
            current["capabilities"].append(value)
            continue

        raise Blocked(f"registry line {number}: unsupported indentation or structure")

    required_top = {
        "version",
        "authorized_user",
        "default_branch",
        "workspace_root",
        "agents",
    }
    if set(top) != required_top:
        missing = sorted(required_top - set(top))
        extra = sorted(set(top) - required_top)
        raise Blocked(f"registry top-level keys invalid; missing={missing}, extra={extra}")
    if top["version"] != 1:
        raise Blocked("registry version must be 1")
    validate_slug(str(top["authorized_user"]), "authorized_user")
    if top["default_branch"] != DEFAULT_BRANCH:
        raise Blocked(f"registry default_branch must be {DEFAULT_BRANCH!r}")
    if top["workspace_root"] != WORKSPACE_ROOT:
        raise Blocked(f"registry workspace_root must be {WORKSPACE_ROOT!r}")

    required_agent = {
        "name",
        "enabled",
        "role",
        "title",
        "scope",
        "reports_to",
        "workspace_key",
        "capabilities",
    }
    names: set[str] = set()
    for agent in agents:
        if set(agent) != required_agent:
            name = agent.get("name", "<unknown>")
            missing = sorted(required_agent - set(agent))
            extra = sorted(set(agent) - required_agent)
            raise Blocked(f"registry agent {name!r} keys invalid; missing={missing}, extra={extra}")
        name = validate_slug(str(agent["name"]), "agent name")
        if name in names:
            raise Blocked(f"duplicate registry agent: {name}")
        names.add(name)
        if not isinstance(agent["enabled"], bool):
            raise Blocked(f"agent {name}: enabled must be boolean")
        if not ROLE_RE.fullmatch(str(agent["role"])):
            raise Blocked(f"agent {name}: invalid role path")
        if not isinstance(agent["title"], str) or not agent["title"].strip():
            raise Blocked(f"agent {name}: title must be non-empty")
        validate_slug(str(agent["scope"]), f"agent {name} scope")
        validate_slug(str(agent["reports_to"]), f"agent {name} reports_to")
        if agent["workspace_key"] != name:
            raise Blocked(f"agent {name}: workspace_key must equal name")
        capabilities = agent["capabilities"]
        if not isinstance(capabilities, list) or any(
            capability != "delegate-delivery" for capability in capabilities
        ):
            raise Blocked(f"agent {name}: unsupported capability")
        if len(set(capabilities)) != len(capabilities):
            raise Blocked(f"agent {name}: duplicate capability")

    allowed_reports = names | {str(top["authorized_user"])}
    for agent in agents:
        if agent["reports_to"] not in allowed_reports:
            raise Blocked(
                f"agent {agent['name']}: reports_to {agent['reports_to']!r} is unknown"
            )
    return top


def validate_remote(remote: str) -> str:
    if not (HTTPS_REMOTE_RE.fullmatch(remote) or SSH_REMOTE_RE.fullmatch(remote)):
        raise Blocked("origin must be a credential-free GitHub HTTPS or SSH URL")
    return remote


def remote_slug(remote: str) -> str:
    validate_remote(remote)
    if remote.startswith("https://"):
        path = urlparse(remote).path.lstrip("/")
    else:
        path = remote.split(":", 1)[1]
    return path.removesuffix(".git")


def origin_for(repo: Path) -> str:
    result = git(repo, "config", "--get", "remote.origin.url")
    return validate_remote(result.stdout.strip())


def fetch_main(host: Path, remote: str) -> None:
    run(
        [
            "git",
            "fetch",
            "origin",
            f"{DEFAULT_BRANCH}:refs/remotes/origin/{DEFAULT_BRANCH}",
        ],
        cwd=host,
        redact=(remote,),
    )


def registry_from_origin_main(host: Path, *, fetch: bool = True) -> dict[str, Any]:
    remote = origin_for(host)
    if fetch:
        fetch_main(host, remote)
    result = git(host, "show", f"origin/{DEFAULT_BRANCH}:{REGISTRY_PATH}")
    registry = parse_registry(result.stdout)
    ignore = git(host, "show", f"origin/{DEFAULT_BRANCH}:.gitignore")
    if "/.workspace/" not in {line.strip() for line in ignore.stdout.splitlines()}:
        raise Blocked("origin/main must track an exact /.workspace/ ignore rule")
    for agent in registry["agents"]:
        role = agent["role"]
        exists = git(
            host,
            "cat-file",
            "-e",
            f"origin/{DEFAULT_BRANCH}:{role}",
            check=False,
        )
        if exists.returncode != 0:
            raise Blocked(f"agent {agent['name']}: role does not exist on origin/main")
    return registry


def agent_record(registry: dict[str, Any], name: str, *, require_enabled: bool = True) -> dict[str, Any]:
    validate_slug(name, "agent name")
    matches = [agent for agent in registry["agents"] if agent["name"] == name]
    if not matches:
        raise Blocked(f"agent {name!r} is not registered on origin/main")
    agent = matches[0]
    if require_enabled and not agent["enabled"]:
        raise Blocked(f"agent {name!r} is disabled")
    return agent


def validate_delivery(
    registry: dict[str, Any],
    *,
    assignee: str,
    delivery: str,
    authorized_by: str,
) -> None:
    agent_record(registry, assignee)
    if delivery == "none":
        return
    if delivery != "open-pr":
        raise Blocked(f"unsupported delivery mode: {delivery}")
    if authorized_by == registry["authorized_user"]:
        return
    validate_slug(authorized_by, "authorized_by")
    authorizer = agent_record(registry, authorized_by)
    if authorized_by == assignee:
        raise Blocked("an agent cannot self-authorize delivery")
    if "delegate-delivery" not in authorizer["capabilities"]:
        raise Blocked(f"agent {authorized_by!r} cannot delegate delivery")


def workspace_paths(host: Path, agent: dict[str, Any]) -> tuple[Path, Path, Path]:
    root = host / WORKSPACE_ROOT
    target = root / agent["workspace_key"]
    locks = root / ".locks"
    if root.is_symlink():
        raise Blocked("workspace root must not be a symlink")
    if root.exists() and not root.is_dir():
        raise Blocked("workspace root must be a directory")
    if target.is_symlink():
        raise Blocked("managed workspace must not be a symlink")
    if target.parent.resolve() != root.resolve():
        raise Blocked("managed workspace escapes the primary checkout")
    return root, target, locks


def assignment_path(root: Path, agent_name: str) -> Path:
    state = root / ".state"
    if state.is_symlink():
        raise Blocked("workspace state directory must not be a symlink")
    if state.exists() and not state.is_dir():
        raise Blocked("workspace state path must be a directory")
    return state / f"{agent_name}.json"


def normalize_scopes(values: list[str], agent: dict[str, Any]) -> list[str]:
    if not values:
        raise Blocked("at least one assignment scope is required")
    normalized: list[str] = []
    for value in values:
        if "," in value:
            raise Blocked(
                f"assignment scope {value!r} contains a comma; repeat --scope once per path, "
                "for example: --scope e-commerce/doc --scope tasks"
            )
        if value == ".":
            scope = "."
        else:
            if not value or "\\" in value:
                raise Blocked(f"invalid assignment scope: {value!r}")
            path = PurePosixPath(value)
            if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
                raise Blocked(f"invalid assignment scope: {value!r}")
            scope = path.as_posix().rstrip("/")
            if path.parts[0] in {".git", WORKSPACE_ROOT}:
                raise Blocked(f"assignment scope is reserved: {value!r}")
        if scope not in normalized:
            normalized.append(scope)
    agent_scope = agent["scope"]
    if agent_scope != "repository-wide":
        for scope in normalized:
            if scope == "." or not (
                scope == agent_scope or scope.startswith(agent_scope + "/")
            ):
                raise Blocked(
                    f"assignment scope {scope!r} exceeds agent scope {agent_scope!r}"
                )
    return normalized


def validate_task(value: str) -> str:
    task = value.strip()
    if not task or len(task) > 240 or any(ord(character) < 32 for character in task):
        raise Blocked("task must be a non-empty single-line value of at most 240 characters")
    return task


def write_assignment(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise Blocked("named agent already has an active assignment")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as exc:
        raise Blocked(f"cannot create assignment metadata: {exc}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_assignment(path: Path) -> dict[str, Any]:
    if not path.exists() or path.is_symlink():
        raise Blocked("active assignment metadata is missing or unsafe")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Blocked("active assignment metadata cannot be read") from exc
    return validate_assignment_payload(payload)


def validate_assignment_payload(payload: Any) -> dict[str, Any]:
    required = {
        "version",
        "agent",
        "task",
        "scope",
        "delivery",
        "authorized_by",
        "branch",
        "created_at",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise Blocked("active assignment metadata has an invalid schema")
    if payload["version"] != ASSIGNMENT_VERSION:
        raise Blocked("active assignment metadata version is unsupported")
    if not isinstance(payload["scope"], list) or not payload["scope"]:
        raise Blocked("active assignment metadata has no scope")
    return payload


def assignment_matches(
    payload: dict[str, Any],
    *,
    agent: str,
    task: str,
    scopes: list[str],
    delivery: str,
    authorized_by: str,
    branch: str,
) -> None:
    expected = {
        "agent": agent,
        "task": task,
        "scope": scopes,
        "delivery": delivery,
        "authorized_by": authorized_by,
        "branch": branch,
    }
    mismatches = [key for key, value in expected.items() if payload.get(key) != value]
    if mismatches:
        raise Blocked(f"assignment does not match active metadata: {', '.join(mismatches)}")


def acquire_lock(locks: Path, agent_name: str, purpose: str) -> tuple[str, Path]:
    if locks.is_symlink():
        raise Blocked("workspace lock directory must not be a symlink")
    if locks.exists() and not locks.is_dir():
        raise Blocked("workspace lock path must be a directory")
    try:
        locks.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise Blocked(f"cannot create workspace lock directory: {exc}") from exc
    lock_path = locks / f"{agent_name}.json"
    token = uuid.uuid4().hex
    payload = {
        "agent": agent_name,
        "purpose": purpose,
        "token": token,
        "pid": os.getpid(),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    try:
        descriptor = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise Blocked(f"workspace is locked: {lock_path}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.write("\n")
    return token, lock_path


def check_lock_token(lock_path: Path, token: str) -> None:
    if not lock_path.exists() or lock_path.is_symlink():
        raise Blocked("workspace lock is missing or unsafe")
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Blocked("workspace lock cannot be read") from exc
    if payload.get("token") != token:
        raise Blocked("workspace lock token does not match")


def release_lock(lock_path: Path, token: str) -> None:
    check_lock_token(lock_path, token)
    lock_path.unlink()


# A task whose pull request is open can be suspended: its assignment moves to a record in
# .workspace/.state/<agent>-prs/<branch-slug>.json (the format of the records of the previous reviewer) and the
# workspace goes back to main, so the agent can start the next task without waiting for the merge.
SUSPENDED_KEYS = {"assignment", "pr", "head", "state_at_delivery", "delivered_at"}
SUSPENDED_OPTIONAL_KEYS = {"owner_override"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def branch_slug(branch: str) -> str:
    return branch.replace("/", "__")


def suspended_dir(root: Path, agent_name: str) -> Path:
    state = root / ".state"
    if state.is_symlink():
        raise Blocked("workspace state directory must not be a symlink")
    directory = state / f"{agent_name}-prs"
    if directory.is_symlink():
        raise Blocked("suspended assignment directory must not be a symlink")
    if directory.exists() and not directory.is_dir():
        raise Blocked("suspended assignment path must be a directory")
    return directory


def read_suspended(path: Path, agent_name: str, expected_slug: str) -> dict[str, Any]:
    if not path.exists() or path.is_symlink() or not path.is_file():
        raise Blocked("suspended assignment record is missing or unsafe")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise Blocked("suspended assignment record cannot be read") from exc
    if (
        not isinstance(payload, dict)
        or not SUSPENDED_KEYS <= set(payload)
        or not set(payload) <= SUSPENDED_KEYS | SUSPENDED_OPTIONAL_KEYS
    ):
        raise Blocked("suspended assignment record has an invalid schema")
    assignment = validate_assignment_payload(payload["assignment"])
    if assignment["agent"] != agent_name or path.stem != branch_slug(assignment["branch"]):
        raise Blocked("suspended assignment record does not match its agent or branch")
    require_pr_url_matches(str(payload["pr"]), expected_slug)
    if not SHA_RE.fullmatch(str(payload["head"])):
        raise Blocked("suspended assignment record has an invalid head")
    return payload


def suspended_branches(directory: Path, agent_name: str, expected_slug: str) -> dict[str, dict[str, Any]]:
    """Valid suspended records of the agent by branch; a record that cannot be read is not counted."""
    records: dict[str, dict[str, Any]] = {}
    if not directory.is_dir():
        return records
    for path in sorted(directory.glob("*.json")):
        try:
            record = read_suspended(path, agent_name, expected_slug)
        except Blocked:
            continue
        records[record["assignment"]["branch"]] = record
    return records


def clean_workspace(workspace: Path) -> None:
    status = git(workspace, "status", "--porcelain=v1", "--untracked-files=all")
    if status.stdout.strip():
        raise Blocked("managed workspace has tracked or untracked changes")


def current_branch(workspace: Path) -> str:
    result = git(workspace, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if result.returncode != 0 or not result.stdout.strip():
        raise Blocked("managed workspace is in detached HEAD state")
    return result.stdout.strip()


def branch_belongs_to_agent(branch: str, agent_name: str) -> bool:
    types = "|".join(sorted(ALLOWED_TYPES))
    return bool(
        re.fullmatch(
            rf"(?:{types})/{re.escape(agent_name)}-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
            branch,
        )
    )


def verify_clone_structure(workspace: Path, expected_remote: str) -> None:
    if not workspace.exists() or workspace.is_symlink():
        raise Blocked("managed workspace is missing or unsafe")
    if git_root(workspace) != workspace.resolve():
        raise Blocked("managed workspace path is not its Git root")
    git_directory = workspace / ".git"
    if not git_directory.is_dir() or git_directory.is_symlink():
        raise Blocked("managed workspace must be a full clone with its own .git directory")
    common = git(workspace, "rev-parse", "--git-common-dir").stdout.strip()
    common_path = (workspace / common).resolve() if not Path(common).is_absolute() else Path(common).resolve()
    if common_path != git_directory.resolve():
        raise Blocked("managed workspace shares Git metadata with another checkout")
    if origin_for(workspace) != expected_remote:
        raise Blocked("managed workspace origin does not match the primary checkout")


def verify_workspace(
    workspace: Path,
    expected_remote: str,
    *,
    host: Path,
    agent_name: str,
) -> None:
    verify_clone_structure(workspace, expected_remote)
    configured_host = git(
        workspace,
        "config",
        "--get",
        "agent.workspaceHost",
        check=False,
    ).stdout.strip()
    configured_agent = git(
        workspace,
        "config",
        "--get",
        "agent.name",
        check=False,
    ).stdout.strip()
    if configured_host != str(host) or configured_agent != agent_name:
        raise Blocked("managed workspace identity markers do not match the registry")


def output(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def cmd_validate(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    registry = registry_from_origin_main(host)
    output({"status": "valid", "agents": [agent["name"] for agent in registry["agents"]]})


def cmd_create(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent)
    root, target, locks = workspace_paths(host, agent)
    try:
        root.mkdir(mode=0o700, exist_ok=True)
    except OSError as exc:
        raise Blocked(f"cannot create workspace root: {exc}") from exc
    token, lock_path = acquire_lock(locks, agent["name"], "create")
    staging = root / f".staging-{agent['name']}-{uuid.uuid4().hex}"
    try:
        if target.exists():
            raise Blocked(f"managed workspace already exists: {target}")
        staging.mkdir(mode=0o700)
        checkout = staging / "checkout"
        run(
            [
                "git",
                "clone",
                "--branch",
                DEFAULT_BRANCH,
                "--origin",
                "origin",
                remote,
                str(checkout),
            ],
            cwd=host,
            redact=(remote,),
        )
        verify_clone_structure(checkout, remote)
        clean_workspace(checkout)
        if current_branch(checkout) != DEFAULT_BRANCH:
            raise Blocked("new clone did not checkout main")
        git(checkout, "config", "agent.workspaceHost", str(host))
        git(checkout, "config", "agent.name", agent["name"])
        verify_workspace(
            checkout,
            remote,
            host=host,
            agent_name=agent["name"],
        )
        if target.exists():
            raise Blocked("managed workspace target appeared during clone")
        os.rename(checkout, target)
        output({"status": "created", "agent": agent["name"], "workspace": str(target)})
    finally:
        try:
            if staging.exists():
                shutil.rmtree(staging)
        finally:
            release_lock(lock_path, token)


def main_relation(workspace: Path) -> str:
    local = git(workspace, "rev-parse", DEFAULT_BRANCH).stdout.strip()
    remote = git(workspace, "rev-parse", f"origin/{DEFAULT_BRANCH}").stdout.strip()
    if local == remote:
        return "synchronized"
    local_ancestor = git(
        workspace,
        "merge-base",
        "--is-ancestor",
        DEFAULT_BRANCH,
        f"origin/{DEFAULT_BRANCH}",
        check=False,
    )
    if local_ancestor.returncode == 0:
        return "behind"
    remote_ancestor = git(
        workspace,
        "merge-base",
        "--is-ancestor",
        f"origin/{DEFAULT_BRANCH}",
        DEFAULT_BRANCH,
        check=False,
    )
    if remote_ancestor.returncode == 0:
        return "ahead"
    return "diverged"


def require_pr_url_matches(url: str, expected_slug: str) -> None:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or len(parts) != 4
        or parts[2] != "pull"
        or not parts[3].isdigit()
        or "/".join(parts[:2]) != expected_slug
    ):
        raise Blocked("pull request does not belong to the managed workspace origin")


def gh_pr(workspace: Path, selector: str, expected_remote: str) -> dict[str, Any]:
    slug = remote_slug(expected_remote)
    if selector.startswith(("http://", "https://")):
        require_pr_url_matches(selector, slug)
    fields = "state,mergedAt,baseRefName,headRefName,headRefOid,url,number"
    result = run(
        ["gh", "pr", "view", selector, "--repo", slug, "--json", fields],
        cwd=workspace,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise Blocked("GitHub CLI returned invalid pull-request JSON") from exc
    required = {"state", "mergedAt", "baseRefName", "headRefName", "headRefOid", "url", "number"}
    if not required.issubset(payload):
        raise Blocked("GitHub pull-request response is incomplete")
    require_pr_url_matches(str(payload["url"]), slug)
    return payload


def open_agent_pull_requests(
    workspace: Path,
    agent_name: str,
    expected_remote: str,
) -> list[dict[str, Any]]:
    slug = remote_slug(expected_remote)
    fields = "state,baseRefName,headRefName,headRefOid,url,number"
    result = run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            slug,
            "--state",
            "open",
            "--limit",
            "1000",
            "--json",
            fields,
        ],
        cwd=workspace,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise Blocked("GitHub CLI returned invalid pull-request list JSON") from exc
    if not isinstance(payload, list):
        raise Blocked("GitHub pull-request list response is incomplete")
    matches: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict) or not {
            "state",
            "baseRefName",
            "headRefName",
            "headRefOid",
            "url",
            "number",
        }.issubset(item):
            raise Blocked("GitHub pull-request list response is incomplete")
        require_pr_url_matches(str(item["url"]), slug)
        if branch_belongs_to_agent(str(item["headRefName"]), agent_name):
            matches.append(item)
    return matches


def cmd_status(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    expected_remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent, require_enabled=False)
    root, target, locks = workspace_paths(host, agent)
    lock_path = locks / f"{agent['name']}.json"
    active_assignment = assignment_path(root, agent["name"])
    payload: dict[str, Any] = {
        "agent": agent["name"],
        "enabled": agent["enabled"],
        "locked": lock_path.exists(),
        "workspace": str(target),
        "assignment_active": active_assignment.exists(),
    }
    if active_assignment.exists() or active_assignment.is_symlink():
        assignment = read_assignment(active_assignment)
        payload["assignment"] = {
            "task": assignment["task"],
            "scope": assignment["scope"],
            "delivery": assignment["delivery"],
            "branch": assignment["branch"],
        }
    records = suspended_branches(
        suspended_dir(root, agent["name"]),
        agent["name"],
        remote_slug(expected_remote),
    )
    if records:
        payload["suspended"] = [
            {"branch": name, "pull_request": record["pr"], "head": record["head"]}
            for name, record in sorted(records.items())
        ]
    if not target.exists():
        payload["status"] = "missing"
        output(payload)
        return
    verify_workspace(
        target,
        expected_remote,
        host=host,
        agent_name=agent["name"],
    )
    branch = current_branch(target)
    dirty = bool(git(target, "status", "--porcelain=v1", "--untracked-files=all").stdout.strip())
    payload.update({"branch": branch, "dirty": dirty})
    if lock_path.exists():
        payload["status"] = "locked"
        payload["remote_refresh"] = "skipped"
        if args.pr:
            payload["pull_request"] = gh_pr(target, args.pr, expected_remote)
        output(payload)
        return
    fetch_main(target, expected_remote)
    if branch == DEFAULT_BRANCH:
        relation = main_relation(target)
        payload["main_relation"] = relation
        payload["status"] = "parked" if not dirty and relation == "synchronized" else "blocked"
    else:
        payload["status"] = "task-branch"
        if args.pr:
            payload["pull_request"] = gh_pr(target, args.pr, expected_remote)
    output(payload)


def run_baselines(workspace: Path, commands: list[str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for command in commands:
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            raise Blocked(f"baseline command cannot be parsed: {command}") from exc
        if not argv:
            raise Blocked("baseline command must not be empty")
        result = run(argv, cwd=workspace, check=False)
        record = {
            "command": command,
            "returncode": result.returncode,
            "last_output": (result.stdout or result.stderr).strip().splitlines()[-1:][0]
            if (result.stdout or result.stderr).strip()
            else "",
        }
        results.append(record)
        if result.returncode != 0:
            raise Blocked(f"baseline failed: {command}: {record['last_output']}")
    return results


def resume_suspended(
    target: Path,
    agent: dict[str, Any],
    args: argparse.Namespace,
    *,
    task: str,
    scopes: list[str],
    expected_remote: str,
    records_dir: Path,
    active_assignment: Path,
    token: str,
) -> None:
    """Make the suspended assignment of an open pull request the active one again."""
    if active_assignment.exists() or active_assignment.is_symlink():
        raise Blocked("named agent has an active assignment; finish or suspend it before resuming another")
    pull_request = gh_pr(target, args.resume_pr, expected_remote)
    branch = str(pull_request["headRefName"])
    record_path = records_dir / f"{branch_slug(branch)}.json"
    if not record_path.exists() and not record_path.is_symlink():
        raise Blocked("pull request has no suspended assignment record")
    record = read_suspended(record_path, agent["name"], remote_slug(expected_remote))
    assignment = record["assignment"]
    assignment_matches(
        assignment,
        agent=agent["name"],
        task=task,
        scopes=scopes,
        delivery=args.delivery,
        authorized_by=args.authorized_by,
        branch=branch,
    )
    if pull_request["state"] != "OPEN":
        raise Blocked("review resume requires an open pull request")
    if pull_request["baseRefName"] != DEFAULT_BRANCH:
        raise Blocked("pull request base is not main")
    if str(pull_request["url"]) != str(record["pr"]):
        raise Blocked("pull request does not match the suspended record")
    exists = git(target, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False)
    if exists.returncode != 0:
        raise Blocked("local task branch of the suspended assignment is missing")
    git(target, "switch", branch)
    try:
        pr_head = str(pull_request["headRefOid"])
        if git(target, "rev-parse", "HEAD").stdout.strip() != pr_head:
            # the owner may have updated the branch on GitHub: accept a pure fast-forward and nothing else
            git(target, "fetch", "origin", branch)
            remote_head = git(target, "rev-parse", f"refs/remotes/origin/{branch}").stdout.strip()
            behind = git(target, "merge-base", "--is-ancestor", "HEAD", remote_head, check=False)
            if remote_head != pr_head or behind.returncode != 0:
                raise Blocked("local HEAD does not match the pull-request head")
            git(target, "merge", "--ff-only", remote_head)
        write_assignment(active_assignment, assignment)
        record_path.unlink()
    except Blocked:
        git(target, "switch", DEFAULT_BRANCH, check=False)
        raise
    output(
        {
            "status": "resumed",
            "agent": agent["name"],
            "workspace": str(target),
            "branch": branch,
            "lock_token": token,
            "pull_request": pull_request["url"],
        }
    )


def cmd_suspend(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    expected_remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent, require_enabled=False)
    root, target, locks = workspace_paths(host, agent)
    active_assignment = assignment_path(root, agent["name"])
    verify_workspace(
        target,
        expected_remote,
        host=host,
        agent_name=agent["name"],
    )
    lock_path = locks / f"{agent['name']}.json"
    check_lock_token(lock_path, args.token)
    clean_workspace(target)
    branch = current_branch(target)
    if branch == DEFAULT_BRANCH:
        raise Blocked("workspace is on main; there is no task to suspend")
    if not branch_belongs_to_agent(branch, agent["name"]):
        raise Blocked("current branch does not belong to the named agent")
    assignment = read_assignment(active_assignment)
    if assignment["agent"] != agent["name"] or assignment["branch"] != branch:
        raise Blocked("active assignment does not match the current workspace")
    if assignment["delivery"] != "open-pr":
        raise Blocked("active assignment did not authorize pull-request delivery")
    local_head = git(target, "rev-parse", "HEAD").stdout.strip()
    pushed = git(target, "ls-remote", "--heads", "origin", branch).stdout.strip()
    if not pushed or pushed.split()[0] != local_head:
        raise Blocked("HEAD of the task branch is not pushed to origin")
    pulls = [
        item
        for item in open_agent_pull_requests(target, agent["name"], expected_remote)
        if item["headRefName"] == branch
    ]
    if not pulls:
        raise Blocked("GitHub has no open pull request for this task branch")
    if len(pulls) > 1:
        raise Blocked("GitHub has more than one open pull request for this task branch")
    pull_request = pulls[0]
    if pull_request["baseRefName"] != DEFAULT_BRANCH:
        raise Blocked("pull request base is not main")
    if pull_request["headRefOid"] != local_head:
        raise Blocked("pull-request head does not match the local HEAD")
    directory = suspended_dir(root, agent["name"])
    record_path = directory / f"{branch_slug(branch)}.json"
    if record_path.exists() or record_path.is_symlink():
        raise Blocked("a suspended record already exists for this branch")
    record = {
        "assignment": assignment,
        "pr": str(pull_request["url"]),
        "head": local_head,
        "state_at_delivery": "OPEN",
        "delivered_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    try:
        directory.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(record_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except OSError as exc:
        raise Blocked(f"cannot create the suspended record: {exc}") from exc
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        git(target, "switch", DEFAULT_BRANCH)
    except Blocked:
        record_path.unlink()
        raise
    active_assignment.unlink()
    release_lock(lock_path, args.token)
    output(
        {
            "status": "suspended",
            "agent": agent["name"],
            "workspace": str(target),
            "branch": branch,
            "pull_request": record["pr"],
            "record": str(record_path),
        }
    )


def cmd_prepare(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    expected_remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent)
    task = validate_task(args.task)
    scopes = normalize_scopes(args.scope, agent)
    validate_delivery(
        registry,
        assignee=agent["name"],
        delivery=args.delivery,
        authorized_by=args.authorized_by,
    )
    root, target, locks = workspace_paths(host, agent)
    active_assignment = assignment_path(root, agent["name"])
    verify_workspace(
        target,
        expected_remote,
        host=host,
        agent_name=agent["name"],
    )
    token, lock_path = acquire_lock(locks, agent["name"], "prepare")
    keep_lock = False
    try:
        clean_workspace(target)
        fetch_main(target, expected_remote)
        branch = current_branch(target)
        if args.resume_pr:
            slug = remote_slug(expected_remote)
            records_dir = suspended_dir(root, agent["name"])
            if branch == DEFAULT_BRANCH:
                if not suspended_branches(records_dir, agent["name"], slug):
                    raise Blocked("cannot resume a pull request while parked on main")
                resume_suspended(
                    target,
                    agent,
                    args,
                    task=task,
                    scopes=scopes,
                    expected_remote=expected_remote,
                    records_dir=records_dir,
                    active_assignment=active_assignment,
                    token=token,
                )
                keep_lock = True
                return
            if not branch_belongs_to_agent(branch, agent["name"]):
                raise Blocked("current branch does not belong to the named agent")
            assignment = read_assignment(active_assignment)
            assignment_matches(
                assignment,
                agent=agent["name"],
                task=task,
                scopes=scopes,
                delivery=args.delivery,
                authorized_by=args.authorized_by,
                branch=branch,
            )
            pull_request = gh_pr(target, args.resume_pr, expected_remote)
            if pull_request["state"] != "OPEN":
                raise Blocked("review resume requires an open pull request")
            if pull_request["baseRefName"] != DEFAULT_BRANCH:
                raise Blocked("pull request base is not main")
            if pull_request["headRefName"] != branch:
                raise Blocked("pull request head does not match the current branch")
            local_head = git(target, "rev-parse", "HEAD").stdout.strip()
            if pull_request["headRefOid"] != local_head:
                raise Blocked("local HEAD does not match the pull-request head")
            keep_lock = True
            output(
                {
                    "status": "review-resumed",
                    "agent": agent["name"],
                    "workspace": str(target),
                    "branch": branch,
                    "lock_token": token,
                    "pull_request": pull_request["url"],
                }
            )
            return

        if branch != DEFAULT_BRANCH:
            raise Blocked("workspace has an active task branch; resume or reconcile it first")
        if active_assignment.exists() or active_assignment.is_symlink():
            raise Blocked("named agent has active assignment metadata; reconcile it first")
        open_pull_requests = open_agent_pull_requests(
            target,
            agent["name"],
            expected_remote,
        )
        suspended = suspended_branches(
            suspended_dir(root, agent["name"]),
            agent["name"],
            remote_slug(expected_remote),
        )
        not_suspended = [item for item in open_pull_requests if item["headRefName"] not in suspended]
        if not_suspended:
            urls = ", ".join(str(item["url"]) for item in not_suspended)
            raise Blocked(
                f"named agent has an open pull request whose assignment is not suspended: {urls}; "
                "run suspend for it first"
            )
        relation = main_relation(target)
        if relation not in {"synchronized", "behind"}:
            raise Blocked(f"local main is {relation}; fast-forward is unsafe")
        if relation == "behind":
            git(target, "merge", "--ff-only", f"origin/{DEFAULT_BRANCH}")
        baseline_head = git(target, "rev-parse", "HEAD").stdout.strip()
        baselines = run_baselines(target, args.baseline_command or [])
        clean_workspace(target)
        if current_branch(target) != DEFAULT_BRANCH:
            raise Blocked("baseline changed the current branch")
        if git(target, "rev-parse", "HEAD").stdout.strip() != baseline_head:
            raise Blocked("baseline changed the main commit")
        if main_relation(target) != "synchronized":
            raise Blocked("baseline changed main synchronization")
        if args.type not in ALLOWED_TYPES:
            raise Blocked(f"unsupported branch type: {args.type}")
        branch_name = f"{args.type}/{agent['name']}-{validate_topic(args.topic)}"
        local_exists = git(
            target,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{branch_name}",
            check=False,
        )
        if local_exists.returncode == 0:
            raise Blocked(f"local branch already exists: {branch_name}")
        remote_exists = git(
            target,
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            branch_name,
            check=False,
        )
        if remote_exists.returncode == 0:
            raise Blocked(f"remote branch already exists: {branch_name}")
        if remote_exists.returncode not in {0, 2}:
            raise Blocked("could not determine whether the task branch exists remotely")
        git(target, "switch", "-c", branch_name)
        write_assignment(
            active_assignment,
            {
                "version": ASSIGNMENT_VERSION,
                "agent": agent["name"],
                "task": task,
                "scope": scopes,
                "delivery": args.delivery,
                "authorized_by": args.authorized_by,
                "branch": branch_name,
                "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            },
        )
        keep_lock = True
        output(
            {
                "status": "prepared",
                "agent": agent["name"],
                "workspace": str(target),
                "branch": branch_name,
                "delivery": args.delivery,
                "authorized_by": args.authorized_by,
                "task": task,
                "scope": scopes,
                "baseline": baselines if baselines else "not-declared",
                "lock_token": token,
            }
        )
    finally:
        if not keep_lock and lock_path.exists():
            release_lock(lock_path, token)


def cmd_release(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    validate_slug(args.agent, "agent name")
    root = host / WORKSPACE_ROOT
    if root.is_symlink():
        raise Blocked("workspace root must not be a symlink")
    lock_path = root / ".locks" / f"{args.agent}.json"
    release_lock(lock_path, args.token)
    output({"status": "released", "agent": args.agent})


def nul_paths(result: subprocess.CompletedProcess[str]) -> set[str]:
    if result.returncode != 0:
        message = (result.stderr or result.stdout or "git path query failed").strip()
        raise Blocked(message)
    return {path for path in result.stdout.split("\0") if path}


def changed_paths(workspace: Path) -> set[str]:
    paths = nul_paths(
        git(
            workspace,
            "diff",
            "--name-only",
            "-z",
            f"{DEFAULT_BRANCH}...HEAD",
            check=False,
        )
    )
    paths.update(
        nul_paths(
            git(
                workspace,
                "diff",
                "--name-only",
                "-z",
                "HEAD",
                check=False,
            )
        )
    )
    paths.update(
        nul_paths(
            git(
                workspace,
                "ls-files",
                "--others",
                "--exclude-standard",
                "-z",
                check=False,
            )
        )
    )
    return paths


def path_in_scope(path: str, scopes: list[str]) -> bool:
    return any(
        scope == "." or path == scope or path.startswith(scope.rstrip("/") + "/")
        for scope in scopes
    )


def cmd_delivery_check(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    expected_remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent)
    root, target, locks = workspace_paths(host, agent)
    verify_workspace(
        target,
        expected_remote,
        host=host,
        agent_name=agent["name"],
    )
    if git_root(Path.cwd()) != target:
        raise Blocked("delivery check must run from the named agent's managed workspace")
    lock_path = locks / f"{agent['name']}.json"
    if not lock_path.exists() or lock_path.is_symlink():
        raise Blocked("delivery requires the active editing-session lock")
    branch = current_branch(target)
    assignment = read_assignment(assignment_path(root, agent["name"]))
    if assignment["agent"] != agent["name"] or assignment["branch"] != branch:
        raise Blocked("active assignment does not match the current workspace")
    normalized_scopes = normalize_scopes(assignment["scope"], agent)
    if normalized_scopes != assignment["scope"]:
        raise Blocked("active assignment scope is not normalized")
    validate_task(str(assignment["task"]))
    if assignment["delivery"] != "open-pr":
        raise Blocked("active assignment did not authorize pull-request delivery")
    validate_delivery(
        registry,
        assignee=agent["name"],
        delivery=assignment["delivery"],
        authorized_by=assignment["authorized_by"],
    )
    paths = sorted(changed_paths(target))
    outside = [path for path in paths if not path_in_scope(path, assignment["scope"])]
    if outside:
        raise Blocked(f"changed paths exceed assignment scope: {', '.join(outside)}")
    output(
        {
            "status": "delivery-authorized",
            "agent": agent["name"],
            "branch": branch,
            "task": assignment["task"],
            "scope": assignment["scope"],
            "authorized_by": assignment["authorized_by"],
            "changed_paths": paths,
        }
    )


def park_suspended(
    target: Path,
    agent: dict[str, Any],
    pull_request: dict[str, Any],
    *,
    record_path: Path,
    current: str,
    expected_remote: str,
) -> None:
    """Close a suspended assignment after its pull request is merged: check the merge, delete the local branch, delete the record."""
    record = read_suspended(record_path, agent["name"], remote_slug(expected_remote))
    assignment = record["assignment"]
    branch = assignment["branch"]
    if assignment["delivery"] != "open-pr":
        raise Blocked("suspended assignment did not authorize pull-request delivery")
    if pull_request["state"] != "MERGED" or not pull_request["mergedAt"]:
        raise Blocked("pull request is not merged")
    if pull_request["baseRefName"] != DEFAULT_BRANCH:
        raise Blocked("pull request base is not main")
    if pull_request["headRefName"] != branch or str(pull_request["url"]) != str(record["pr"]):
        raise Blocked("pull request does not match the suspended record")
    if current == branch:
        raise Blocked("the suspended task branch is checked out")
    exists = git(target, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False)
    if exists.returncode == 0:
        local_head = git(target, "rev-parse", f"refs/heads/{branch}").stdout.strip()
        if pull_request["headRefOid"] != local_head:
            raise Blocked("local task branch does not match the merged pull-request head")
        remote_head = git(target, "ls-remote", "--heads", "origin", branch).stdout.strip()
        if remote_head and remote_head.split()[0] != local_head:
            raise Blocked("remote task branch no longer matches local HEAD")
    if current == DEFAULT_BRANCH:
        relation = main_relation(target)
        if relation not in {"synchronized", "behind"}:
            raise Blocked(f"local main is {relation}; fast-forward is unsafe")
        if relation == "behind":
            git(target, "merge", "--ff-only", f"origin/{DEFAULT_BRANCH}")
    if exists.returncode == 0:
        git(target, "branch", "-D", branch)
    record_path.unlink()
    output(
        {
            "status": "parked",
            "agent": agent["name"],
            "workspace": str(target),
            "branch_deleted_locally": branch if exists.returncode == 0 else None,
            "pull_request": pull_request["url"],
            "suspended_record_removed": True,
        }
    )


def cmd_park(args: argparse.Namespace) -> None:
    host = resolve_host(args.host)
    expected_remote = origin_for(host)
    registry = registry_from_origin_main(host)
    agent = agent_record(registry, args.agent, require_enabled=False)
    root, target, locks = workspace_paths(host, agent)
    active_assignment = assignment_path(root, agent["name"])
    verify_workspace(
        target,
        expected_remote,
        host=host,
        agent_name=agent["name"],
    )
    token, lock_path = acquire_lock(locks, agent["name"], "park")
    try:
        clean_workspace(target)
        fetch_main(target, expected_remote)
        branch = current_branch(target)
        records_dir = suspended_dir(root, agent["name"])
        if records_dir.is_dir() and any(records_dir.glob("*.json")):
            candidate = gh_pr(target, args.pr, expected_remote)
            record_path = records_dir / f"{branch_slug(str(candidate['headRefName']))}.json"
            if record_path.exists() or record_path.is_symlink():
                park_suspended(
                    target,
                    agent,
                    candidate,
                    record_path=record_path,
                    current=branch,
                    expected_remote=expected_remote,
                )
                return
        if branch == DEFAULT_BRANCH:
            if active_assignment.exists() or active_assignment.is_symlink():
                raise Blocked("workspace is on main but active assignment metadata remains")
            if main_relation(target) != "synchronized":
                raise Blocked("workspace is on main but is not synchronized")
            output({"status": "already-parked", "agent": agent["name"], "workspace": str(target)})
            return
        if not branch_belongs_to_agent(branch, agent["name"]):
            raise Blocked("current branch does not belong to the named agent")
        assignment = read_assignment(active_assignment)
        if assignment["agent"] != agent["name"] or assignment["branch"] != branch:
            raise Blocked("active assignment does not match the current workspace")
        if assignment["delivery"] != "open-pr":
            raise Blocked("active assignment did not authorize pull-request delivery")
        pull_request = gh_pr(target, args.pr, expected_remote)
        if pull_request["state"] != "MERGED" or not pull_request["mergedAt"]:
            raise Blocked("pull request is not merged")
        if pull_request["baseRefName"] != DEFAULT_BRANCH:
            raise Blocked("pull request base is not main")
        if pull_request["headRefName"] != branch:
            raise Blocked("pull request head does not match the current branch")
        local_head = git(target, "rev-parse", "HEAD").stdout.strip()
        if pull_request["headRefOid"] != local_head:
            raise Blocked("local HEAD does not match the merged pull-request head")
        remote_head = git(
            target,
            "ls-remote",
            "--heads",
            "origin",
            branch,
        ).stdout.strip()
        if remote_head and remote_head.split()[0] != local_head:
            raise Blocked("remote task branch no longer matches local HEAD")
        relation = main_relation(target)
        if relation not in {"synchronized", "behind"}:
            raise Blocked(f"local main is {relation}; fast-forward is unsafe")
        git(target, "switch", DEFAULT_BRANCH)
        if relation == "behind":
            git(target, "merge", "--ff-only", f"origin/{DEFAULT_BRANCH}")
        git(target, "branch", "-D", branch)
        active_assignment.unlink()
        output(
            {
                "status": "parked",
                "agent": agent["name"],
                "workspace": str(target),
                "branch_deleted_locally": branch,
                "pull_request": pull_request["url"],
            }
        )
    finally:
        if lock_path.exists():
            release_lock(lock_path, token)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate origin/main registry and ignore policy")
    validate.add_argument("--host")
    validate.set_defaults(func=cmd_validate)

    create = subparsers.add_parser("create", help="create a missing named-agent clone")
    create.add_argument("--agent", required=True)
    create.add_argument("--host")
    create.set_defaults(func=cmd_create)

    status = subparsers.add_parser("status", help="inspect a named-agent workspace")
    status.add_argument("--agent", required=True)
    status.add_argument("--host")
    status.add_argument("--pr", help="optional pull-request number or URL to inspect")
    status.set_defaults(func=cmd_status)

    prepare = subparsers.add_parser("prepare", help="prepare a task branch or resume review")
    prepare.add_argument("--agent", required=True)
    prepare.add_argument("--host")
    prepare.add_argument("--type", required=True)
    prepare.add_argument("--topic", required=True)
    prepare.add_argument("--delivery", choices=("none", "open-pr"), required=True)
    prepare.add_argument("--authorized-by", required=True)
    prepare.add_argument("--task", required=True)
    prepare.add_argument("--scope", action="append", required=True)
    prepare.add_argument("--baseline-command", action="append", default=[])
    prepare.add_argument("--resume-pr")
    prepare.set_defaults(func=cmd_prepare)

    release = subparsers.add_parser("release", help="release the active execution lock")
    release.add_argument("--agent", required=True)
    release.add_argument("--token", required=True)
    release.add_argument("--host")
    release.set_defaults(func=cmd_release)

    suspend = subparsers.add_parser(
        "suspend",
        help="move the assignment of a task whose pull request is open to a record and return to main",
    )
    suspend.add_argument("--agent", required=True)
    suspend.add_argument("--token", required=True)
    suspend.add_argument("--host")
    suspend.set_defaults(func=cmd_suspend)

    delivery_check = subparsers.add_parser(
        "delivery-check",
        help="validate delegated delivery and changed paths against active assignment metadata",
    )
    delivery_check.add_argument("--agent", required=True)
    delivery_check.add_argument("--host")
    delivery_check.set_defaults(func=cmd_delivery_check)

    park = subparsers.add_parser("park", help="verify a merged PR and return the workspace to main")
    park.add_argument("--agent", required=True)
    park.add_argument("--pr", required=True)
    park.add_argument("--host")
    park.set_defaults(func=cmd_park)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Blocked as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, indent=2), file=sys.stderr)
        return 2
    except OSError as exc:
        print(
            json.dumps({"status": "blocked", "reason": f"filesystem operation failed: {exc}"}, indent=2),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
