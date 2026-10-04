#!/usr/bin/env python3
"""Build versioned Ame-chan runtime packages and SHA-256 checksums."""

import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.4"
OUTPUT = ROOT.parent / f"ame-chan-release-{VERSION}"
TAG = f"v{VERSION}"
RUNTIME = ["canvastty.plugin.json", "index.html", "ame.js", "ame-frames.js"]
RUNTIME += [f"ame-{i}.webp" for i in range(6)]
DOCS = ["README.md", "README.ru.md", "README.zh-CN.md", "INSTALL.md", "LICENSE", "NOTICE.md", "SECURITY.md"]
PATCHES = {
    "windows-x64": ["frameless.css", "ame-chan-host.js", "frameless.ps1", "install-frameless.cmd", "uninstall-frameless.cmd"],
    "linux-x86_64": ["frameless.css", "ame-chan-host.js", "linux-transparent-card.py"],
    "mac-arm64": ["frameless.css", "ame-chan-host.js", "linux-transparent-card.py", "mac-transparent-card.py"],
}


def main():
    source = subprocess.check_output(["git", "archive", TAG], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(source)) as archive:
        files = {entry.name: archive.extractfile(entry).read() for entry in archive if entry.isfile()}
    manifest = json.loads(files["canvastty.plugin.json"])
    if manifest["version"] != VERSION:
        raise RuntimeError("Release tag has the wrong plugin version")
    commit = subprocess.check_output(["git", "rev-list", "-n", "1", TAG], cwd=ROOT, text=True).strip()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checksums = []
    for platform in ["plugin", *PATCHES]:
        package = {name: files[name] for name in RUNTIME + ["assets/preview.webp"]}
        # Runtime files are pinned to the released tag; installation and rights
        # documentation includes the maintainer's latest corrections.
        package.update({name: (ROOT / name).read_bytes() for name in DOCS})
        for name in PATCHES.get(platform, []):
            package[f"frameless/{name}"] = files[f"frameless/{name}"]
        package["RELEASE.txt"] = (
            f"Ame-chan for CanvasTTY {VERSION}\nRuntime commit: {commit}\n"
            f"Package: {platform}\n\n"
            "CanvasTTY installs from public GitHub repositories only.\n"
            "When public, install through Settings > Plugins > Inspect using:\n"
            "https://github.com/CLOSETTTY/canvastty-plugin-ame-chan\n\n"
            "CanvasTTY does not import these ZIP packages directly.\n"
            "Platform packages include the local transparent-card patch.\n"
            "Read README.md and INSTALL.md before applying it.\n"
            "Demo video is not included. Artwork provenance is in NOTICE.md.\n"
        ).encode("utf-8")
        destination = OUTPUT / f"Ame-chan-{VERSION}-{platform}.zip"
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as zipped:
            for name, contents in sorted(package.items()):
                zipped.writestr(name, contents)
        with zipfile.ZipFile(destination) as zipped:
            if zipped.testzip() or any(name.endswith(".mp4") for name in zipped.namelist()):
                raise RuntimeError(f"Invalid package: {destination}")
        checksum = hashlib.sha256(destination.read_bytes()).hexdigest()
        checksums.append(f"{checksum}  {destination.name}")
        print(f"{destination.name}: {destination.stat().st_size} bytes, {len(package)} files")
    (OUTPUT / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print(f"Packages and checksums: {OUTPUT}")


if __name__ == "__main__":
    main()
