"""Site session: staged file changes, commit, and undo/redo history.

The "project" for this harness is a checkout of the Devlens website. Every
mutation is staged in memory first (reads see the staged version), then
committed to disk in one step. Each commit is recorded as a transaction in
``<site>/.devlens-cli/session.json`` so it can be undone or redone.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

MAX_HISTORY = 30
STATE_DIR = ".devlens-cli"


class SessionError(RuntimeError):
    pass


def _locked_save_json(path, data, **dump_kwargs) -> None:
    """Write JSON with an exclusive lock. Truncate only after locking."""
    try:
        f = open(path, "r+", encoding="utf-8")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        f = open(path, "w", encoding="utf-8")
    with f:
        locked = False
        try:
            import fcntl

            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            locked = True
        except (ImportError, OSError):
            pass
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, **dump_kwargs)
            f.flush()
        finally:
            if locked:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _enc(b: bytes | None):
    return None if b is None else base64.b64encode(b).decode("ascii")


def _dec(s):
    return None if s is None else base64.b64decode(s)


def _digest(b: bytes | None):
    return None if b is None else hashlib.sha256(b).hexdigest()


class Session:
    """Staged changes on top of a site directory."""

    def __init__(self, root: str | os.PathLike):
        self.root = Path(root).resolve()
        self.state_path = self.root / STATE_DIR / "session.json"
        self._staged: dict[str, bytes | None] = {}  # relpath -> new bytes (None = delete)
        self._modified = False
        self.last_commit: dict | None = None

    # ---- staging -------------------------------------------------------
    def _rel(self, path) -> str:
        p = Path(path)
        if p.is_absolute():
            p = p.resolve().relative_to(self.root)
        rel = p.as_posix()
        if rel.startswith("../") or rel.startswith("/"):
            raise SessionError(f"Path escapes the site: {path}")
        return rel

    def read_bytes(self, path) -> bytes | None:
        rel = self._rel(path)
        if rel in self._staged:
            return self._staged[rel]
        full = self.root / rel
        return full.read_bytes() if full.is_file() else None

    def exists(self, path) -> bool:
        return self.read_bytes(path) is not None

    def write_bytes(self, path, data: bytes) -> None:
        self._staged[self._rel(path)] = data
        self._modified = True

    def delete(self, path) -> None:
        rel = self._rel(path)
        if self.read_bytes(rel) is None:
            raise SessionError(f"File does not exist: {rel}")
        self._staged[rel] = None
        self._modified = True

    def pending(self) -> list[dict]:
        out = []
        for rel, new in sorted(self._staged.items()):
            full = self.root / rel
            old_exists = full.is_file()
            if new is None:
                action = "delete"
            elif not old_exists:
                action = "create"
            elif full.read_bytes() == new:
                continue
            else:
                action = "modify"
            out.append({"path": rel, "action": action})
        return out

    def discard(self) -> None:
        self._staged.clear()
        self._modified = False

    # ---- commit / history ----------------------------------------------
    def _load_state(self) -> dict:
        if self.state_path.is_file():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {"version": 1, "undo": [], "redo": []}

    def _save_state(self, state: dict) -> None:
        _locked_save_json(self.state_path, state)
        gi = self.state_path.parent / ".gitignore"
        if not gi.exists():
            gi.write_text("*\n", encoding="utf-8")

    def _apply(self, files: list[dict], direction: str, force: bool) -> None:
        """Apply a transaction's files. direction='after' (redo) or 'before' (undo)."""
        expect_key = "after_sha" if direction == "before" else "before_sha"
        if not force:
            for f in files:
                full = self.root / f["path"]
                current = full.read_bytes() if full.is_file() else None
                if _digest(current) != f[expect_key]:
                    raise SessionError(
                        f"{f['path']} changed outside the CLI since this step; "
                        "use --force to overwrite it anyway"
                    )
        for f in files:
            full = self.root / f["path"]
            data = _dec(f[direction])
            if data is None:
                if full.is_file():
                    full.unlink()
            else:
                full.parent.mkdir(parents=True, exist_ok=True)
                tmp = full.with_name(f".{full.name}.devlens-tmp")
                tmp.write_bytes(data)
                os.replace(tmp, full)  # atomic; never edits a shared inode in place

    def commit(self, command: str) -> dict:
        changes = self.pending()
        if not changes:
            self.discard()
            self.last_commit = {"committed": False, "files": []}
            return self.last_commit
        files = []
        for c in changes:
            full = self.root / c["path"]
            before = full.read_bytes() if full.is_file() else None
            after = self._staged[c["path"]]
            files.append({
                "path": c["path"], "action": c["action"],
                "before": _enc(before), "after": _enc(after),
                "before_sha": _digest(before), "after_sha": _digest(after),
            })
        self._apply(files, "after", force=True)
        state = self._load_state()
        state["undo"].append({
            "command": command,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "files": files,
        })
        state["undo"] = state["undo"][-MAX_HISTORY:]
        state["redo"] = []
        self._save_state(state)
        self.discard()
        self.last_commit = {"committed": True, "files": changes}
        return self.last_commit

    def undo(self, force: bool = False) -> dict:
        if self._staged:
            raise SessionError("There are uncommitted changes")
        state = self._load_state()
        if not state["undo"]:
            raise SessionError("Nothing to undo")
        tx = state["undo"][-1]
        self._apply(tx["files"], "before", force)
        state["undo"].pop()
        state["redo"].append(tx)
        self._save_state(state)
        return {"undone": tx["command"], "files": [f["path"] for f in tx["files"]]}

    def redo(self, force: bool = False) -> dict:
        if self._staged:
            raise SessionError("There are uncommitted changes")
        state = self._load_state()
        if not state["redo"]:
            raise SessionError("Nothing to redo")
        tx = state["redo"][-1]
        self._apply(tx["files"], "after", force)
        state["redo"].pop()
        state["undo"].append(tx)
        self._save_state(state)
        return {"redone": tx["command"], "files": [f["path"] for f in tx["files"]]}

    def history(self) -> dict:
        state = self._load_state()
        strip = lambda tx: {
            "command": tx["command"], "time": tx["time"],
            "files": [{"path": f["path"], "action": f["action"]} for f in tx["files"]],
        }
        return {"undo": [strip(t) for t in state["undo"]], "redo": [strip(t) for t in state["redo"]]}
