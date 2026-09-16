"""Snapshot and controller state live separately from the agent's writable workspace."""

import hashlib
import json
import os
from pathlib import Path
import subprocess

SKIP_DIRS = {".git", ".codex", ".agents", ".apex", "node_modules", ".venv", "venv",
             "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build", ".next", "target"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temp.replace(path)


def load_json(path):
    return json.loads(Path(path).read_text())


def contained(root, relative):
    root = Path(root).resolve()
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not relative:
        raise ValueError(f"Expected a relative path inside the workspace: {relative!r}")
    candidate = root / rel
    if any(p.is_symlink() for p in [candidate, *candidate.parents] if p != root and root in p.parents):
        raise ValueError(f"Symlink evidence is not accepted: {relative}")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path escapes workspace: {relative}")
    return resolved


def secret_name(name):
    return ((name.startswith(".env") and name not in {".env.example", ".env.sample", ".env.template"})
            or name.endswith((".pem", ".key", ".p12", ".pfx"))
            or name in {"id_rsa", "id_ed25519", ".npmrc", ".netrc"})


def snapshot(source, destination, max_files=20000, max_bytes=100_000_000):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if not source.is_dir():
        raise ValueError("Repository must be a local directory")
    if destination.is_relative_to(source):
        raise ValueError("Audit output must be outside the repository being audited")
    destination.mkdir(parents=True, exist_ok=False)
    git = subprocess.run(["git", "-C", str(source), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         capture_output=True)
    if git.returncode == 0:
        names = sorted(set(os.fsdecode(p) for p in git.stdout.split(b"\0") if p))
    else:
        names = []
        for base, dirs, files in os.walk(source, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(base) / d).is_symlink())
            names.extend(str((Path(base) / f).relative_to(source)) for f in sorted(files))
    hashes, excluded, total = {}, [], 0
    for name in names:
        rel = Path(name)
        if any(part in SKIP_DIRS for part in rel.parts) or secret_name(rel.name):
            excluded.append({"file": name, "reason": "excluded directory or credential filename"})
            continue
        try:
            original = contained(source, name)
        except ValueError:
            excluded.append({"file": name, "reason": "symlink or escaping path"})
            continue
        if not original.is_file():
            excluded.append({"file": name, "reason": "not a regular file"})
            continue
        if original.stat().st_size > 2_000_000:
            excluded.append({"file": name, "reason": "larger than 2 MB"})
            continue
        data = original.read_bytes()
        if len(hashes) >= max_files or total + len(data) > max_bytes:
            raise ValueError("Snapshot exceeds size limit; use a narrower repository directory")
        dest = destination / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(original.stat().st_mode & 0o777)
        hashes[name] = digest(data)
        total += len(data)
    if not hashes:
        raise ValueError("No auditable files were copied")
    commit = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True)
    return {"files": hashes, "excluded": excluded, "bytes": total,
            "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "content_sha256": digest(json.dumps(hashes, sort_keys=True).encode())}


def snapshot_unchanged(root, manifest):
    root = Path(root)
    actual = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".pytest_cache"}]
        if any((Path(base) / d).is_symlink() for d in dirs):
            return False
        for name in files:
            p = Path(base) / name
            if p.is_symlink():
                return False
            actual[str(p.relative_to(root))] = digest(p.read_bytes())
    return actual == manifest["files"]
