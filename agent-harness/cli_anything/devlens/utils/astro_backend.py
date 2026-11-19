"""Backend: the site's real Astro build (the same one Cloudflare Pages runs)."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path


class BackendError(RuntimeError):
    pass


INSTALL_HINT = (
    "Install Node.js 20 or newer (https://nodejs.org) and then run 'npm ci' in the site folder."
)


def find_node() -> str:
    node = shutil.which("node")
    if not node:
        raise BackendError(f"Node.js was not found in PATH. {INSTALL_HINT}")
    return node


def find_astro(site_root: Path) -> Path:
    astro = site_root / "node_modules" / "astro" / "astro.js"
    if not astro.is_file():
        raise BackendError(f"Astro is not installed in {site_root}. Run 'npm ci' there. {INSTALL_HINT}")
    return astro


def version(site_root: Path) -> dict:
    node = find_node()
    astro = find_astro(site_root)
    nv = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    av = subprocess.run([node, str(astro), "--version"], capture_output=True, text=True,
                        cwd=site_root).stdout.strip().splitlines()
    return {"node": nv, "astro": av[-1].strip() if av else "unknown"}


def build(site_root: Path, out_dir: Path | None = None, timeout: int = 600) -> dict:
    """Run 'astro build' and return its log and timing."""
    node = find_node()
    astro = find_astro(site_root)
    cmd = [node, str(astro), "build"]
    if out_dir is not None:
        cmd += ["--outDir", str(out_dir)]
    env = {**os.environ, "ASTRO_TELEMETRY_DISABLED": "1", "NO_COLOR": "1"}
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=site_root, capture_output=True, text=True,
                          timeout=timeout, env=env)
    elapsed = round(time.time() - t0, 2)
    log = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        tail = "\n".join(log.strip().splitlines()[-25:])
        raise BackendError(f"astro build failed (exit {proc.returncode}):\n{tail}")
    return {"command": " ".join(cmd), "seconds": elapsed, "log": log}
