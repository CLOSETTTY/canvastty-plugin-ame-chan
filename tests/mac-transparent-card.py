"""Verify that the macOS patch makes and signs an independent app bundle."""

import os
import plistlib
import runpy
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
fixture = runpy.run_path(str(ROOT / "tests/linux-transparent-card.py"))["fixture"]
patcher = runpy.run_path(str(ROOT / "frameless/mac-transparent-card.py"))


@unittest.skipUnless(sys.platform == "darwin", "Requires macOS codesign")
class MacTransparentCardTest(unittest.TestCase):
    def test_signed_copy_and_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / "home"
            home.mkdir()
            app = root / "CanvasTTY.app"
            contents = app / "Contents"
            executable = contents / "MacOS/CanvasTTY"
            executable.parent.mkdir(parents=True)
            shutil.copyfile("/usr/bin/true", executable)
            executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
            with (contents / "Info.plist").open("wb") as output:
                plistlib.dump({
                    "CFBundleName": "CanvasTTY",
                    "CFBundleIdentifier": "com.example.canvastty-test",
                    "CFBundleExecutable": "CanvasTTY",
                    "CFBundlePackageType": "APPL",
                    "CFBundleVersion": "1",
                    "CFBundleShortVersionString": "1.0",
                }, output)
            fixture(contents / "Resources")
            with mock.patch.dict(os.environ, {"HOME": str(home)}):
                patcher["apply"](app)
                copy = home / "Applications/CanvasTTY Ame-chan.app"
                self.assertTrue((app / "Contents/Resources/app.asar").is_file())
                self.assertTrue((copy / "Contents/Resources/app.asar.bak").is_file())
                subprocess.run(["codesign", "--verify", "--deep", "--strict", str(copy)], check=True)
                patcher["restore"]()
                self.assertFalse(copy.exists())
                self.assertTrue((home / "Applications/CanvasTTY Ame-chan.disabled.app").is_dir())


if __name__ == "__main__":
    unittest.main()
