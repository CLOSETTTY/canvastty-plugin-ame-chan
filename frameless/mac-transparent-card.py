#!/usr/bin/env python3
"""Create a separately signed macOS CanvasTTY copy with Ame-chan's transparent card."""

import argparse
import hashlib
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path


shared = runpy.run_path(str(Path(__file__).with_name("linux-transparent-card.py")))
apply_resources = shared["apply_resources"]
stylesheet = shared["stylesheet"]
START = shared["START"]


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def source_app(value):
    if value:
        return value.expanduser().resolve()
    candidates = [Path("/Applications/CanvasTTY.app"), Path.home() / "Applications/CanvasTTY.app"]
    matches = [candidate for candidate in candidates if (candidate / "Contents/Resources/app.asar").is_file()]
    if len(matches) != 1:
        raise RuntimeError("CanvasTTY.app not found uniquely; pass --app /path/to/CanvasTTY.app")
    return matches[0].resolve()


def sign_and_verify(app):
    subprocess.run(["codesign", "--force", "--sign", "-", str(app)], check=True)
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)


def apply(app):
    archive = app / "Contents/Resources/app.asar"
    if not archive.is_file():
        raise RuntimeError(f"CanvasTTY app.asar not found: {archive}")
    target = Path.home() / "Applications/CanvasTTY Ame-chan.app"
    if app == target.resolve():
        raise RuntimeError("Use the original CanvasTTY.app as --app, not the patched copy")
    resources = target / "Contents/Resources"
    if target.exists():
        backup = resources / "app.asar.bak"
        if not backup.is_file() or START not in stylesheet(resources / "app").read_text(encoding="utf-8"):
            raise RuntimeError(f"Refusing to overwrite an unrelated app: {target}")
        if checksum(archive) == checksum(backup):
            apply_resources(resources)
            sign_and_verify(target)
            print(f"Updated patched CanvasTTY: {target}")
            return
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ame-chan-mac-", dir=target.parent) as temporary:
        stage = Path(temporary) / "CanvasTTY Ame-chan.app"
        subprocess.run(["ditto", str(app), str(stage)], check=True)
        apply_resources(stage / "Contents/Resources")
        sign_and_verify(stage)
        if target.exists():
            old = target.with_name("CanvasTTY Ame-chan.previous.app")
            if old.exists():
                raise RuntimeError(f"Refusing to overwrite previous patched app: {old}")
            target.rename(old)
            try:
                stage.rename(target)
            except Exception:
                old.rename(target)
                raise
        else:
            stage.rename(target)
    print(f"Patched copy ready: {target}")
    print(f"Start it with: open '{target}'")


def restore():
    target = Path.home() / "Applications/CanvasTTY Ame-chan.app"
    if not target.is_dir():
        raise RuntimeError("Patched CanvasTTY copy was not found")
    if START not in stylesheet(target / "Contents/Resources/app").read_text(encoding="utf-8"):
        raise RuntimeError("Existing CanvasTTY copy was not patched by this script")
    disabled = target.with_name("CanvasTTY Ame-chan.disabled.app")
    if disabled.exists():
        raise RuntimeError(f"Refusing to overwrite {disabled}")
    target.rename(disabled)
    print(f"Patched copy disabled at {disabled}; open the original CanvasTTY.app")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "restore"))
    parser.add_argument("--app", type=Path, help="Path to the original CanvasTTY.app")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("This script must run on macOS")
    try:
        if args.action == "apply":
            apply(source_app(args.app))
        else:
            restore()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
