"""Exercise the Linux CanvasTTY host patch without changing an installation."""

import importlib.util
import json
import os
import stat
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "frameless/linux-transparent-card.py"
spec = importlib.util.spec_from_file_location("linux_transparent_card", SCRIPT)
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


def fixture(resources):
    files = {
        "out/renderer/index.html": b'<link rel="stylesheet" href="./assets/main.css">',
        "out/renderer/assets/main.css": b".plugin-canvas-card{background:#222}",
    }
    root = {"files": {}}
    payload = b""
    for path, content in files.items():
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            node = node["files"].setdefault(part, {"files": {}})
        node["files"][parts[-1]] = {"size": len(content), "offset": str(len(payload))}
        payload += content
    header = json.dumps(root, separators=(",", ":")).encode()
    resources.mkdir(parents=True)
    (resources / "app.asar").write_bytes(
        struct.pack("<4I", 4, 8 + len(header), len(header), len(header)) + header + payload
    )


class LinuxTransparentCardTest(unittest.TestCase):
    def test_deb_apply_update_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            resources = Path(temporary) / "resources"
            fixture(resources)
            patcher.apply_resources(resources)
            css = patcher.stylesheet(resources / "app")
            self.assertTrue((resources / "app.asar.bak").is_file())
            self.assertEqual(css.read_text().count(patcher.START), 1)
            self.assertIn("ame-chan-claude", css.read_text())
            patcher.apply_resources(resources)
            self.assertEqual(css.read_text().count(patcher.START), 1)
            patcher.restore_resources(resources)
            self.assertTrue((resources / "app.asar").is_file())
            self.assertFalse((resources / "app").exists())

    @unittest.skipIf(os.name == "nt", "AppImage extraction runs on Linux")
    def test_appimage_launcher(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template = root / "template"
            fixture(template / "resources")
            (template / "AppRun").write_text("#!/bin/sh\nexit 0\n")
            image = root / "CanvasTTY.AppImage"
            image.write_text('#!/bin/sh\nmkdir -p squashfs-root\ncp -R "$FAKE_APPDIR"/. squashfs-root/\n')
            image.chmod(image.stat().st_mode | stat.S_IXUSR)
            home = root / "home"
            home.mkdir()
            with mock.patch.dict(os.environ, {"HOME": str(home), "FAKE_APPDIR": str(template)}):
                patcher.apply_appimage(image)
                launcher = home / ".local/bin/canvastty-ame-chan"
                self.assertTrue(launcher.is_file())
                self.assertIn(patcher.LAUNCHER_MARKER, launcher.read_text())
                self.assertEqual(len(list((home / ".local/share/canvastty-ame-chan").glob("*/resources/app.asar.bak"))), 1)
                patcher.restore_appimage()
                self.assertFalse(launcher.exists())


if __name__ == "__main__":
    unittest.main()
