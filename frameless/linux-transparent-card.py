#!/usr/bin/env python3
"""Apply Ame-chan's transparent CanvasTTY card styling on Linux.

The plugin iframe cannot style its CanvasTTY parent. This patches the local
host stylesheet while keeping the plugin card, resize handle, and controls.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


START = "/* ame-chan-claude-frameless:start */"
END = "/* ame-chan-claude-frameless:end */"
CSS = Path(__file__).with_name("frameless.css")
LAUNCHER_MARKER = "# ame-chan-canvastty-appimage-launcher"


def stylesheet(app):
    html = (app / "out/renderer/index.html").read_text(encoding="utf-8")
    match = re.search(r'href=["\']\./(assets/[^"\']+\.css)["\']', html)
    if not match:
        raise RuntimeError("CanvasTTY renderer stylesheet was not found")
    target = (app / "out/renderer" / match.group(1)).resolve()
    if not target.is_relative_to(app.resolve()) or not target.is_file():
        raise RuntimeError("CanvasTTY renderer stylesheet path is invalid")
    return target


def add_css(app, require_existing=False):
    target = stylesheet(app)
    original = target.read_text(encoding="utf-8")
    block = f"{START}\n{CSS.read_text(encoding='utf-8').rstrip()}\n{END}"
    if START in original or END in original:
        if original.count(START) != 1 or original.count(END) != 1:
            raise RuntimeError("CanvasTTY stylesheet has an incomplete Ame-chan patch")
        first, remainder = original.split(START, 1)
        _, last = remainder.split(END, 1)
        updated = first + block + last
    elif require_existing:
        raise RuntimeError("Existing CanvasTTY app was not patched by this script")
    else:
        updated = original + "\n" + block + "\n"
    target.write_text(updated, encoding="utf-8")


def unpack_asar(archive, destination):
    unpacked = Path(str(archive) + ".unpacked")
    with archive.open("rb") as source:
        first = source.read(16)
        if len(first) != 16:
            raise RuntimeError("CanvasTTY app.asar header is incomplete")
        _, header_size, _, json_size = struct.unpack("<4I", first)
        if header_size < 8 or json_size > header_size - 8 or header_size > 64 * 1024 * 1024:
            raise RuntimeError("CanvasTTY app.asar header is invalid")
        root = json.loads(source.read(json_size))
        data_start = 8 + header_size

        def walk(node, relative=Path()):
            for name, entry in node["files"].items():
                if name in ("", ".", "..") or "/" in name or "\\" in name:
                    raise RuntimeError("CanvasTTY app.asar contains an invalid path")
                member = relative / name
                target = destination / member
                if "files" in entry:
                    target.mkdir(parents=True, exist_ok=True)
                    walk(entry, member)
                elif entry.get("unpacked"):
                    original = unpacked / member
                    if not original.is_file():
                        # The archive also lists native builds for other platforms.
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original, target)
                elif "offset" in entry:
                    size = int(entry["size"])
                    offset = int(entry["offset"])
                    if size < 0 or offset < 0:
                        raise RuntimeError("CanvasTTY app.asar contains an invalid offset")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source.seek(data_start + offset)
                    with target.open("wb") as output:
                        remaining = size
                        while remaining:
                            chunk = source.read(min(remaining, 1024 * 1024))
                            if not chunk:
                                raise RuntimeError(f"CanvasTTY app.asar ended at {member}")
                            output.write(chunk)
                            remaining -= len(chunk)
                    if entry.get("executable"):
                        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                else:
                    raise RuntimeError(f"Unsupported CanvasTTY app.asar entry: {member}")

        walk(root)


def apply_resources(resources):
    archive = resources / "app.asar"
    backup = resources / "app.asar.bak"
    app = resources / "app"
    if not archive.exists() and backup.is_file() and app.is_dir():
        add_css(app, require_existing=True)
        print(f"Updated transparent Ame-chan card in {resources}")
        return
    if not archive.is_file() or backup.exists() or app.exists():
        raise RuntimeError("Expected app.asar and no existing app/backup; refusing to overwrite CanvasTTY files")
    stage = Path(tempfile.mkdtemp(prefix="ame-chan-app-", dir=resources))
    try:
        unpack_asar(archive, stage)
        add_css(stage)
        archive.rename(backup)
        try:
            stage.rename(app)
        except Exception:
            backup.rename(archive)
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(f"Transparent Ame-chan card applied in {resources}; restart CanvasTTY")


def restore_resources(resources):
    archive = resources / "app.asar"
    backup = resources / "app.asar.bak"
    app = resources / "app"
    if archive.exists() or not backup.is_file() or not app.is_dir():
        raise RuntimeError("No restorable Ame-chan CanvasTTY patch was found")
    if START not in stylesheet(app).read_text(encoding="utf-8"):
        raise RuntimeError("Existing CanvasTTY app was not patched by this script")
    disabled = resources / "app.ame-chan-disabled"
    if disabled.exists():
        raise RuntimeError(f"Refusing to overwrite {disabled}")
    app.rename(disabled)
    try:
        backup.rename(archive)
    except Exception:
        disabled.rename(app)
        raise
    print(f"Original CanvasTTY restored; patched app retained at {disabled}")


def find_resources():
    candidates = [Path("/opt/CanvasTTY/resources"), Path("/opt/canvastty/resources")]
    executable = shutil.which("canvastty")
    if executable:
        candidates.insert(0, Path(executable).resolve().parent / "resources")
    matches = [path for path in candidates if (path / "app.asar").is_file() or (path / "app.asar.bak").is_file()]
    if len(set(matches)) != 1:
        raise RuntimeError("CanvasTTY .deb installation not found uniquely; pass --resources /path/to/resources")
    return matches[0]


def apply_appimage(image):
    image = image.resolve()
    if not image.is_file():
        raise RuntimeError(f"AppImage not found: {image}")
    checksum = hashlib.sha256()
    with image.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(chunk)
    digest = checksum.hexdigest()[:12]
    base = Path.home() / ".local/share/canvastty-ame-chan"
    target = base / digest
    launcher = Path.home() / ".local/bin/canvastty-ame-chan"
    if launcher.exists() and LAUNCHER_MARKER not in launcher.read_text(encoding="utf-8"):
        raise RuntimeError(f"Refusing to overwrite existing launcher: {launcher}")
    base.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with tempfile.TemporaryDirectory(prefix="ame-chan-image-", dir=base) as temporary:
            subprocess.run([str(image), "--appimage-extract"], cwd=temporary, check=True)
            extracted = Path(temporary) / "squashfs-root"
            resources = extracted / "resources"
            if not (extracted / "AppRun").is_file() or not (resources / "app.asar").is_file():
                raise RuntimeError("Unrecognized CanvasTTY AppImage layout")
            apply_resources(resources)
            extracted.rename(target)
    else:
        resources = target / "resources"
        if not (resources / "app.asar.bak").is_file():
            raise RuntimeError(f"Existing extracted AppImage is not patched: {target}")
        apply_resources(resources)
    launcher.parent.mkdir(parents=True, exist_ok=True)
    import shlex
    launcher.write_text(f"#!/bin/sh\n{LAUNCHER_MARKER}\nexec {shlex.quote(str(target / 'AppRun'))} \"$@\"\n", encoding="utf-8")
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Launch transparent-card CanvasTTY with: {launcher}")


def restore_appimage():
    launcher = Path.home() / ".local/bin/canvastty-ame-chan"
    if not launcher.is_file() or LAUNCHER_MARKER not in launcher.read_text(encoding="utf-8"):
        raise RuntimeError("Ame-chan AppImage launcher was not found")
    launcher.unlink()
    print("Ame-chan AppImage launcher removed; run the original AppImage")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "restore"))
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--resources", type=Path, help="CanvasTTY installation resources directory")
    source.add_argument("--appimage", type=Path, help="CanvasTTY AppImage (apply only)")
    args = parser.parse_args()
    try:
        if args.appimage:
            if args.action == "apply":
                apply_appimage(args.appimage)
            else:
                restore_appimage()
        elif args.action == "restore" and not args.resources:
            try:
                resources = find_resources()
            except RuntimeError:
                restore_appimage()
            else:
                restore_resources(resources)
        else:
            resources = args.resources or find_resources()
            (apply_resources if args.action == "apply" else restore_resources)(resources.resolve())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
